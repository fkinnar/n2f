#!/usr/bin/env python3
"""
Tests spécifiques pour le module business.process.axe
"""

import unittest
import sys
import os
import pandas as pd
from unittest.mock import Mock, patch, MagicMock

# Ajouter le répertoire python au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

import business.process.axe as axe_process
from business.process.axe_types import AxeType
from core import SyncContext


class TestBusinessAxe(unittest.TestCase):
    """Tests pour le module business.process.axe."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Mock du contexte
        self.mock_context = Mock(spec=SyncContext)
        self.mock_context.base_dir = "/test/base/dir"
        self.mock_context.db_user = "test_user"
        self.mock_context.db_password = "test_password"

        # Mock des arguments
        self.mock_args = Mock()
        self.mock_args.create = True
        self.mock_args.update = True
        self.mock_args.delete = True
        self.mock_context.args = self.mock_args

        # Mock de la configuration
        self.mock_agresso_config = Mock()
        self.mock_agresso_config.sql_path = "sql"
        self.mock_agresso_config.prod = False

        self.mock_n2f_config = Mock()
        self.mock_n2f_config.sandbox = False

        # Mock du client N2F
        self.mock_n2f_client = Mock()

        # DataFrames de test
        self.df_agresso_axes = pd.DataFrame(
            {
                "code": ["PROJ1", "PROJ2", "PROJ3"],
                "name": ["Project 1", "Project 2", "Project 3"],
                "typ": [
                    "PROJECTS",
                    "PROJECTS",
                    "PROJECTS",
                ],  # Utiliser la bonne colonne
            }
        )

        self.df_n2f_companies = pd.DataFrame(
            {"uuid": ["uuid1", "uuid2"], "name": ["Company 1", "Company 2"]}
        )

        self.df_n2f_axes = pd.DataFrame(
            {"code": ["EXISTING"], "name": ["Existing Project"]}
        )

    @patch("business.process.axe.select")
    def test_load_agresso_axes_success(self, mock_select):
        """Test de chargement des axes Agresso avec succès."""
        # Configuration du mock
        mock_select.return_value = self.df_agresso_axes
        self.mock_context.get_config_value.side_effect = lambda key: (
            self.mock_agresso_config if key == "agresso" else self.mock_n2f_config
        )

        # Exécution de la fonction
        result = axe_process._load_agresso_axes(
            self.mock_context, "test_query.sql", "PROJECTS"
        )

        # Vérifications
        mock_select.assert_called_once()
        self.assertEqual(len(result), 3)
        self.assertTrue(all(result["typ"].str.upper() == "PROJECTS"))

    @patch("business.process.axe.select")
    def test_load_agresso_axes_empty_result(self, mock_select):
        """Test de chargement des axes Agresso avec résultat vide."""
        # Configuration du mock
        mock_select.return_value = pd.DataFrame()
        self.mock_context.get_config_value.side_effect = lambda key: (
            self.mock_agresso_config if key == "agresso" else self.mock_n2f_config
        )

        # Exécution de la fonction
        result = axe_process._load_agresso_axes(
            self.mock_context, "test_query.sql", "PROJECTS"
        )

        # Vérifications
        self.assertTrue(result.empty)

    @patch("business.process.axe.select")
    def test_load_agresso_axes_filtered_result(self, mock_select):
        """Test de chargement des axes Agresso avec filtrage."""
        # Configuration du mock avec données mixtes
        mixed_df = pd.DataFrame(
            {
                "code": ["PROJ1", "PLATE1", "PROJ2"],
                "name": ["Project 1", "Plate 1", "Project 2"],
                "typ": ["PROJECTS", "PLATES", "PROJECTS"],  # Utiliser la bonne colonne
            }
        )
        mock_select.return_value = mixed_df
        self.mock_context.get_config_value.side_effect = lambda key: (
            self.mock_agresso_config if key == "agresso" else self.mock_n2f_config
        )

        # Exécution de la fonction
        result = axe_process._load_agresso_axes(
            self.mock_context, "test_query.sql", "PROJECTS"
        )

        # Vérifications
        self.assertEqual(len(result), 2)
        self.assertTrue(all(result["typ"].str.upper() == "PROJECTS"))

    @patch("business.process.axe.get_n2f_projects")
    def test_load_n2f_axes_success(self, mock_get_n2f_projects):
        """Test de chargement des axes N2F avec succès."""
        # Configuration du mock
        mock_get_n2f_projects.return_value = self.df_n2f_axes

        # Exécution de la fonction
        result = axe_process._load_n2f_axes(
            self.mock_n2f_client, self.df_n2f_companies, "axe123"
        )

        # Vérifications
        self.assertEqual(mock_get_n2f_projects.call_count, 2)
        self.assertEqual(len(result), 2)  # 1 axe par entreprise

    @patch("business.process.axe.get_n2f_projects")
    def test_load_n2f_axes_empty_companies(self, mock_get_n2f_projects):
        """Test de chargement des axes N2F avec entreprises vides."""
        # Configuration du mock
        empty_companies = pd.DataFrame(
            columns=["uuid"]
        )  # DataFrame avec colonne uuid mais vide

        # Exécution de la fonction
        result = axe_process._load_n2f_axes(
            self.mock_n2f_client, empty_companies, "axe123"
        )

        # Vérifications
        mock_get_n2f_projects.assert_not_called()
        self.assertTrue(result.empty)

    @patch("business.process.axe.get_n2f_projects")
    def test_load_n2f_axes_mixed_results(self, mock_get_n2f_projects):
        """Test de chargement des axes N2F avec résultats mixtes."""
        # Configuration du mock
        mock_get_n2f_projects.side_effect = [
            self.df_n2f_axes,  # Première entreprise
            pd.DataFrame(),  # Deuxième entreprise vide
        ]

        # Exécution de la fonction
        result = axe_process._load_n2f_axes(
            self.mock_n2f_client, self.df_n2f_companies, "axe123"
        )

        # Vérifications
        self.assertEqual(len(result), 1)  # Seulement l'axe de la première entreprise

    def test_get_scope_from_axe_type_projects(self):
        """Test de détermination du scope pour les projets."""
        result = axe_process._get_scope_from_axe_type(AxeType.PROJECTS)
        self.assertEqual(result, "projects")

    def test_get_scope_from_axe_type_plates(self):
        """Test de détermination du scope pour les plaques."""
        result = axe_process._get_scope_from_axe_type(AxeType.PLATES)
        self.assertEqual(result, "plates")

    def test_get_scope_from_axe_type_subposts(self):
        """Test de détermination du scope pour les subposts."""
        result = axe_process._get_scope_from_axe_type(AxeType.SUBPOSTS)
        self.assertEqual(result, "subposts")

    def test_get_scope_from_axe_type_unknown(self):
        """Test de détermination du scope pour un type inconnu."""
        result = axe_process._get_scope_from_axe_type("UNKNOWN")
        self.assertEqual(result, "unknown")

    @patch("business.process.axe.create_n2f_axes")
    @patch("business.process.axe.reporting")
    def test_perform_sync_actions_create_only(self, mock_reporting, mock_create_axes):
        """Test des actions de synchronisation - création uniquement."""
        # Configuration des mocks
        self.mock_args.create = True
        self.mock_args.update = False
        self.mock_args.delete = False

        mock_create_axes.return_value = (self.df_agresso_axes, "created")
        # Configurer le mock pour retourner la config N2F
        self.mock_context.get_config_value.side_effect = lambda key: (
            self.mock_n2f_config if key == "n2f" else self.mock_agresso_config
        )

        # Exécution de la fonction
        result = axe_process._perform_sync_actions(
            self.mock_context,
            self.mock_n2f_client,
            "axe123",
            "PROJECTS",
            self.df_agresso_axes,
            self.df_n2f_axes,
            self.df_n2f_companies,
            "projects",
        )

        # Vérifications
        mock_create_axes.assert_called_once()
        mock_reporting.assert_called_once()
        self.assertEqual(len(result), 1)

    @patch("business.process.axe.update_n2f_axes")
    @patch("business.process.axe.reporting")
    def test_perform_sync_actions_update_only(self, mock_reporting, mock_update_axes):
        """Test des actions de synchronisation - mise à jour uniquement."""
        # Configuration des mocks
        self.mock_args.create = False
        self.mock_args.update = True
        self.mock_args.delete = False

        mock_update_axes.return_value = (self.df_agresso_axes, "updated")
        # Configurer le mock pour retourner la config N2F
        self.mock_context.get_config_value.side_effect = lambda key: (
            self.mock_n2f_config if key == "n2f" else self.mock_agresso_config
        )

        # Exécution de la fonction
        result = axe_process._perform_sync_actions(
            self.mock_context,
            self.mock_n2f_client,
            "axe123",
            "PROJECTS",
            self.df_agresso_axes,
            self.df_n2f_axes,
            self.df_n2f_companies,
            "projects",
        )

        # Vérifications
        mock_update_axes.assert_called_once()
        mock_reporting.assert_called_once()
        self.assertEqual(len(result), 1)

    @patch("business.process.axe.delete_n2f_axes")
    @patch("business.process.axe.reporting")
    def test_perform_sync_actions_delete_only(self, mock_reporting, mock_delete_axes):
        """Test des actions de synchronisation - suppression uniquement."""
        # Configuration des mocks
        self.mock_args.create = False
        self.mock_args.update = False
        self.mock_args.delete = True

        mock_delete_axes.return_value = (self.df_agresso_axes, "deleted")
        # Configurer le mock pour retourner la config N2F
        self.mock_context.get_config_value.side_effect = lambda key: (
            self.mock_n2f_config if key == "n2f" else self.mock_agresso_config
        )

        # Exécution de la fonction
        result = axe_process._perform_sync_actions(
            self.mock_context,
            self.mock_n2f_client,
            "axe123",
            "PROJECTS",
            self.df_agresso_axes,
            self.df_n2f_axes,
            self.df_n2f_companies,
            "projects",
        )

        # Vérifications
        mock_delete_axes.assert_called_once()
        mock_reporting.assert_called_once()
        self.assertEqual(len(result), 1)

    @patch("business.process.axe.create_n2f_axes")
    @patch("business.process.axe.update_n2f_axes")
    @patch("business.process.axe.delete_n2f_axes")
    @patch("business.process.axe.reporting")
    def test_perform_sync_actions_all_operations(
        self, mock_reporting, mock_delete_axes, mock_update_axes, mock_create_axes
    ):
        """Test des actions de synchronisation - toutes les opérations."""
        # Configuration des mocks
        self.mock_args.create = True
        self.mock_args.update = True
        self.mock_args.delete = True

        mock_create_axes.return_value = (self.df_agresso_axes, "created")
        mock_update_axes.return_value = (self.df_agresso_axes, "updated")
        mock_delete_axes.return_value = (self.df_agresso_axes, "deleted")
        # Configurer le mock pour retourner la config N2F
        self.mock_context.get_config_value.side_effect = lambda key: (
            self.mock_n2f_config if key == "n2f" else self.mock_agresso_config
        )

        # Exécution de la fonction
        result = axe_process._perform_sync_actions(
            self.mock_context,
            self.mock_n2f_client,
            "axe123",
            "PROJECTS",
            self.df_agresso_axes,
            self.df_n2f_axes,
            self.df_n2f_companies,
            "projects",
        )

        # Vérifications
        mock_create_axes.assert_called_once()
        mock_update_axes.assert_called_once()
        mock_delete_axes.assert_called_once()
        self.assertEqual(mock_reporting.call_count, 3)
        self.assertEqual(len(result), 3)

    @patch("business.process.axe.create_n2f_axes")
    @patch("business.process.axe.reporting")
    def test_perform_sync_actions_empty_results(self, mock_reporting, mock_create_axes):
        """Test des actions de synchronisation avec résultats vides."""
        # Configuration des mocks
        self.mock_args.create = True
        self.mock_args.update = False
        self.mock_args.delete = False

        mock_create_axes.return_value = (pd.DataFrame(), "created")
        # Configurer le mock pour retourner la config N2F
        self.mock_context.get_config_value.side_effect = lambda key: (
            self.mock_n2f_config if key == "n2f" else self.mock_agresso_config
        )

        # Exécution de la fonction
        result = axe_process._perform_sync_actions(
            self.mock_context,
            self.mock_n2f_client,
            "axe123",
            "PROJECTS",
            self.df_agresso_axes,
            self.df_n2f_axes,
            self.df_n2f_companies,
            "projects",
        )

        # Vérifications
        mock_create_axes.assert_called_once()
        mock_reporting.assert_called_once()
        self.assertEqual(len(result), 0)  # Aucun résultat ajouté car DataFrame vide

    @patch("business.process.axe._perform_sync_actions")
    @patch("business.process.axe._load_n2f_axes")
    @patch("business.process.axe._load_agresso_axes")
    @patch("business.process.axe._get_scope_from_axe_type")
    @patch("business.process.axe.get_axe_mapping")
    @patch("business.process.axe.N2fApiClient")
    def test_synchronize_projects(
        self,
        mock_n2f_client_class,
        mock_get_axe_mapping,
        mock_get_scope,
        mock_load_agresso,
        mock_load_n2f,
        mock_perform_actions,
    ):
        """Test de synchronisation des projets."""
        # Configuration des mocks
        mock_n2f_client_instance = Mock()
        mock_n2f_client_class.return_value = mock_n2f_client_instance
        mock_n2f_client_instance.get_companies.return_value = self.df_n2f_companies

        mock_get_axe_mapping.return_value = ("PROJECTS", "axe123")
        mock_get_scope.return_value = "projects"
        mock_load_agresso.return_value = self.df_agresso_axes
        mock_load_n2f.return_value = self.df_n2f_axes
        mock_perform_actions.return_value = [self.df_agresso_axes]

        # Exécution de la fonction
        result = axe_process.synchronize_projects(self.mock_context, "test_query.sql")

        # Vérifications
        mock_n2f_client_class.assert_called_once_with(self.mock_context)
        mock_n2f_client_instance.get_companies.assert_called_once()
        mock_get_axe_mapping.assert_called_once_with(
            axe_type=AxeType.PROJECTS,
            n2f_client=mock_n2f_client_instance,
            company_id="uuid1",
        )
        mock_get_scope.assert_called_once_with(AxeType.PROJECTS)
        mock_load_agresso.assert_called_once_with(
            self.mock_context, "test_query.sql", "PROJECTS"
        )
        mock_load_n2f.assert_called_once_with(
            mock_n2f_client_instance, self.df_n2f_companies, "axe123"
        )
        mock_perform_actions.assert_called_once()
        self.assertEqual(len(result), 1)

    @patch("business.process.axe.synchronize")
    def test_synchronize_plates(self, mock_synchronize):
        """Test de synchronisation des plaques."""
        # Configuration du mock
        mock_synchronize.return_value = [self.df_agresso_axes]

        # Exécution de la fonction
        result = axe_process.synchronize_plates(self.mock_context, "test_query.sql")

        # Vérifications
        mock_synchronize.assert_called_once_with(
            context=self.mock_context,
            axe_type=AxeType.PLATES,
            sql_filename="test_query.sql",
        )
        self.assertEqual(len(result), 1)

    @patch("business.process.axe.synchronize")
    def test_synchronize_subposts(self, mock_synchronize):
        """Test de synchronisation des subposts."""
        # Configuration du mock
        mock_synchronize.return_value = [self.df_agresso_axes]

        # Exécution de la fonction
        result = axe_process.synchronize_subposts(self.mock_context, "test_query.sql")

        # Vérifications
        mock_synchronize.assert_called_once_with(
            context=self.mock_context,
            axe_type=AxeType.SUBPOSTS,
            sql_filename="test_query.sql",
        )
        self.assertEqual(len(result), 1)

    @patch("business.process.axe._perform_sync_actions")
    @patch("business.process.axe._load_n2f_axes")
    @patch("business.process.axe._load_agresso_axes")
    @patch("business.process.axe._get_scope_from_axe_type")
    @patch("business.process.axe.get_axe_mapping")
    @patch("business.process.axe.N2fApiClient")
    def test_synchronize_empty_companies(
        self,
        mock_n2f_client_class,
        mock_get_axe_mapping,
        mock_get_scope,
        mock_load_agresso,
        mock_load_n2f,
        mock_perform_actions,
    ):
        """Test de synchronisation avec entreprises vides."""
        # Configuration des mocks
        mock_n2f_client_instance = Mock()
        mock_n2f_client_class.return_value = mock_n2f_client_instance
        mock_n2f_client_instance.get_companies.return_value = pd.DataFrame()

        mock_get_axe_mapping.return_value = ("PROJECTS", "axe123")
        mock_get_scope.return_value = "projects"
        mock_load_agresso.return_value = self.df_agresso_axes
        mock_load_n2f.return_value = self.df_n2f_axes
        mock_perform_actions.return_value = [self.df_agresso_axes]

        # Exécution de la fonction
        result = axe_process.synchronize(
            self.mock_context, AxeType.PROJECTS, "test_query.sql"
        )

        # Vérifications
        mock_get_axe_mapping.assert_called_once_with(
            axe_type=AxeType.PROJECTS,
            n2f_client=mock_n2f_client_instance,
            company_id="",  # UUID vide car pas d'entreprises
        )


if __name__ == "__main__":
    unittest.main()
