"""
Exemple d'utilisation du système de métriques N2F.

Ce module démontre comment utiliser le système de métriques pour :
- Surveiller les performances des opérations
- Collecter des statistiques détaillées
- Générer des rapports de performance
- Exporter les métriques au format JSON
"""

import time
import random
from pathlib import Path
from ..metrics import (
    get_metrics,
    start_operation,
    end_operation,
    record_memory_usage,
    print_summary,
    export_metrics,
)


def simulate_sync_operation(
    scope: str,
    action: str,
    duration: float = 1.0,
    success: bool = True,
    records: int = 100,
) -> None:
    """Simule une opération de synchronisation."""
    print(f"🔄 Démarrage {action} pour {scope}...")

    # Démarrage du suivi
    metrics = start_operation(scope, action)

    # Simulation de l'opération
    time.sleep(duration)

    # Simulation d'erreur aléatoire
    if not success:
        error_message = f"Erreur simulée pour {scope} - {action}"
        print(f"❌ {error_message}")
    else:
        print(f"✅ {action} terminé pour {scope} ({records} enregistrements)")

    # Enregistrement de l'utilisation mémoire simulée
    memory_usage = random.uniform(10.0, 50.0)
    record_memory_usage(memory_usage, scope)

    # Fin du suivi
    end_operation(
        metrics,
        success=success,
        error_message=None if success else f"Erreur simulée pour {scope}",
        records_processed=records if success else 0,
        memory_usage_mb=memory_usage,
        api_calls=random.randint(5, 20),
        cache_hits=random.randint(0, 10),
        cache_misses=random.randint(0, 5),
    )


def example_metrics_basic_usage() -> None:
    """Exemple d'utilisation basique du système de métriques."""
    print("=== Exemple d'utilisation basique ===")

    # Simulation d'opérations de synchronisation
    operations = [
        ("users", "create", 2.0, True, 150),
        ("users", "update", 1.5, True, 75),
        ("projects", "create", 3.0, True, 200),
        ("projects", "delete", 1.0, False, 0),  # Échec simulé
        ("companies", "sync", 2.5, True, 50),
    ]

    for scope, action, duration, success, records in operations:
        simulate_sync_operation(scope, action, duration, success, records)

    # Affichage du résumé
    print_summary()


def example_detailed_metrics() -> None:
    """Exemple avec métriques détaillées."""
    print("\n=== Exemple avec métriques détaillées ===")

    # Simulation d'opérations plus complexes
    scopes = ["users", "projects", "companies", "departments"]
    actions = ["create", "update", "delete", "sync"]

    for scope in scopes:
        for action in actions:
            # Simulation de variations de performance
            duration = random.uniform(0.5, 4.0)
            success = random.random() > 0.1  # 90% de succès
            records = random.randint(10, 300)

            simulate_sync_operation(scope, action, duration, success, records)

    # Affichage du résumé détaillé
    print_summary()

    # Export des métriques
    output_path = export_metrics()
    print(f"\n📊 Métriques exportées vers: {output_path}")


def example_performance_monitoring() -> None:
    """Exemple de monitoring de performance."""
    print("\n=== Exemple de monitoring de performance ===")

    # Simulation d'un processus de synchronisation avec monitoring
    metrics = get_metrics()

    # Monitoring en temps réel
    for i in range(5):
        scope = f"batch_{i + 1}"
        action = "sync"

        print(f"\n📊 Monitoring batch {i + 1}...")

        # Démarrage avec métriques
        op_metrics = start_operation(scope, action)

        # Simulation de travail avec monitoring
        start_time = time.time()
        for step in range(3):
            time.sleep(0.5)
            elapsed = time.time() - start_time
            print(f"   Étape {step + 1}: {elapsed:.1f}s écoulées")

        # Fin avec métriques détaillées
        end_operation(
            op_metrics,
            success=True,
            records_processed=random.randint(50, 200),
            memory_usage_mb=random.uniform(20.0, 80.0),
            api_calls=random.randint(10, 30),
            cache_hits=random.randint(5, 15),
            cache_misses=random.randint(0, 8),
        )

    # Résumé final
    print_summary()


def example_error_tracking() -> None:
    """Exemple de suivi des erreurs."""
    print("\n=== Exemple de suivi des erreurs ===")

    # Simulation d'erreurs variées
    error_scenarios = [
        ("users", "create", "Erreur de validation des données"),
        ("projects", "update", "Erreur de connexion API"),
        ("companies", "delete", "Erreur de permissions"),
        ("departments", "sync", "Timeout de la requête"),
    ]

    for scope, action, error_msg in error_scenarios:
        print(f"🔄 Test d'erreur: {action} pour {scope}")

        metrics = start_operation(scope, action)

        # Simulation de l'erreur
        time.sleep(1.0)

        end_operation(
            metrics,
            success=False,
            error_message=error_msg,
            records_processed=0,
            memory_usage_mb=random.uniform(5.0, 15.0),
            api_calls=random.randint(1, 5),
            cache_hits=0,
            cache_misses=random.randint(1, 3),
        )

    # Affichage du résumé avec erreurs
    print_summary()


def example_export_and_analysis() -> None:
    """Exemple d'export et d'analyse des métriques."""
    print("\n=== Exemple d'export et d'analyse ===")

    # Génération de métriques
    for i in range(10):
        scope = f"test_scope_{i % 3}"
        action = random.choice(["create", "update", "delete"])

        simulate_sync_operation(
            scope,
            action,
            duration=random.uniform(0.5, 2.0),
            success=random.random() > 0.2,  # 80% de succès
            records=random.randint(20, 150),
        )

    # Export des métriques
    output_path = export_metrics(Path("example_metrics.json"))
    print(f"📊 Métriques exportées vers: {output_path}")

    # Affichage du résumé
    print_summary()

    # Analyse des métriques par scope
    metrics = get_metrics()
    summary = metrics.get_summary()

    print("\n📈 ANALYSE DÉTAILLÉE:")
    print(f"   • Scopes traités: {len(summary['operations_by_scope'])}")
    print(f"   • Actions effectuées: {len(summary['operations_by_action'])}")
    print(
        f"   • Taux de succès global: {summary['summary']['success_rate'] * 100:.1f}%"
    )
    print(
        f"   • Performance moyenne: {summary['summary']['average_records_per_second']:.1f} enregistrements/s"
    )


def example_memory_monitoring() -> None:
    """Exemple de monitoring mémoire."""
    print("\n=== Exemple de monitoring mémoire ===")

    # Simulation de variations d'utilisation mémoire
    for i in range(8):
        scope = f"memory_test_{i % 2}"
        action = "process"

        # Simulation d'utilisation mémoire croissante puis décroissante
        if i < 4:
            memory_usage = 20.0 + i * 15.0  # Croissance
        else:
            memory_usage = 80.0 - (i - 4) * 15.0  # Décroissance

        print(f"🔄 {action} pour {scope} (mémoire: {memory_usage:.1f}MB)")

        metrics = start_operation(scope, action)
        time.sleep(0.5)

        record_memory_usage(memory_usage, scope)

        end_operation(
            metrics,
            success=True,
            records_processed=random.randint(10, 50),
            memory_usage_mb=memory_usage,
            api_calls=random.randint(1, 10),
            cache_hits=random.randint(0, 5),
            cache_misses=random.randint(0, 3),
        )

    # Affichage du résumé avec focus mémoire
    summary = get_metrics().get_summary()
    print("\n💾 ANALYSE MÉMOIRE:")
    print(f"   • Pic d'utilisation: {summary['memory']['peak_usage_mb']:.1f}MB")
    print(f"   • Utilisation moyenne: {summary['memory']['average_usage_mb']:.1f}MB")
    print(f"   • Échantillons mémoire: {summary['memory']['memory_samples']}")

    print_summary()


if __name__ == "__main__":
    print("Exemples d'utilisation du système de métriques N2F")
    print("=" * 60)

    try:
        # Exemples d'utilisation
        example_metrics_basic_usage()
        example_detailed_metrics()
        example_performance_monitoring()
        example_error_tracking()
        example_export_and_analysis()
        example_memory_monitoring()

    except Exception as e:
        print(f"Erreur lors de l'exécution des exemples : {e}")

    print("\n" + "=" * 60)
    print("Exemples terminés")
