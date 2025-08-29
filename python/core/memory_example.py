"""
Exemple d'utilisation du MemoryManager pour la synchronisation N2F.

Ce module démontre comment utiliser le gestionnaire de mémoire pour :
- Enregistrer des DataFrames avec gestion automatique
- Surveiller l'utilisation mémoire
- Nettoyer la mémoire par scope
- Obtenir des métriques détaillées
"""

import pandas as pd
import numpy as np
from pathlib import Path
from memory_manager import (
    get_memory_manager,
    register_dataframe,
    get_dataframe,
    cleanup_scope,
    cleanup_all,
    print_memory_summary,
    get_memory_stats
)


def create_sample_dataframe(rows: int = 1000, cols: int = 10) -> pd.DataFrame:
    """Crée un DataFrame de test avec des données aléatoires."""
    data = {
        f'col_{i}': np.random.randn(rows) for i in range(cols)
    }
    return pd.DataFrame(data)


def example_basic_usage():
    """Exemple d'utilisation basique du MemoryManager."""
    print("=== Exemple d'utilisation basique ===")

    # Initialisation avec une limite de 100MB pour les tests
    memory_manager = get_memory_manager(max_memory_mb=100)

    # Création de DataFrames de test
    df1 = create_sample_dataframe(5000, 5)  # ~200KB
    df2 = create_sample_dataframe(10000, 8)  # ~640KB
    df3 = create_sample_dataframe(20000, 12)  # ~1.9MB

    # Enregistrement des DataFrames
    print("\n📊 Enregistrement des DataFrames...")
    register_dataframe("users_data", df1, scope="users")
    register_dataframe("projects_data", df2, scope="projects")
    register_dataframe("large_dataset", df3, scope="projects")

    # Affichage du résumé
    print_memory_summary()

    # Récupération d'un DataFrame
    print("\n🔍 Récupération d'un DataFrame...")
    retrieved_df = get_dataframe("users_data")
    if retrieved_df is not None:
        print(f"DataFrame récupéré: {retrieved_df.shape}")

    # Nettoyage d'un scope
    print("\n🧹 Nettoyage du scope 'users'...")
    freed_memory = cleanup_scope("users")
    print(f"Mémoire libérée: {freed_memory:.1f}MB")

    print_memory_summary()


def example_memory_pressure():
    """Exemple de gestion de la pression mémoire."""
    print("\n=== Exemple de gestion de la pression mémoire ===")

    # Initialisation avec une limite très basse pour simuler la pression
    memory_manager = get_memory_manager(max_memory_mb=50)

    # Tentative d'enregistrement de gros DataFrames
    print("\n📊 Tentative d'enregistrement de gros DataFrames...")

    for i in range(10):
        df = create_sample_dataframe(10000, 15)  # ~1.2MB par DataFrame
        success = register_dataframe(f"large_df_{i}", df, scope="test")
        if not success:
            print(f"⚠️  Échec d'enregistrement pour large_df_{i}")
            break

    print_memory_summary()

    # Nettoyage complet
    print("\n🧹 Nettoyage complet...")
    cleanup_all()


def example_scope_management():
    """Exemple de gestion par scope."""
    print("\n=== Exemple de gestion par scope ===")

    memory_manager = get_memory_manager(max_memory_mb=200)

    # Création de DataFrames pour différents scopes
    scopes = ["users", "projects", "companies", "departments"]

    for scope in scopes:
        print(f"\n📊 Enregistrement pour le scope '{scope}'...")
        for i in range(3):
            df = create_sample_dataframe(5000, 8)
            register_dataframe(f"{scope}_data_{i}", df, scope=scope)

    print_memory_summary()

    # Nettoyage sélectif par scope
    for scope in scopes[:2]:  # Nettoyer seulement les 2 premiers scopes
        print(f"\n🧹 Nettoyage du scope '{scope}'...")
        freed = cleanup_scope(scope)
        print(f"Mémoire libérée: {freed:.1f}MB")

    print_memory_summary()


def example_metrics_detailed():
    """Exemple d'utilisation des métriques détaillées."""
    print("\n=== Exemple de métriques détaillées ===")

    memory_manager = get_memory_manager(max_memory_mb=150)

    # Création de DataFrames avec différentes tailles
    sizes = [(1000, 5), (5000, 10), (10000, 15), (20000, 20)]

    for i, (rows, cols) in enumerate(sizes):
        df = create_sample_dataframe(rows, cols)
        register_dataframe(f"df_{i}", df, scope=f"scope_{i % 3}")

    # Obtenir les statistiques détaillées
    stats = get_memory_stats()

    print("\n📊 Statistiques détaillées:")
    print(f"Utilisation actuelle: {stats['memory_manager']['current_usage_mb']:.1f}MB")
    print(f"Pic d'utilisation: {stats['memory_manager']['peak_usage_mb']:.1f}MB")
    print(f"DataFrames actifs: {stats['memory_manager']['active_dataframes']}")
    print(f"Mémoire système utilisée: {stats['system']['memory_percentage']:.1f}%")

    print("\n📁 Répartition par scope:")
    for scope, info in stats['dataframes_by_scope'].items():
        print(f"  • {scope}: {info['count']} DataFrames, {info['size_mb']:.1f}MB")

    # Nettoyage final
    cleanup_all()


def example_integration_with_sync():
    """Exemple d'intégration avec un processus de synchronisation."""
    print("\n=== Exemple d'intégration avec synchronisation ===")

    memory_manager = get_memory_manager(max_memory_mb=300)

    # Simulation d'un processus de synchronisation
    sync_scopes = ["users", "projects", "companies"]

    for scope in sync_scopes:
        print(f"\n🔄 Synchronisation du scope '{scope}'...")

        # Simulation de chargement de données Agresso
        agresso_data = create_sample_dataframe(8000, 12)
        register_dataframe(f"{scope}_agresso", agresso_data, scope=scope)

        # Simulation de récupération de données N2F
        n2f_data = create_sample_dataframe(6000, 10)
        register_dataframe(f"{scope}_n2f", n2f_data, scope=scope)

        # Simulation de traitement
        processed_data = create_sample_dataframe(4000, 8)
        register_dataframe(f"{scope}_processed", processed_data, scope=scope)

        print(f"✅ Scope '{scope}' synchronisé")

        # Nettoyage du scope après synchronisation
        freed = cleanup_scope(scope)
        print(f"🧹 Mémoire libérée pour {scope}: {freed:.1f}MB")

    print_memory_summary()
    cleanup_all()


if __name__ == "__main__":
    print("Exemples d'utilisation du MemoryManager")
    print("=" * 50)

    try:
        # Exemples d'utilisation
        example_basic_usage()
        example_memory_pressure()
        example_scope_management()
        example_metrics_detailed()
        example_integration_with_sync()

    except Exception as e:
        print(f"Erreur lors de l'exécution des exemples : {e}")

    print("\n" + "=" * 50)
    print("Exemples terminés")
