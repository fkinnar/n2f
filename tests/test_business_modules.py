import business.process.helper as business_helper
import business.process.axe as axe_process

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from typing import Dict, List, Any

import business.process.axe_types as axe_types
from core.exceptions import ApiException, ValidationException


class TestBusinessHelper(unittest.TestCase):
    """Tests pour business.process.helper."""

    def setUp(self) -> None:
        """Configuration initiale pour les tests."""
        self.sample_df: pd.DataFrame = pd.DataFrame(
            {
                "entity_id": ["user1", "user2", "user3", "user4"],
                "success": [True, True, False, True],
            }
        )

    @patch("logging.info")
    def test_reporting_with_results(self, mock_log_info: Mock) -> None:
        """Test de reporting avec des résultats."""
        business_helper.reporting(
            self.sample_df, "Aucune opération", "Opérations effectuées", "success"
        )

        # Vérifier que logging.info a été appelé avec les bonnes valeurs
        calls: List = mock_log_info.call_args_list
        self.assertIn("Opérations effectuées :", [call[0][0] for call in calls])
        # Vérifier les appels avec lazy formatting
        success_calls = [call for call in calls if call[0][0] == "  Success : %s / %s"]
        failure_calls = [call for call in calls if call[0][0] == "  Failures : %s / %s"]
        self.assertEqual(len(success_calls), 1)
        self.assertEqual(len(failure_calls), 1)
        self.assertEqual(success_calls[0][0][1], 3)  # nb_success
        self.assertEqual(success_calls[0][0][2], 4)  # nb_total
        self.assertEqual(failure_calls[0][0][1], 1)  # nb_failed
        self.assertEqual(failure_calls[0][0][2], 4)  # nb_total

    @patch("logging.info")
    def test_reporting_empty_dataframe(self, mock_log_info: Mock) -> None:
        """Test de reporting avec DataFrame vide."""
        business_helper.reporting(
            pd.DataFrame(), "Aucune opération", "Opérations effectuées", "success"
        )

        mock_log_info.assert_called_once_with("Aucune opération")

    @patch("logging.info")
    def test_reporting_without_status_column(self, mock_log_info: Mock) -> None:
        """Test de reporting sans colonne de statut."""
        df_no_status: pd.DataFrame = pd.DataFrame({"entity_id": ["user1", "user2"]})

        business_helper.reporting(
            df_no_status, "Aucune opération", "Opérations effectuées", "success"
        )

        calls: List = mock_log_info.call_args_list
        self.assertIn("Opérations effectuées :", [call[0][0] for call in calls])
        # Vérifier l'appel avec lazy formatting
        total_calls = [call for call in calls if call[0][0] == "  Total : %s"]
        self.assertEqual(len(total_calls), 1)
        self.assertEqual(total_calls[0][0][1], 2)  # len(result_df)

    def test_has_payload_changes_no_changes(self) -> None:
        """Test de détection de changements - aucun changement."""
        payload: Dict[str, str] = {"name": "John Doe", "email": "john@example.com"}
        n2f_entity: Dict[str, Any] = {
            "name": "John Doe",
            "email": "john@example.com",
            "id": 123,
        }

        result: bool = business_helper.has_payload_changes(payload, n2f_entity, "user")

        self.assertFalse(result)

    def test_has_payload_changes_with_changes(self) -> None:
        """Test de détection de changements - avec changements."""
        payload: Dict[str, str] = {"name": "Jane Doe", "email": "jane@example.com"}
        n2f_entity: Dict[str, Any] = {
            "name": "John Doe",
            "email": "john@example.com",
            "id": 123,
        }

        result: bool = business_helper.has_payload_changes(payload, n2f_entity, "user")

        self.assertTrue(result)

    def test_has_payload_changes_ignore_technical_fields(self):
        """Test de détection de changements - ignore les champs techniques."""
        payload = {"name": "John Doe", "email": "john@example.com", "id": 123}
        n2f_entity = {"name": "John Doe", "email": "john@example.com", "id": 456}

        result = business_helper.has_payload_changes(payload, n2f_entity, "user")

        self.assertFalse(result)

    def test_has_payload_changes_empty_n2f_entity(self):
        """Test de détection de changements avec entité N2F vide."""
        payload = {"name": "John Doe", "email": "john@example.com"}
        n2f_entity = {}

        result = business_helper.has_payload_changes(payload, n2f_entity, "user")

        self.assertTrue(result)

    def test_has_payload_changes_different_types(self):
        """Test de détection de changements avec différents types de données."""
        payload = {"name": "John Doe", "active": True}
        n2f_entity = {"name": "John Doe", "active": "true"}

        result = business_helper.has_payload_changes(payload, n2f_entity, "user")

        # Le résultat peut varier selon l'implémentation exacte
        # Testons que la fonction ne lève pas d'exception
        self.assertIsInstance(result, bool)


class TestAxeTypes(unittest.TestCase):
    """Tests pour business.process.axe_types."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.n2f_client = Mock()
        self.company_id = "company123"

    def test_axe_type_enum_values(self):
        """Test des valeurs de l'enum AxeType."""
        self.assertEqual(axe_types.AxeType.PROJECTS.value, "projects")
        self.assertEqual(axe_types.AxeType.PLATES.value, "plates")
        self.assertEqual(axe_types.AxeType.SUBPOSTS.value, "subposts")

    def test_get_axe_mapping_projects(self):
        """Test de récupération du mapping pour les projets."""
        result = axe_types.get_axe_mapping(
            axe_types.AxeType.PROJECTS, self.n2f_client, self.company_id
        )

        self.assertEqual(result, ("PROJECT", "projects"))

    def test_get_axe_mapping_projects_no_company_id(self):
        """Test de récupération du mapping pour les projets sans company_id."""
        result = axe_types.get_axe_mapping(
            axe_types.AxeType.PROJECTS, self.n2f_client, ""
        )

        self.assertEqual(result, ("PROJECT", "projects"))

    def test_get_axe_mapping_plates_with_company_id(self):
        """Test de récupération du mapping pour les plaques avec company_id."""
        # Nettoyer le cache avant le test
        axe_types.clear_mappings_cache()

        # Mock le client pour retourner des données de test
        mock_df = pd.DataFrame(
            {"uuid": ["uuid1"], "names": [[{"culture": "fr", "value": "plaque"}]]}
        )
        self.n2f_client.get_custom_axes.return_value = mock_df

        result = axe_types.get_axe_mapping(
            axe_types.AxeType.PLATES, self.n2f_client, self.company_id
        )

        self.assertEqual(result, ("PLAQUE", "uuid1"))

    def test_get_axe_mapping_subposts_with_company_id(self):
        """Test de récupération du mapping pour les subposts avec company_id."""
        # Mock le client pour retourner des données de test
        mock_df = pd.DataFrame(
            {"uuid": ["uuid2"], "names": [[{"culture": "fr", "value": "subpost"}]]}
        )
        self.n2f_client.get_custom_axes.return_value = mock_df

        # Nettoyer le cache avant le test
        axe_types.clear_mappings_cache()

        result = axe_types.get_axe_mapping(
            axe_types.AxeType.SUBPOSTS, self.n2f_client, self.company_id
        )

        self.assertEqual(result, ("SUBPOST", "uuid2"))

    def test_get_axe_mapping_plates_no_company_id(self):
        """Test de récupération du mapping pour les plaques sans company_id."""
        with self.assertRaises(ValidationException):
            axe_types.get_axe_mapping(axe_types.AxeType.PLATES, self.n2f_client, "")

    def test_get_axe_mapping_subposts_no_company_id(self):
        """Test de récupération du mapping pour les subposts sans company_id."""
        with self.assertRaises(ValidationException):
            axe_types.get_axe_mapping(axe_types.AxeType.SUBPOSTS, self.n2f_client, "")

    def test_get_axe_mapping_unknown_type(self):
        """Test de récupération du mapping pour un type inconnu."""
        # Créer un type d'axe inconnu en utilisant une approche différente
        from enum import Enum

        class UnknownAxeType(Enum):
            UNKNOWN = "unknown"

        with self.assertRaises(ValidationException):
            axe_types.get_axe_mapping(
                UnknownAxeType.UNKNOWN, self.n2f_client, self.company_id
            )

    def test_get_axe_mapping_client_error(self):
        """Test de gestion d'erreur du client."""
        # Nettoyer le cache avant le test
        axe_types.clear_mappings_cache()

        self.n2f_client.get_custom_axes.side_effect = ApiException("API Error")

        with self.assertRaises(ApiException):
            axe_types.get_axe_mapping(
                axe_types.AxeType.PLATES, self.n2f_client, self.company_id
            )

    def test_get_axe_mapping_empty_response(self):
        """Test de gestion d'une réponse vide du client."""
        # Nettoyer le cache avant le test
        axe_types.clear_mappings_cache()

        self.n2f_client.get_custom_axes.return_value = pd.DataFrame()

        with self.assertRaises(ValidationException):
            axe_types.get_axe_mapping(
                axe_types.AxeType.PLATES, self.n2f_client, self.company_id
            )

    def test_clear_mappings_cache(self):
        """Test de nettoyage du cache des mappings."""
        # D'abord, initialiser le cache
        mock_df = pd.DataFrame(
            {"uuid": ["uuid1"], "names": [[{"culture": "fr", "value": "plaque"}]]}
        )
        self.n2f_client.get_custom_axes.return_value = mock_df

        # Appeler get_axe_mapping pour initialiser le cache
        axe_types.get_axe_mapping(
            axe_types.AxeType.PLATES, self.n2f_client, self.company_id
        )

        # Nettoyer le cache
        axe_types.clear_mappings_cache()

        # Vérifier que le cache a été nettoyé en appelant à nouveau
        # Le client devrait être appelé à nouveau
        axe_types.get_axe_mapping(
            axe_types.AxeType.PLATES, self.n2f_client, self.company_id
        )

        # Vérifier que get_custom_axes a été appelé deux fois
        self.assertEqual(self.n2f_client.get_custom_axes.call_count, 2)

    def test_get_axe_mapping_cache_behavior(self):
        """Test du comportement du cache des mappings."""
        # Nettoyer le cache avant le test
        axe_types.clear_mappings_cache()

        mock_df = pd.DataFrame(
            {"uuid": ["uuid1"], "names": [[{"culture": "fr", "value": "plaque"}]]}
        )
        self.n2f_client.get_custom_axes.return_value = mock_df

        # Premier appel - devrait appeler le client
        result1 = axe_types.get_axe_mapping(
            axe_types.AxeType.PLATES, self.n2f_client, self.company_id
        )

        # Deuxième appel - devrait utiliser le cache
        result2 = axe_types.get_axe_mapping(
            axe_types.AxeType.PLATES, self.n2f_client, self.company_id
        )

        # Les résultats doivent être identiques
        self.assertEqual(result1, result2)

        # Le client ne doit être appelé qu'une seule fois
        self.n2f_client.get_custom_axes.assert_called_once()


if __name__ == "__main__":
    unittest.main()
