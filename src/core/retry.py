"""
Module de retry automatique pour la synchronisation N2F.

Ce module fournit un système de retry intelligent qui :
- Gère les erreurs temporaires avec backoff exponentiel
- Distingue les erreurs récupérables des erreurs fatales
- Fournit des métriques de retry détaillées
- Intègre avec le système de métriques existant
"""

import time
import random
from typing import Callable, Any, Optional, List, Dict, Type, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

from core.exceptions import SyncException


class RetryableError(Exception):
    """Exception de base pour les erreurs récupérables."""

    pass


class FatalError(Exception):
    """Exception de base pour les erreurs fatales (non récupérables)."""

    pass


class RetryStrategy(Enum):
    """Stratégies de retry disponibles."""

    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    CONSTANT_DELAY = "constant_delay"
    FIBONACCI_BACKOFF = "fibonacci_backoff"


@dataclass
class RetryMetrics:
    """Métriques de retry pour une opération."""

    total_attempts: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0
    total_delay_seconds: float = 0.0
    last_error: Optional[str] = None
    last_error_type: Optional[str] = None
    retry_reasons: List[str] = field(default_factory=list)
    delays_used: List[float] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calcule le taux de succès."""
        return (
            self.successful_attempts / self.total_attempts
            if self.total_attempts > 0
            else 0
        )

    @property
    def average_delay(self) -> float:
        """Calcule le délai moyen."""
        return sum(self.delays_used) / len(self.delays_used) if self.delays_used else 0

    def to_dict(self) -> Dict[str, Any]:
        """Convertit les métriques en dictionnaire."""
        return {
            "total_attempts": self.total_attempts,
            "successful_attempts": self.successful_attempts,
            "failed_attempts": self.failed_attempts,
            "success_rate": self.success_rate,
            "total_delay_seconds": self.total_delay_seconds,
            "average_delay": self.average_delay,
            "last_error": self.last_error,
            "last_error_type": self.last_error_type,
            "retry_reasons": self.retry_reasons,
            "delays_used": self.delays_used,
        }


@dataclass
class RetryConfig:
    """Configuration pour les retry automatiques."""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    jitter_factor: float = 0.1
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    retryable_exceptions: List[Type[Exception]] = field(
        default_factory=lambda: [ConnectionError, TimeoutError, OSError, RetryableError]
    )
    fatal_exceptions: List[Type[Exception]] = field(
        default_factory=lambda: [FatalError, ValueError, TypeError]
    )
    log_retries: bool = True
    log_level: int = logging.INFO

    def is_retryable(self, exception: Exception) -> bool:
        """Détermine si une exception est récupérable."""
        exception_type = type(exception)

        # Vérifier les exceptions fatales en premier
        for fatal_exc in self.fatal_exceptions:
            if issubclass(exception_type, fatal_exc):
                return False

        # Vérifier les exceptions récupérables
        for retryable_exc in self.retryable_exceptions:
            if issubclass(exception_type, retryable_exc):
                return True

        return False


class RetryManager:
    """
    Gestionnaire de retry intelligent.

    Fournit des fonctionnalités avancées de retry avec :
    - Stratégies de backoff configurables
    - Distinction entre erreurs récupérables et fatales
    - Métriques détaillées
    - Logging intelligent
    """

    def __init__(self, config: Optional[RetryConfig] = None) -> None:
        """
        Initialise le gestionnaire de retry.

        Args:
            config: Configuration du retry (utilise les valeurs par défaut si None)
        """
        self.config = config or RetryConfig()
        self.logger = logging.getLogger(__name__)
        self.metrics: Dict[str, RetryMetrics] = {}

    def execute(
        self,
        func: Callable[..., Any],
        *args: Any,
        operation_name: str = "unknown",
        **kwargs: Any,
    ) -> Any:
        """
        Exécute une fonction avec retry automatique.

        Args:
            func: Fonction à exécuter
            *args: Arguments positionnels
            operation_name: Nom de l'opération pour les métriques
            **kwargs: Arguments nommés

        Returns:
            Résultat de la fonction

        Raises:
            Exception: Dernière exception si toutes les tentatives échouent
        """
        if operation_name not in self.metrics:
            self.metrics[operation_name] = RetryMetrics()

        metrics = self.metrics[operation_name]
        last_exception: Optional[Exception] = None

        for attempt in range(1, self.config.max_attempts + 1):
            try:
                metrics.total_attempts += 1

                if self.config.log_retries and attempt > 1:
                    self.logger.log(
                        self.config.log_level,
                        f"Tentative {attempt}/{self.config.max_attempts} pour "
                        f"{operation_name}",
                    )

                result = func(*args, **kwargs)
                metrics.successful_attempts += 1

                if attempt > 1:
                    self.logger.info(
                        f"Succès à la tentative {attempt} pour {operation_name}"
                    )

                return result

            except Exception as e:  # noqa: B001
                metrics.failed_attempts += 1
                metrics.last_error = str(e)
                metrics.last_error_type = type(e).__name__
                last_exception = e

                # Vérifier si l'erreur est récupérable
                if not self.config.is_retryable(e):
                    self.logger.error(f"Erreur fatale pour {operation_name}: {e}")
                    raise e

                # Dernière tentative échouée
                if attempt == self.config.max_attempts:
                    self.logger.error(
                        f"Échec définitif après {self.config.max_attempts} tentatives "
                        f"pour {operation_name}: {e}"
                    )
                    break

                # Calculer le délai de retry
                delay = self._calculate_delay(attempt)
                metrics.total_delay_seconds += delay
                metrics.delays_used.append(delay)
                metrics.retry_reasons.append(f"Tentative {attempt}: {type(e).__name__}")

                if self.config.log_retries:
                    self.logger.warning(
                        f"Tentative {attempt} échouée pour {operation_name}: {e}. "
                        f"Réessai dans {delay:.2f}s..."
                    )

                time.sleep(delay)

        # Toutes les tentatives ont échoué
        if last_exception is not None:
            raise last_exception
        else:
            # This case should theoretically not be reached
            raise SyncException(
                "Unexpected error in RetryManager: no exception was captured "
                "after all attempts.",
                context={"operation_name": operation_name},
            )

    def _calculate_delay(self, attempt: int) -> float:
        """
        Calcule le délai de retry selon la stratégie configurée.

        Args:
            attempt: Numéro de la tentative (1 - based)

        Returns:
            Délai en secondes
        """
        if self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.config.base_delay * attempt
        elif self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.config.base_delay * (2 ** (attempt - 1))
        elif self.config.strategy == RetryStrategy.CONSTANT_DELAY:
            delay = self.config.base_delay
        elif self.config.strategy == RetryStrategy.FIBONACCI_BACKOFF:
            delay = self.config.base_delay * self._fibonacci(attempt)
        else:
            delay = self.config.base_delay

        # Limiter le délai maximum
        delay = min(delay, self.config.max_delay)

        # Ajouter du jitter si activé
        if self.config.jitter:
            jitter = delay * self.config.jitter_factor * random.uniform(-1, 1)
            delay = max(0.1, delay + jitter)  # Minimum 0.1 seconde

        return delay

    def _fibonacci(self, n: int) -> int:
        """Calcule le n - ième nombre de Fibonacci."""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

    def get_metrics(
        self,
        operation_name: Optional[str] = None,
    ) -> Union[RetryMetrics, Dict[str, RetryMetrics]]:
        """
        Récupère les métriques de retry.

        Args:
            operation_name: Nom de l'opération (None pour toutes les opérations)

        Returns:
            Métriques de retry
        """
        if operation_name:
            return self.metrics.get(operation_name, RetryMetrics())
        return self.metrics.copy()

    def reset_metrics(self, operation_name: Optional[str] = None) -> None:
        """
        Réinitialise les métriques de retry.

        Args:
            operation_name: Nom de l'opération (None pour toutes les opérations)
        """
        if operation_name:
            if operation_name in self.metrics:
                self.metrics[operation_name] = RetryMetrics()
        else:
            self.metrics.clear()

    def print_summary(self) -> None:
        """Affiche un résumé des métriques de retry."""
        if not self.metrics:
            logging.info("Aucune métrique de retry disponible.")
            return

        logging.info("\n" + "=" * 60)
        logging.info("RÉSUMÉ DES MÉTRIQUES DE RETRY")
        logging.info("=" * 60)

        total_attempts = sum(m.total_attempts for m in self.metrics.values())
        total_successful = sum(m.successful_attempts for m in self.metrics.values())
        total_failed = sum(m.failed_attempts for m in self.metrics.values())

        logging.info(f"Tentatives totales: {total_attempts}")
        logging.info(f"Succès: {total_successful}")
        logging.info(f"Échecs: {total_failed}")
        logging.info(
            f"Taux de succès: {(total_successful / total_attempts * 100):.1f}%"
            if total_attempts > 0
            else "N / A"
        )

        logging.info("\nDétail par opération:")
        for op_name, metrics in self.metrics.items():
            success_rate = (
                (metrics.successful_attempts / metrics.total_attempts * 100)
                if metrics.total_attempts > 0
                else 0
            )
            logging.info(
                f"- {op_name}: {metrics.successful_attempts}/{metrics.total_attempts} "
                f"({success_rate:.1f}%)"
            )

        logging.info("=" * 60)


# Instance globale du gestionnaire de retry
_retry_manager: Optional[RetryManager] = None


def get_retry_manager(config: Optional[RetryConfig] = None) -> RetryManager:
    """
    Récupère l'instance globale du gestionnaire de retry.

    Args:
        config: Configuration optionnelle pour l'initialisation

    Returns:
        Instance du RetryManager
    """
    global _retry_manager
    if _retry_manager is None:
        _retry_manager = RetryManager(config)
    return _retry_manager


def print_retry_summary() -> None:
    """Affiche le résumé des métriques de retry."""
    manager = get_retry_manager()
    manager.print_summary()


def retry(
    config: Optional[RetryConfig] = None, operation_name: Optional[str] = None
) -> Callable:
    """Décorateur pour appliquer une logique de retry à une fonction."""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            op_name = operation_name or func.__name__
            manager = get_retry_manager(config)
            return manager.execute(func, *args, operation_name=op_name, **kwargs)

        return wrapper

    return decorator


def api_retry(
    max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 30.0
) -> Callable:
    """Décorateur de retry optimisé pour les appels API."""
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        retryable_exceptions=[ConnectionError, TimeoutError, RetryableError],
    )
    return retry(config)


def database_retry(
    max_attempts: int = 2, base_delay: float = 0.5, max_delay: float = 5.0
) -> Callable:
    """Décorateur de retry optimisé pour les opérations de base de données."""
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        strategy=RetryStrategy.LINEAR_BACKOFF,
        retryable_exceptions=[ConnectionError, TimeoutError, RetryableError],
    )
    return retry(config)


def execute_with_retry(
    func: Callable, *args: Any, config: Optional[RetryConfig] = None, **kwargs: Any
) -> Any:
    """Exécute une fonction avec une logique de retry."""
    operation_name = kwargs.pop("operation_name", func.__name__)
    manager = get_retry_manager(config)
    return manager.execute(func, *args, operation_name=operation_name, **kwargs)


def get_retry_metrics(
    operation_name: Optional[str] = None,
) -> Union[RetryMetrics, Dict[str, RetryMetrics]]:
    """Récupère les métriques de retry."""
    manager = get_retry_manager()
    return manager.get_metrics(operation_name)


def reset_retry_metrics(operation_name: Optional[str] = None) -> None:
    """Réinitialise les métriques de retry."""
    manager = get_retry_manager()
    manager.reset_metrics(operation_name)
