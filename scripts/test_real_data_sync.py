#!/usr/bin/env python3
"""
Script de test de synchronisation avec données réelles.

Ce script permet de tester la synchronisation complète avec les vraies
données Agresso en mode simulation.
"""

import logging
import argparse
import os
from pathlib import Path

from core import SyncContext
from n2f.real_data_tester import RealDataSyncTester, create_test_context
from n2f.production_simulation import SimulationMode


def setup_logging(level: str = "INFO") -> None:
    """Configure le logging pour les tests."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def main():
    """Fonction principale du script de test."""
    parser = argparse.ArgumentParser(
        description="Test de synchronisation avec données réelles"
    )
    parser.add_argument(
        "--mode",
        choices=["real_data", "generated", "hybrid"],
        default="real_data",
        help="Mode de simulation",
    )
    parser.add_argument("--base-dir", default="test_data", help="Répertoire de base")
    parser.add_argument("--db-user", help="Utilisateur de base de données")
    parser.add_argument("--db-password", help="Mot de passe de base de données")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Niveau de logging",
    )
    parser.add_argument(
        "--skip-dotenv-loading", action="store_true", help="Skip loading .env file"
    )

    args = parser.parse_args()

    # Chargement des variables d'environnement depuis .env
    if not args.skip_dotenv_loading:
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            logging.warning("python-dotenv not installed, skipping .env loading")

    # Configuration du logging
    setup_logging(args.log_level)

    try:
        # Création du contexte de test
        context = create_test_context(
            base_dir=args.base_dir, db_user=args.db_user, db_password=args.db_password
        )

        # Création du testeur
        tester = RealDataSyncTester(context)

        # Conversion du mode
        mode = SimulationMode(args.mode)

        # Exécution du test
        logging.info(f"Démarrage du test en mode: {mode.value}")
        results = tester.run_full_test(mode)

        # Affichage des résultats
        print("\n" + "=" * 60)
        print("RÉSULTATS DU TEST DE SYNCHRONISATION")
        print("=" * 60)
        print(f"Mode: {results['test_mode']}")
        print(f"Statut: {results['status']}")

        if results["status"] == "SUCCESS":
            stats = results["simulation_results"]["statistics"]
            summary = results["simulation_results"]["summary"]

            print("\nStatistiques:")
            print(f"  - Utilisateurs traités: {stats['users_processed']}")
            print(f"  - Utilisateurs créés: {stats['users_created']}")
            print(f"  - Utilisateurs mis à jour: {stats['users_updated']}")
            print(f"  - Axes traités: {stats['axes_processed']}")
            print(f"  - Axes créés: {stats['axes_created']}")
            print(f"  - Axes mis à jour: {stats['axes_updated']}")
            print(f"  - Erreurs: {stats['errors']}")
            print(f"  - Taux de succès: {summary['success_rate']:.1f}%")

            # Validation
            validation = results["validation"]
            if validation["issues"]:
                print("\nProblèmes détectés:")
                for issue in validation["issues"]:
                    print(f"  - {issue}")

            if validation["warnings"]:
                print("\nAvertissements:")
                for warning in validation["warnings"]:
                    print(f"  - {warning}")

        elif results["status"] == "ERROR":
            print(f"\nErreur: {results['error']}")

        print("=" * 60)

        # Code de sortie
        return 0 if results["status"] == "SUCCESS" else 1

    except Exception as e:
        logging.error(f"Erreur fatale: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
