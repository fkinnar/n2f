"""
Exemple d'utilisation du système de retry N2F.

Ce module démontre comment utiliser le système de retry pour :
- Gérer les erreurs temporaires avec différentes stratégies
- Utiliser les décorateurs spécialisés pour API et DB
- Analyser les métriques de retry
- Intégrer avec le système de métriques existant
"""

import time
import random
from ..retry import (
    RetryConfig,
    RetryStrategy,
    RetryableError,
    FatalError,
    retry,
    api_retry,
    database_retry,
    execute_with_retry,
    get_retry_metrics,
    print_retry_summary,
    reset_retry_metrics,
)


def simulate_api_call(success_rate: float = 0.3, operation_name: str = "api_call"):
    """Simule un appel API avec un taux de succès configurable."""
    print(f"🔄 Tentative d'appel API: {operation_name}")

    if random.random() < success_rate:
        print(f"✅ Succès: {operation_name}")
        return {"status": "success", "data": "sample_data"}
    else:
        error_type = random.choice(
            [
                ConnectionError("Connexion perdue"),
                TimeoutError("Timeout de la requête"),
                RetryableError("Erreur temporaire du serveur"),
            ]
        )
        print(f"❌ Échec: {operation_name} - {error_type}")
        raise error_type


def simulate_database_operation(
    success_rate: float = 0.5, operation_name: str = "db_operation"
):
    """Simule une opération de base de données."""
    print(f"🔄 Tentative d'opération DB: {operation_name}")

    if random.random() < success_rate:
        print(f"✅ Succès: {operation_name}")
        return {"status": "success", "rows_affected": random.randint(1, 100)}
    else:
        error_type = random.choice(
            [
                ConnectionError("Connexion DB perdue"),
                TimeoutError("Timeout de la requête DB"),
                RetryableError("Verrouillage temporaire"),
            ]
        )
        print(f"❌ Échec: {operation_name} - {error_type}")
        raise error_type


def simulate_fatal_error():
    """Simule une erreur fatale (non récupérable)."""
    print("🔄 Tentative d'opération avec erreur fatale")
    raise FatalError("Erreur fatale - données invalides")


@api_retry(max_attempts=3, base_delay=1.0, max_delay=10.0)
def api_function_with_retry():
    """Fonction API avec retry automatique via décorateur."""
    return simulate_api_call(0.2, "api_function_with_retry")


@database_retry(max_attempts=2, base_delay=0.5, max_delay=5.0)
def db_function_with_retry():
    """Fonction DB avec retry automatique via décorateur."""
    return simulate_database_operation(0.3, "db_function_with_retry")


def example_basic_retry():
    """Exemple d'utilisation basique du retry."""
    print("=== Exemple d'utilisation basique ===")

    # Configuration personnalisée
    config = RetryConfig(
        max_attempts=3,
        base_delay=1.0,
        max_delay=10.0,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        jitter=True,
    )

    try:
        result = execute_with_retry(
            simulate_api_call,
            success_rate=0.2,
            operation_name="basic_api_call",
            config=config,
        )
        print(f"Résultat final: {result}")
    except Exception as e:
        print(f"Échec définitif: {e}")


def example_different_strategies():
    """Exemple avec différentes stratégies de retry."""
    print("\n=== Exemple avec différentes stratégies ===")

    strategies = [
        (RetryStrategy.EXPONENTIAL_BACKOFF, "Backoff exponentiel"),
        (RetryStrategy.LINEAR_BACKOFF, "Backoff linéaire"),
        (RetryStrategy.CONSTANT_DELAY, "Délai constant"),
        (RetryStrategy.FIBONACCI_BACKOFF, "Backoff Fibonacci"),
    ]

    for strategy, name in strategies:
        print(f"\n--- Test de la stratégie: {name} ---")

        config = RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            max_delay=10.0,
            strategy=strategy,
            jitter=False,  # Désactiver le jitter pour voir les délais exacts
        )

        try:
            result = execute_with_retry(
                simulate_api_call,
                success_rate=0.1,
                operation_name=f"strategy_{strategy.value}",
                config=config,
            )
            print(f"✅ Succès avec {name}")
        except Exception as e:
            print(f"❌ Échec avec {name}: {e}")


def example_decorators():
    """Exemple d'utilisation des décorateurs spécialisés."""
    print("\n=== Exemple d'utilisation des décorateurs ===")

    # Test du décorateur API
    print("\n--- Test du décorateur API ---")
    try:
        result = api_function_with_retry()
        print(f"✅ API function réussie: {result}")
    except Exception as e:
        print(f"❌ API function échouée: {e}")

    # Test du décorateur DB
    print("\n--- Test du décorateur DB ---")
    try:
        result = db_function_with_retry()
        print(f"✅ DB function réussie: {result}")
    except Exception as e:
        print(f"❌ DB function échouée: {e}")


def example_fatal_error_handling():
    """Exemple de gestion des erreurs fatales."""
    print("\n=== Exemple de gestion des erreurs fatales ===")

    config = RetryConfig(max_attempts=3, base_delay=1.0, max_delay=10.0)

    try:
        result = execute_with_retry(
            simulate_fatal_error, operation_name="fatal_error_test", config=config
        )
        print(f"Résultat: {result}")
    except FatalError as e:
        print(f"❌ Erreur fatale détectée et non retryée: {e}")
    except Exception as e:
        print(f"❌ Autre erreur: {e}")


def example_metrics_analysis():
    """Exemple d'analyse des métriques de retry."""
    print("\n=== Exemple d'analyse des métriques ===")

    # Réinitialiser les métriques
    reset_retry_metrics()

    # Effectuer plusieurs opérations
    operations = [
        ("api_call_1", lambda: simulate_api_call(0.1, "api_call_1")),
        ("api_call_2", lambda: simulate_api_call(0.3, "api_call_2")),
        ("db_operation_1", lambda: simulate_database_operation(0.2, "db_operation_1")),
        ("db_operation_2", lambda: simulate_database_operation(0.4, "db_operation_2")),
    ]

    config = RetryConfig(max_attempts=2, base_delay=0.5, max_delay=5.0)

    for operation_name, operation_func in operations:
        print(f"\n--- Test de {operation_name} ---")
        try:
            result = execute_with_retry(
                operation_func, operation_name=operation_name, config=config
            )
            print(f"✅ {operation_name} réussi")
        except Exception as e:
            print(f"❌ {operation_name} échoué: {e}")

    # Afficher les métriques
    print("\n--- Analyse des métriques ---")
    print_retry_summary()

    # Métriques détaillées par opération
    print("\n--- Métriques détaillées ---")
    all_metrics = get_retry_metrics()
    for operation_name, metrics in all_metrics.items():
        print(f"\n{operation_name}:")
        print(f"  • Tentatives: {metrics.total_attempts}")
        print(f"  • Succès: {metrics.successful_attempts}")
        print(f"  • Taux de succès: {metrics.success_rate*100:.1f}%")
        print(f"  • Délai total: {metrics.total_delay_seconds:.2f}s")
        print(f"  • Délai moyen: {metrics.average_delay:.2f}s")
        if metrics.retry_reasons:
            print(f"  • Raisons des retry: {', '.join(metrics.retry_reasons)}")


def example_integration_with_metrics():
    """Exemple d'intégration avec le système de métriques existant."""
    print("\n=== Exemple d'intégration avec les métriques ===")

    try:
        from metrics import start_operation, end_operation, print_summary
        from retry import execute_with_retry

        # Démarrage du suivi des métriques
        metrics = start_operation("retry_integration_test", "api_call")

        # Configuration du retry
        config = RetryConfig(max_attempts=3, base_delay=1.0, max_delay=10.0)

        try:
            # Exécution avec retry
            result = execute_with_retry(
                simulate_api_call,
                success_rate=0.2,
                operation_name="integration_test",
                config=config,
            )

            # Fin du suivi avec succès
            end_operation(metrics, success=True, records_processed=1, api_calls=1)

            print(f"✅ Intégration réussie: {result}")

        except Exception as e:
            # Fin du suivi avec échec
            end_operation(
                metrics,
                success=False,
                error_message=str(e),
                records_processed=0,
                api_calls=1,
            )
            print(f"❌ Intégration échouée: {e}")

        # Affichage des métriques combinées
        print("\n--- Métriques combinées ---")
        print_summary()
        print_retry_summary()

    except ImportError:
        print("⚠️  Module metrics non disponible pour l'intégration")


def example_custom_retryable_exceptions():
    """Exemple avec des exceptions récupérables personnalisées."""
    print("\n=== Exemple avec exceptions personnalisées ===")

    class CustomAPIError(RetryableError):
        """Erreur API personnalisée récupérable."""

        pass

    class CustomDBError(RetryableError):
        """Erreur DB personnalisée récupérable."""

        pass

    def simulate_custom_api_call():
        """Simule un appel API avec erreurs personnalisées."""
        print("🔄 Tentative d'appel API personnalisé")

        if random.random() < 0.3:
            print("✅ Succès")
            return {"status": "success"}
        else:
            error = random.choice(
                [
                    CustomAPIError("Erreur API temporaire"),
                    CustomDBError("Erreur DB temporaire"),
                    ConnectionError("Erreur de connexion"),
                ]
            )
            print(f"❌ Échec: {error}")
            raise error

    # Configuration avec exceptions personnalisées
    config = RetryConfig(
        max_attempts=3,
        base_delay=1.0,
        max_delay=10.0,
        retryable_exceptions=[
            ConnectionError,
            TimeoutError,
            OSError,
            CustomAPIError,
            CustomDBError,
            RetryableError,
        ],
    )

    try:
        result = execute_with_retry(
            simulate_custom_api_call,
            operation_name="custom_exceptions_test",
            config=config,
        )
        print(f"✅ Test réussi: {result}")
    except Exception as e:
        print(f"❌ Test échoué: {e}")


if __name__ == "__main__":
    print("Exemples d'utilisation du système de retry N2F")
    print("=" * 60)

    try:
        # Exemples d'utilisation
        example_basic_retry()
        example_different_strategies()
        example_decorators()
        example_fatal_error_handling()
        example_metrics_analysis()
        example_integration_with_metrics()
        example_custom_retryable_exceptions()

    except Exception as e:
        print(f"Erreur lors de l'exécution des exemples : {e}")

    print("\n" + "=" * 60)
    print("Exemples terminés")
