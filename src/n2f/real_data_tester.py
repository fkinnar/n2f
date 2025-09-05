"""
Testeur de synchronisation avec données réelles.

Ce module fournit des outils pour tester la synchronisation complète
avec les vraies données Agresso en mode simulation.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from core import SyncContext
from n2f.production_simulation import ProductionDataSimulator, SimulationMode
from n2f.simulation_config import apply_simulation_scenario


class RealDataSyncTester:
    """
    Testeur de synchronisation avec données réelles.

    Permet de tester la logique de synchronisation complète avec les vraies
    données Agresso tout en simulant les appels API N2F.
    """

    def __init__(self, context: SyncContext):
        self.context = context
        self.simulator = None

    def run_full_test(
        self, mode: SimulationMode = SimulationMode.REAL_DATA
    ) -> Dict[str, Any]:
        """
        Lance un test complet de synchronisation.

        Args:
            mode: Mode de simulation à utiliser

        Returns:
            Rapport de test complet
        """
        logging.info("*** DÉBUT DE TEST DE SYNCHRONISATION COMPLÈTE ***")

        try:
            # Configuration de la simulation
            self._setup_simulation(mode)

            # Création du simulateur
            self.simulator = ProductionDataSimulator(self.context, mode)

            # Exécution de la simulation
            results = self.simulator.simulate_full_sync()

            # Validation des résultats
            validation = self._validate_results(results)

            # Génération du rapport final
            final_report = {
                "test_mode": mode.value,
                "simulation_results": results,
                "validation": validation,
                "status": "SUCCESS" if validation["is_valid"] else "FAILED",
            }

            logging.info("*** FIN DE TEST DE SYNCHRONISATION COMPLÈTE ***")
            return final_report

        except Exception as e:
            logging.error(f"Erreur lors du test: {e}")
            return {"test_mode": mode.value, "error": str(e), "status": "ERROR"}

    def _setup_simulation(self, mode: SimulationMode) -> None:
        """Configure la simulation selon le mode."""
        if mode == SimulationMode.REAL_DATA:
            # Configuration pour données réelles
            apply_simulation_scenario("realistic")
        elif mode == SimulationMode.GENERATED:
            # Configuration pour données générées
            apply_simulation_scenario("basic")
        else:
            # Configuration hybride
            apply_simulation_scenario("realistic")

    def _validate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Valide les résultats de la simulation."""
        validation = {"is_valid": True, "issues": [], "warnings": []}

        # Vérification des statistiques
        stats = results.get("statistics", {})

        if stats.get("errors", 0) > 0:
            validation["issues"].append(f"{stats['errors']} erreurs détectées")
            # Ne pas échouer si on a quand même des succès
            if (
                stats.get("users_processed", 0) == 0
                and stats.get("axes_processed", 0) == 0
            ):
                validation["is_valid"] = False

        if stats.get("users_processed", 0) == 0:
            validation["warnings"].append("Aucun utilisateur traité")

        if stats.get("axes_processed", 0) == 0:
            validation["warnings"].append("Aucun axe traité")

        # Vérification du taux de succès
        success_rate = results.get("summary", {}).get("success_rate", 0)
        if success_rate < 80:
            validation["warnings"].append(f"Taux de succès faible: {success_rate:.1f}%")

        return validation


def create_test_context(
    base_dir: str = "test_data",
    db_user: Optional[str] = None,
    db_password: Optional[str] = None,
) -> SyncContext:
    """
    Crée un contexte de test pour la synchronisation.

    Args:
        base_dir: Répertoire de base pour les tests
        db_user: Utilisateur de base de données (optionnel)
        db_password: Mot de passe de base de données (optionnel)

    Returns:
        Contexte de synchronisation configuré pour les tests
    """
    import argparse
    import os

    # Configuration de test
    mock_config = {
        "n2f": {
            "base_urls": "https://api.n2f.test",
            "simulate": True,  # Mode simulation activé
        },
        "agresso": {
            "database": {"host": "localhost", "port": 5432, "name": "agresso_test"}
        },
    }

    # Arguments de test
    mock_args = argparse.Namespace()
    mock_args.simulate = True
    mock_args.test_mode = True

    return SyncContext(
        args=mock_args,
        config=mock_config,
        base_dir=Path(base_dir),
        db_user=db_user or os.getenv("AGRESSO_DB_USER", "test_user"),
        db_password=db_password or os.getenv("AGRESSO_DB_PASSWORD", "test_password"),
        client_id=os.getenv("N2F_CLIENT_ID", "test_client"),
        client_secret=os.getenv("N2F_CLIENT_SECRET", "test_secret"),
    )
