"""
Production data simulation system for N2F API operations.

This module provides simulation capabilities using real Agresso data
while simulating N2F API calls to avoid side effects like sending emails.
"""

import logging
from typing import Dict, Any
from enum import Enum

from core import SyncContext
from n2f.client import N2fApiClient
from n2f.simulation import EnhancedSimulator
from agresso.process import select
from business.normalize import normalize_agresso_users, normalize_n2f_users

# Les synchronizers seront importés dynamiquement pour éviter les dépendances


class SimulationMode(Enum):
    """Modes de simulation disponibles."""

    GENERATED = "generated"  # Données générées artificiellement
    REAL_DATA = "real_data"  # Vraies données Agresso + simulation API
    HYBRID = "hybrid"  # Mélange selon configuration


class ProductionDataSimulator:
    """
    Simulateur pour les données de production.

    Utilise les vraies données Agresso pour tester la logique de synchronisation
    complète tout en simulant les appels API N2F.
    """

    def __init__(
        self, context: SyncContext, mode: SimulationMode = SimulationMode.REAL_DATA
    ):
        self.context = context
        self.mode = mode
        self.simulator = EnhancedSimulator()
        self.client = N2fApiClient(context)

        # Statistiques de simulation
        self.stats = {
            "users_processed": 0,
            "users_created": 0,
            "users_updated": 0,
            "users_deleted": 0,
            "axes_processed": 0,
            "axes_created": 0,
            "axes_updated": 0,
            "axes_deleted": 0,
            "errors": 0,
            "warnings": 0,
        }

    def simulate_full_sync(self) -> Dict[str, Any]:
        """
        Simule une synchronisation complète avec les vraies données Agresso.

        Returns:
            Dict contenant les statistiques et résultats de la simulation
        """
        logging.info("*** DÉBUT DE SIMULATION AVEC DONNÉES RÉELLES ***")

        try:
            # 1. Récupération des vraies données Agresso
            agresso_data = self._get_real_agresso_data()

            # 2. Récupération des données N2F (simulées)
            n2f_data = self._get_simulated_n2f_data()

            # 3. Normalisation des données
            normalized_data = self._normalize_data(agresso_data, n2f_data)

            # 4. Simulation de la synchronisation
            sync_results = self._simulate_synchronization(normalized_data)

            # 5. Génération du rapport
            report = self._generate_report(sync_results)

            logging.info("*** FIN DE SIMULATION AVEC DONNÉES RÉELLES ***")
            return report

        except Exception as e:
            logging.error(f"Erreur lors de la simulation: {e}")
            self.stats["errors"] += 1
            raise

    def _get_real_agresso_data(self) -> Dict[str, Any]:
        """Récupère les vraies données Agresso via SQL."""
        logging.info(">> Récupération des vraies données Agresso")

        # Pour le mode GENERATED, on utilise des données simulées
        if self.mode == SimulationMode.GENERATED:
            logging.info("Mode GENERATED: utilisation de données simulées pour Agresso")
            import pandas as pd

            # Données simulées pour les utilisateurs
            df_users = pd.DataFrame(
                {
                    "AdresseEmail": [
                        "user1@test.com",
                        "user2@test.com",
                        "user3@test.com",
                    ],
                    "Manager": [
                        "manager1@test.com",
                        "manager2@test.com",
                        "manager3@test.com",
                    ],
                    "Structure": ["Structure1", "Structure2", "Structure3"],
                    "Methode_SSO": ["SSO1", "SSO2", "SSO3"],
                    "Entreprise": ["Company1", "Company2", "Company3"],
                    "Prenom": ["User1", "User2", "User3"],
                    "Nom": ["Test1", "Test2", "Test3"],
                    "Role": ["Role1", "Role2", "Role3"],
                    "Profil": ["Profil1", "Profil2", "Profil3"],
                    "Creation_Vehicule": [
                        False,
                        False,
                        False,
                    ],  # Colonne manquante ajoutée
                    "active": [True, True, True],
                }
            )

            # Données simulées pour les axes
            df_axes = pd.DataFrame(
                {
                    "code": ["AXE001", "AXE002", "AXE003"],
                    "name": ["Axe 1", "Axe 2", "Axe 3"],
                    "description": ["Description 1", "Description 2", "Description 3"],
                    "type": ["PROJECT", "PLATE", "SUBPOST"],
                    "axe_id": ["axe1", "axe2", "axe3"],
                    "active": [True, True, True],
                }
            )

            logging.info(
                f"Données simulées: {len(df_users)} utilisateurs et {len(df_axes)} axes"
            )
            return {"users": df_users, "axes": df_axes}

        try:
            # Récupération des vraies données Agresso
            # Utilise le fichier .prod.sql car la vue iris_N2F_User n'existe qu'en prod
            df_users = select(
                str(self.context.base_dir),
                self.context.db_user or "",
                self.context.db_password or "",
                "sql",  # sql_path
                "get-agresso-n2f-users.prod.sql",  # sql_filename
                True,  # prod = True pour utiliser la vue de production
            )

            # Récupération des axes Agresso
            df_axes = select(
                str(self.context.base_dir),
                self.context.db_user or "",
                self.context.db_password or "",
                "sql",  # sql_path
                "get-agresso-n2f-customaxes.prod.sql",  # sql_filename
                True,  # prod = True pour utiliser la vue de production
            )

            logging.info(
                f"Récupéré {len(df_users)} utilisateurs et {len(df_axes)} axes"
            )

            return {"users": df_users, "axes": df_axes}

        except Exception as e:
            logging.error(f"Erreur lors de la récupération des données Agresso: {e}")
            raise

    def _get_simulated_n2f_data(self) -> Dict[str, Any]:
        """Récupère les données N2F simulées."""
        logging.info(">> Récupération des données N2F simulées")

        try:
            # Utilise le client avec simulation activée
            users_df = self.client.get_users()
            companies_df = self.client.get_companies()
            roles_df = self.client.get_roles()
            profiles_df = self.client.get_userprofiles()

            logging.info(
                f"Données N2F simulées: {len(users_df)} users, "
                f"{len(companies_df)} companies"
            )

            return {
                "users": users_df,
                "companies": companies_df,
                "roles": roles_df,
                "profiles": profiles_df,
            }

        except Exception as e:
            logging.error(f"Erreur lors de la récupération des données N2F: {e}")
            raise

    def _normalize_data(
        self, agresso_data: Dict[str, Any], n2f_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalise les données pour la synchronisation."""
        logging.info(">> Normalisation des données")

        try:
            # Normalisation des utilisateurs Agresso
            normalized_users = normalize_agresso_users(agresso_data["users"])

            # Normalisation des utilisateurs N2F
            normalized_n2f_users = normalize_n2f_users(n2f_data["users"])

            logging.info(
                f"Données normalisées: {len(normalized_users)} users Agresso, "
                f"{len(normalized_n2f_users)} users N2F"
            )

            return {
                "agresso_users": normalized_users,
                "n2f_users": normalized_n2f_users,
                "n2f_companies": n2f_data["companies"],
                "n2f_roles": n2f_data["roles"],
                "n2f_profiles": n2f_data["profiles"],
                "agresso_axes": agresso_data["axes"],
            }

        except Exception as e:
            logging.error(f"Erreur lors de la normalisation: {e}")
            raise

    def _simulate_synchronization(
        self, normalized_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simule la synchronisation complète."""
        logging.info(">> Simulation de la synchronisation")

        try:
            # Simulation de la synchronisation des utilisateurs
            user_sync_results = self._simulate_user_sync(normalized_data)

            # Simulation de la synchronisation des axes
            axe_sync_results = self._simulate_axe_sync(normalized_data)

            return {"users": user_sync_results, "axes": axe_sync_results}

        except Exception as e:
            logging.error(f"Erreur lors de la synchronisation: {e}")
            raise

    def _simulate_user_sync(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simule la synchronisation des utilisateurs."""
        logging.info(">> Simulation synchronisation utilisateurs")

        try:
            # Import dynamique pour éviter les dépendances circulaires
            from business.process.user_synchronizer import UserSynchronizer

            # Création du synchronizer avec les bons paramètres
            synchronizer = UserSynchronizer(
                self.client, self.context.get_config_value("n2f").get("sandbox", True)
            )

            # Simulation des opérations CRUD
            results = {"created": [], "updated": [], "deleted": [], "errors": []}

            # Traitement des utilisateurs Agresso
            for _, user in data["agresso_users"].iterrows():
                try:
                    # Simulation de la création/mise à jour
                    payload = synchronizer.build_payload(
                        user,
                        data["agresso_users"],
                        data["n2f_users"],
                        data["n2f_companies"],
                    )
                    result = self.client.create_user(payload)

                    if result.success:
                        if result.action_type == "create":
                            results["created"].append(user.get("email", "unknown"))
                            self.stats["users_created"] += 1
                        else:
                            results["updated"].append(user.get("email", "unknown"))
                            self.stats["users_updated"] += 1
                    else:
                        results["errors"].append(
                            f"Erreur pour {user.get('email', 'unknown')}: "
                            f"{result.message}"
                        )
                        self.stats["errors"] += 1

                    self.stats["users_processed"] += 1

                except Exception as e:
                    error_msg = (
                        f"Erreur pour utilisateur {user.get('email', 'unknown')}: {e}"
                    )
                    results["errors"].append(error_msg)
                    self.stats["errors"] += 1
                    logging.warning(error_msg)

            logging.info(
                f"Synchronisation utilisateurs: {len(results['created'])} créés, "
                f"{len(results['updated'])} mis à jour, "
                f"{len(results['errors'])} erreurs"
            )
            return results

        except Exception as e:
            logging.error(f"Erreur lors de la synchronisation des utilisateurs: {e}")
            raise

    def _simulate_axe_sync(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simule la synchronisation des axes."""
        logging.info(">> Simulation synchronisation axes")

        try:
            # Import dynamique pour éviter les dépendances circulaires
            from business.process.axe_synchronizer import AxeSynchronizer

            # Création du synchronizer avec les bons paramètres
            synchronizer = AxeSynchronizer(
                self.client,
                self.context.get_config_value("n2f").get("sandbox", True),
                "default_axe",
                "projects",
            )

            results = {"created": [], "updated": [], "deleted": [], "errors": []}

            # Traitement des axes Agresso
            for _, axe in data["agresso_axes"].iterrows():
                try:
                    # Simulation de la création/mise à jour
                    import pandas as pd

                    payload = synchronizer.build_payload(
                        axe,
                        data["agresso_axes"],
                        pd.DataFrame(),  # df_n2f vide pour la simulation
                        data.get("n2f_companies"),
                    )
                    result = self.client.upsert_axe_value(
                        company_id="default_company",
                        axe_id=axe.get("axe_id", "default_axe"),
                        payload=payload,
                    )

                    if result.success:
                        if result.action_type == "create":
                            results["created"].append(axe.get("code", "unknown"))
                            self.stats["axes_created"] += 1
                        else:
                            results["updated"].append(axe.get("code", "unknown"))
                            self.stats["axes_updated"] += 1
                    else:
                        results["errors"].append(
                            f"Erreur pour axe {axe.get('code', 'unknown')}: "
                            f"{result.message}"
                        )
                        self.stats["errors"] += 1

                    self.stats["axes_processed"] += 1

                except Exception as e:
                    error_msg = f"Erreur pour axe {axe.get('code', 'unknown')}: {e}"
                    results["errors"].append(error_msg)
                    self.stats["errors"] += 1
                    logging.warning(error_msg)

            logging.info(
                f"Synchronisation axes: {len(results['created'])} créés, "
                f"{len(results['updated'])} mis à jour, "
                f"{len(results['errors'])} erreurs"
            )
            return results

        except Exception as e:
            logging.error(f"Erreur lors de la synchronisation des axes: {e}")
            raise

    def _generate_report(self, sync_results: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un rapport de simulation."""
        logging.info(">> Génération du rapport de simulation")

        report = {
            "simulation_mode": self.mode.value,
            "statistics": self.stats.copy(),
            "results": sync_results,
            "summary": {
                "total_processed": self.stats["users_processed"]
                + self.stats["axes_processed"],
                "total_success": self.stats["users_created"]
                + self.stats["users_updated"]
                + self.stats["axes_created"]
                + self.stats["axes_updated"],
                "total_errors": self.stats["errors"],
                "success_rate": 0.0,
            },
        }

        # Calcul du taux de succès
        total_processed = report["summary"]["total_processed"]
        if total_processed > 0:
            report["summary"]["success_rate"] = (
                report["summary"]["total_success"] / total_processed
            ) * 100

        logging.info(
            f"Rapport généré: {report['summary']['total_processed']} éléments traités, "
            f"taux de succès: {report['summary']['success_rate']:.1f}%"
        )

        return report
