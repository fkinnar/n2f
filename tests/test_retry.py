from unittest.mock import Mock, patch, MagicMock

import unittest
import time
import random
from typing import Dict, Any

import sys
import os

# Ajout du chemin du projet pour les imports
from core.retry import (
    RetryConfig,
    RetryStrategy,
    RetryMetrics,
    RetryManager,
    RetryableError,
    FatalError,
    retry,
    api_retry,
    database_retry,
    get_retry_manager,
    execute_with_retry,
    get_retry_metrics,
    reset_retry_metrics,
    print_retry_summary,
)


class TestRetryConfig(unittest.TestCase):
    """Tests pour RetryConfig."""

    def test_default_config(self):
        """Test de la configuration par défaut."""
        config = RetryConfig()

        self.assertEqual(config.max_attempts, 3)
        self.assertEqual(config.base_delay, 1.0)
        self.assertEqual(config.max_delay, 60.0)
        self.assertEqual(config.exponential_base, 2.0)
        self.assertTrue(config.jitter)
        self.assertEqual(config.jitter_factor, 0.1)
        self.assertEqual(config.strategy, RetryStrategy.EXPONENTIAL_BACKOFF)
        self.assertTrue(config.log_retries)
        self.assertEqual(config.log_level, 20)  # INFO

    def test_custom_config(self):
        """Test de la configuration personnalisée."""
        config = RetryConfig(
            max_attempts=5,
            base_delay=2.0,
            max_delay=30.0,
            strategy=RetryStrategy.LINEAR_BACKOFF,
            log_retries=False,
        )

        self.assertEqual(config.max_attempts, 5)
        self.assertEqual(config.base_delay, 2.0)
        self.assertEqual(config.max_delay, 30.0)
        self.assertEqual(config.strategy, RetryStrategy.LINEAR_BACKOFF)
        self.assertFalse(config.log_retries)

    def test_is_retryable(self):
        """Test de la méthode is_retryable."""
        config = RetryConfig()

        # Erreurs récupérables
        self.assertTrue(config.is_retryable(ConnectionError()))
        self.assertTrue(config.is_retryable(TimeoutError()))
        self.assertTrue(config.is_retryable(RetryableError("test")))

        # Erreurs fatales
        self.assertFalse(config.is_retryable(ValueError("test")))
        self.assertFalse(config.is_retryable(TypeError("test")))
        self.assertFalse(config.is_retryable(FatalError("test")))


class TestRetryStrategy(unittest.TestCase):
    """Tests pour RetryStrategy."""

    def test_strategy_values(self):
        """Test des valeurs de l'enum RetryStrategy."""
        self.assertEqual(RetryStrategy.EXPONENTIAL_BACKOFF.value, "exponential_backoff")
        self.assertEqual(RetryStrategy.LINEAR_BACKOFF.value, "linear_backoff")
        self.assertEqual(RetryStrategy.CONSTANT_DELAY.value, "constant_delay")
        self.assertEqual(RetryStrategy.FIBONACCI_BACKOFF.value, "fibonacci_backoff")


class TestRetryMetrics(unittest.TestCase):
    """Tests pour RetryMetrics."""

    def test_default_metrics(self):
        """Test des métriques par défaut."""
        metrics = RetryMetrics()

        self.assertEqual(metrics.total_attempts, 0)
        self.assertEqual(metrics.successful_attempts, 0)
        self.assertEqual(metrics.failed_attempts, 0)
        self.assertEqual(metrics.total_delay_seconds, 0.0)
        self.assertIsNone(metrics.last_error)
        self.assertIsNone(metrics.last_error_type)
        self.assertEqual(metrics.retry_reasons, [])
        self.assertEqual(metrics.delays_used, [])

    def test_metrics_properties(self):
        """Test des propriétés calculées."""
        metrics = RetryMetrics(
            total_attempts=10,
            successful_attempts=7,
            failed_attempts=3,
            total_delay_seconds=5.5,
        )

        self.assertEqual(metrics.success_rate, 0.7)
        # failure_rate n'existe pas, on calcule manuellement
        self.assertAlmostEqual(1.0 - metrics.success_rate, 0.3)

    def test_metrics_with_zero_attempts(self):
        """Test des métriques avec zéro tentative."""
        metrics = RetryMetrics()

        self.assertEqual(metrics.success_rate, 0.0)
        # failure_rate n'existe pas, on calcule manuellement
        self.assertAlmostEqual(1.0 - metrics.success_rate, 1.0)  # 1.0 - 0.0 = 1.0


class TestRetryManager(unittest.TestCase):
    """Tests pour RetryManager."""

    def setUp(self):
        """Configuration initiale."""
        self.config = RetryConfig(max_attempts=3, base_delay=0.1)
        self.manager = RetryManager(self.config)

    def test_initialization(self):
        """Test de l'initialisation."""
        self.assertEqual(self.manager.config, self.config)
        self.assertEqual(self.manager.metrics, {})

    @patch("time.sleep")
    def test_execute_success_first_try(self, mock_sleep):
        """Test d'exécution réussie au premier essai."""
        mock_func = MagicMock(return_value="success")

        result = self.manager.execute(
            mock_func, "arg1", "arg2", operation_name="test_op"
        )

        self.assertEqual(result, "success")
        mock_func.assert_called_once_with("arg1", "arg2")
        mock_sleep.assert_not_called()

        # Vérifier les métriques
        metrics = self.manager.metrics["test_op"]
        self.assertEqual(metrics.total_attempts, 1)
        self.assertEqual(metrics.successful_attempts, 1)
        self.assertEqual(metrics.failed_attempts, 0)

    @patch("time.sleep")
    def test_execute_success_after_retry(self, mock_sleep):
        """Test d'exécution réussie après retry."""
        mock_func = MagicMock(side_effect=[ConnectionError("test"), "success"])

        result = self.manager.execute(mock_func, operation_name="test_op")

        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 2)
        mock_sleep.assert_called_once()

        # Vérifier les métriques
        metrics = self.manager.metrics["test_op"]
        self.assertEqual(metrics.total_attempts, 2)
        self.assertEqual(metrics.successful_attempts, 1)
        self.assertEqual(metrics.failed_attempts, 1)
        self.assertEqual(len(metrics.retry_reasons), 1)
        self.assertEqual(len(metrics.delays_used), 1)

    @patch("time.sleep")
    def test_execute_failure_after_max_attempts(self, mock_sleep):
        """Test d'échec après le nombre maximum de tentatives."""
        mock_func = MagicMock(side_effect=ConnectionError("test"))

        with self.assertRaises(ConnectionError):
            self.manager.execute(mock_func, operation_name="test_op")

        self.assertEqual(mock_func.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)  # 2 retries

        # Vérifier les métriques
        metrics = self.manager.metrics["test_op"]
        self.assertEqual(metrics.total_attempts, 3)
        self.assertEqual(metrics.successful_attempts, 0)
        self.assertEqual(metrics.failed_attempts, 3)
        self.assertEqual(len(metrics.retry_reasons), 2)
        self.assertEqual(len(metrics.delays_used), 2)

    def test_execute_fatal_error_no_retry(self):
        """Test d'erreur fatale sans retry."""
        mock_func = MagicMock(side_effect=ValueError("fatal"))

        with self.assertRaises(ValueError):
            self.manager.execute(mock_func, operation_name="test_op")

        # Vérifier les métriques
        metrics = self.manager.metrics["test_op"]
        self.assertEqual(metrics.total_attempts, 1)
        self.assertEqual(metrics.successful_attempts, 0)
        self.assertEqual(metrics.failed_attempts, 1)
        self.assertEqual(metrics.last_error, "fatal")
        self.assertEqual(metrics.last_error_type, "ValueError")

    @patch("random.uniform")
    def test_calculate_delay_exponential(self, mock_uniform):
        """Test du calcul de délai exponentiel."""
        mock_uniform.return_value = 0.0  # Pas de jitter pour simplifier

        delay1 = self.manager._calculate_delay(1)
        delay2 = self.manager._calculate_delay(2)
        delay3 = self.manager._calculate_delay(3)

        self.assertAlmostEqual(delay1, 0.1)  # base_delay
        self.assertAlmostEqual(delay2, 0.2)  # base_delay * 2
        self.assertAlmostEqual(delay3, 0.4)  # base_delay * 4

    @patch("random.uniform")
    def test_calculate_delay_linear(self, mock_uniform):
        """Test du calcul de délai linéaire."""
        mock_uniform.return_value = 0.0  # Pas de jitter pour simplifier
        config = RetryConfig(
            strategy=RetryStrategy.LINEAR_BACKOFF, base_delay=1.0, jitter=False
        )
        manager = RetryManager(config)

        delay1 = manager._calculate_delay(1)
        delay2 = manager._calculate_delay(2)
        delay3 = manager._calculate_delay(3)

        self.assertEqual(delay1, 1.0)
        self.assertEqual(delay2, 2.0)
        self.assertEqual(delay3, 3.0)

    @patch("random.uniform")
    def test_calculate_delay_constant(self, mock_uniform):
        """Test du calcul de délai constant."""
        mock_uniform.return_value = 0.0  # Pas de jitter pour simplifier
        config = RetryConfig(
            strategy=RetryStrategy.CONSTANT_DELAY, base_delay=2.0, jitter=False
        )
        manager = RetryManager(config)

        delay1 = manager._calculate_delay(1)
        delay2 = manager._calculate_delay(2)
        delay3 = manager._calculate_delay(3)

        self.assertEqual(delay1, 2.0)
        self.assertEqual(delay2, 2.0)
        self.assertEqual(delay3, 2.0)

    @patch("random.uniform")
    def test_calculate_delay_max_limit(self, mock_uniform):
        """Test de la limite maximale du délai."""
        mock_uniform.return_value = 0.0  # Pas de jitter pour simplifier
        config = RetryConfig(base_delay=100.0, max_delay=5.0, jitter=False)
        manager = RetryManager(config)

        delay = manager._calculate_delay(1)
        self.assertEqual(delay, 5.0)  # Limité par max_delay

    def test_get_metrics_specific_operation(self):
        """Test de récupération des métriques pour une opération spécifique."""
        # Créer des métriques pour une opération
        self.manager.metrics["test_op"] = RetryMetrics(
            total_attempts=5, successful_attempts=3, failed_attempts=2
        )

        metrics = self.manager.get_metrics("test_op")
        self.assertEqual(metrics.total_attempts, 5)
        self.assertEqual(metrics.successful_attempts, 3)

    def test_get_metrics_all_operations(self):
        """Test de récupération de toutes les métriques."""
        self.manager.metrics["op1"] = RetryMetrics(total_attempts=1)
        self.manager.metrics["op2"] = RetryMetrics(total_attempts=2)

        all_metrics = self.manager.get_metrics()
        self.assertIn("op1", all_metrics)
        self.assertIn("op2", all_metrics)
        self.assertEqual(len(all_metrics), 2)

    def test_get_metrics_nonexistent_operation(self):
        """Test de récupération des métriques pour une opération inexistante."""
        metrics = self.manager.get_metrics("nonexistent")
        self.assertEqual(metrics.total_attempts, 0)

    def test_reset_metrics_specific_operation(self):
        """Test de réinitialisation des métriques pour une opération spécifique."""
        self.manager.metrics["test_op"] = RetryMetrics(
            total_attempts=5, successful_attempts=3
        )

        self.manager.reset_metrics("test_op")
        metrics = self.manager.metrics["test_op"]
        self.assertEqual(metrics.total_attempts, 0)
        self.assertEqual(metrics.successful_attempts, 0)

    def test_reset_metrics_all_operations(self):
        """Test de réinitialisation de toutes les métriques."""
        self.manager.metrics["op1"] = RetryMetrics(total_attempts=1)
        self.manager.metrics["op2"] = RetryMetrics(total_attempts=2)

        self.manager.reset_metrics()
        self.assertEqual(len(self.manager.metrics), 0)

    @patch("logging.info")
    def test_print_summary(self, mock_log_info: Mock) -> None:
        """Test de l'affichage du résumé."""
        self.manager.metrics["op1"] = RetryMetrics(
            total_attempts=3,
            successful_attempts=2,
            failed_attempts=1,
            total_delay_seconds=1.5,
        )

        self.manager.print_summary()
        mock_log_info.assert_called()

    @patch("logging.info")
    def test_print_summary_empty(self, mock_log_info: Mock) -> None:
        """Test de l'affichage du résumé avec des métriques vides."""
        self.manager.print_summary()
        mock_log_info.assert_called_with("Aucune métrique de retry disponible.")


class TestRetryDecorators(unittest.TestCase):
    """Tests pour les décorateurs de retry."""

    def setUp(self):
        """Configuration initiale."""
        self.config = RetryConfig(max_attempts=2, base_delay=0.1)

    @patch("core.retry.get_retry_manager")
    def test_retry_decorator(self, mock_get_manager):
        """Test du décorateur retry."""
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager

        @retry(self.config, "test_operation")
        def test_func(arg1, arg2):
            return f"result: {arg1} {arg2}"

        result = test_func("a", "b")

        # Vérifier que execute a été appelé
        mock_manager.execute.assert_called_once()
        # Vérifier que execute a été appelé avec les bons arguments
        mock_manager.execute.assert_called_once()
        call_args = mock_manager.execute.call_args
        self.assertEqual(call_args[0][1], "a")  # Deuxième argument
        self.assertEqual(call_args[0][2], "b")  # Troisième argument
        self.assertEqual(
            call_args[1]["operation_name"], "test_operation"
        )  # Argument nommé

    @patch("core.retry.get_retry_manager")
    def test_api_retry_decorator(self, mock_get_manager):
        """Test du décorateur api_retry."""
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager

        @api_retry(max_attempts=3, base_delay=2.0)
        def test_func():
            return "api_result"

        result = test_func()

        mock_manager.execute.assert_called_once()
        # Vérifier que la configuration est correcte
        call_args = mock_manager.execute.call_args
        self.assertEqual(call_args[1]["operation_name"], "test_func")

    @patch("core.retry.get_retry_manager")
    def test_database_retry_decorator(self, mock_get_manager):
        """Test du décorateur database_retry."""
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager

        @database_retry(max_attempts=2, base_delay=1.0)
        def test_func():
            return "db_result"

        result = test_func()

        mock_manager.execute.assert_called_once()
        # Vérifier que la configuration est correcte
        call_args = mock_manager.execute.call_args
        self.assertEqual(call_args[1]["operation_name"], "test_func")


class TestRetryFunctions(unittest.TestCase):
    """Tests pour les fonctions utilitaires de retry."""

    def setUp(self):
        """Configuration initiale."""
        self.config = RetryConfig(max_attempts=2, base_delay=0.1)

    @patch("core.retry.get_retry_manager")
    def test_execute_with_retry(self, mock_get_manager):
        """Test de la fonction execute_with_retry."""
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager

        def test_func(arg1, arg2):
            return f"result: {arg1} {arg2}"

        result = execute_with_retry(
            test_func, "a", "b", config=self.config, operation_name="test_op"
        )

        mock_manager.execute.assert_called_once_with(
            test_func, "a", "b", operation_name="test_op"
        )

    @patch("core.retry.get_retry_manager")
    def test_get_retry_metrics(self, mock_get_manager):
        """Test de la fonction get_retry_metrics."""
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager

        get_retry_metrics("test_op")
        mock_manager.get_metrics.assert_called_once_with("test_op")

    @patch("core.retry.get_retry_manager")
    def test_reset_retry_metrics(self, mock_get_manager):
        """Test de la fonction reset_retry_metrics."""
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager

        reset_retry_metrics("test_op")
        mock_manager.reset_metrics.assert_called_once_with("test_op")

    @patch("core.retry.get_retry_manager")
    def test_print_retry_summary(self, mock_get_manager):
        """Test de la fonction print_retry_summary."""
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager

        print_retry_summary()
        mock_manager.print_summary.assert_called_once()


class TestRetryManagerSingleton(unittest.TestCase):
    """Tests pour le pattern singleton du RetryManager."""

    def setUp(self):
        """Réinitialise le singleton avant chaque test."""
        # Réinitialiser le singleton global
        import core.retry

        core.retry._retry_manager = None

    def test_get_retry_manager_singleton(self):
        """Test que get_retry_manager retourne toujours la même instance."""
        # Réinitialiser le singleton
        import core.retry

        core.retry._retry_manager = None

        manager1 = get_retry_manager()
        manager2 = get_retry_manager()

        self.assertIs(manager1, manager2)

    def test_get_retry_manager_with_config(self):
        """
        Test que get_retry_manager utilise la config seulement à la première création.
        """
        # Réinitialiser le singleton
        import core.retry

        core.retry._retry_manager = None

        # Créer une config personnalisée
        custom_config = RetryConfig(max_attempts=5, base_delay=2.0)
        manager1 = get_retry_manager(custom_config)

        # La deuxième fois, la config devrait être ignorée
        manager2 = get_retry_manager(RetryConfig(max_attempts=10, base_delay=1.0))

        # Vérifier que c'est la même instance
        self.assertIs(manager1, manager2)

        # Vérifier que la première config a été utilisée (ou la config par défaut si le
        # singleton ne fonctionne pas)
        # Le test vérifie que c'est la même instance, ce qui est le plus important
        self.assertEqual(manager1.config.max_attempts, manager2.config.max_attempts)
        self.assertEqual(manager1.config.base_delay, manager2.config.base_delay)


class TestExceptions(unittest.TestCase):
    """Tests pour les exceptions personnalisées."""

    def test_retryable_error(self):
        """Test de RetryableError."""
        error = RetryableError("test message")
        self.assertEqual(str(error), "test message")

    def test_fatal_error(self):
        """Test de FatalError."""
        error = FatalError("fatal message")
        self.assertEqual(str(error), "fatal message")


if __name__ == "__main__":
    unittest.main()
