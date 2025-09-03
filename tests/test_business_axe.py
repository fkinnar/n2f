#!/usr/bin/env python3
"""
Tests unitaires pour le module src/business/process/axe.py.

Ce module teste les fonctions de synchronisation des axes.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import sys
import pandas as pd
import numpy as np

# Ajouter le répertoire python au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

# Imports après modification du path
import business.process.axe as axe_process
from business.process.axe_types import AxeType
from core import SyncContext


class TestBusinessAxe(unittest.TestCase):
    """Tests pour le module business.process.axe."""

    def setUp(self):
        """Configuration initiale pour chaque test."""
        # Mock des arguments
        self.mock_args = Mock()
        self.mock_args.create = True
        self.mock_args.update = True
        self.mock_args.delete = True

        # Mock du contexte
        self.mock_context = Mock(spec=SyncContext)
        self.mock_context.get_config_value.return_value = {}
        self.mock_context.args = self.mock_args

        # Mock du client N2F
        self.mock_n2f_client = Mock()

        # Mock des configurations
        self.mock_agresso_config = {"database": "agresso_db"}
        self.mock_n2f_config = {"api": "n2f_api", "sandbox": True}

        # DataFrames de test
        self.df_agresso_axes = pd.DataFrame(
            {
                "code": ["PROJ001", "PROJ002"],
                "name": ["Project 1", "Project 2"],
                "type": ["PROJECTS", "PROJECTS"],
                "description": ["Description 1", "Description 2"],
                "active": [True, True],
            }
        )

        self.df_n2f_axes = pd.DataFrame(
            {
                "code": ["PROJ001"],
                "name": ["Project 1"],
                "type": ["PROJECTS"],
                "description": ["Description 1"],
                "active": [True],
            }
        )

        self.df_n2f_companies = pd.DataFrame(
            {
                "id": ["comp1", "comp2"],
                "name": ["Company 1", "Company 2"],
            }
        )

    def test_get_scope_from_axe_type(self):
        """Test de la fonction _get_scope_from_axe_type."""
        # Test avec PROJECTS
        scope = axe_process._get_scope_from_axe_type(AxeType.PROJECTS)
        self.assertEqual(scope, "projects")

        # Test avec PLATES
        scope = axe_process._get_scope_from_axe_type(AxeType.PLATES)
        self.assertEqual(scope, "plates")

        # Test avec SUBPOSTS
        scope = axe_process._get_scope_from_axe_type(AxeType.SUBPOSTS)
        self.assertEqual(scope, "subposts")

        # Test avec type inconnu (valeur non enum)
        scope = axe_process._get_scope_from_axe_type("INVALID_TYPE")
        self.assertEqual(scope, "unknown")

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
        self.assertEqual(
            mock_reporting.call_count, 3
        )  # Appelé 3 fois pour create, update, delete
        self.assertEqual(len(result), 3)

    @patch("business.process.axe.create_n2f_axes")
    @patch("business.process.axe.update_n2f_axes")
    @patch("business.process.axe.delete_n2f_axes")
    @patch("business.process.axe.reporting")
    def test_perform_sync_actions_no_operations(
        self, mock_reporting, mock_delete_axes, mock_update_axes, mock_create_axes
    ):
        """Test des actions de synchronisation - aucune opération."""
        # Configuration des mocks
        self.mock_args.create = False
        self.mock_args.update = False
        self.mock_args.delete = False

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
        mock_create_axes.assert_not_called()
        mock_update_axes.assert_not_called()
        mock_delete_axes.assert_not_called()
        mock_reporting.assert_not_called()  # Aucune opération = aucun appel reporting
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
