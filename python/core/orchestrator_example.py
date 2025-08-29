"""
Exemple d'utilisation de l'orchestrateur de synchronisation N2F.

Ce module démontre comment utiliser l'orchestrateur pour différentes
scénarios de synchronisation.
"""

import argparse
from pathlib import Path
from .orchestrator import SyncOrchestrator


def example_basic_usage():
    """Exemple d'utilisation basique de l'orchestrateur."""
    print("=== Exemple d'utilisation basique ===")
    
    # Création d'arguments simulés
    args = argparse.Namespace(
        create=True,
        update=False,
        delete=False,
        config='dev',
        scope=['users']
    )
    
    # Chemin de configuration
    config_path = Path(__file__).parent.parent.parent / "dev.yaml"
    
    # Création de l'orchestrateur
    orchestrator = SyncOrchestrator(config_path, args)
    
    # Affichage du résumé de configuration
    config_summary = orchestrator.get_configuration_summary()
    print(f"Configuration file: {config_summary['config_file']}")
    print(f"Database prod: {config_summary['database_prod']}")
    print(f"API sandbox: {config_summary['api_sandbox']}")
    print(f"Available scopes: {config_summary['available_scopes']}")
    print(f"Enabled scopes: {config_summary['enabled_scopes']}")
    
    # Exécution de la synchronisation
    print("\nExécution de la synchronisation...")
    orchestrator.run()


def example_multiple_scopes():
    """Exemple avec plusieurs scopes."""
    print("\n=== Exemple avec plusieurs scopes ===")
    
    args = argparse.Namespace(
        create=True,
        update=True,
        delete=False,
        config='dev',
        scope=['users', 'departments']
    )
    
    config_path = Path(__file__).parent.parent.parent / "dev.yaml"
    orchestrator = SyncOrchestrator(config_path, args)
    orchestrator.run()


def example_all_scopes():
    """Exemple avec tous les scopes."""
    print("\n=== Exemple avec tous les scopes ===")
    
    args = argparse.Namespace(
        create=True,
        update=True,
        delete=True,
        config='dev',
        scope=['all']
    )
    
    config_path = Path(__file__).parent.parent.parent / "dev.yaml"
    orchestrator = SyncOrchestrator(config_path, args)
    orchestrator.run()


def example_error_handling():
    """Exemple de gestion d'erreur."""
    print("\n=== Exemple de gestion d'erreur ===")
    
    # Test avec un scope inexistant
    args = argparse.Namespace(
        create=True,
        update=False,
        delete=False,
        config='dev',
        scope=['inexistent_scope']
    )
    
    config_path = Path(__file__).parent.parent.parent / "dev.yaml"
    orchestrator = SyncOrchestrator(config_path, args)
    orchestrator.run()


if __name__ == "__main__":
    print("Exemples d'utilisation de l'orchestrateur N2F")
    print("=" * 50)
    
    try:
        # Exemples d'utilisation
        example_basic_usage()
        example_multiple_scopes()
        example_all_scopes()
        example_error_handling()
        
    except Exception as e:
        print(f"Erreur lors de l'exécution des exemples : {e}")
    
    print("\n" + "=" * 50)
    print("Exemples terminés")
