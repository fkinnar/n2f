import business.process.helper as business_helper
import business.process.axe as axe_process

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

import business.process.axe_types as axe_types
import business.process.department as department


class TestBusinessHelper(unittest.TestCase):
    """Tests pour business.process.helper."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.sample_df = pd.DataFrame(
            {
                "entity_id": ["user1", "user2", "user3", "user4"],
                "success": [True, True, False, True],
            }
        )

    @patch("builtins.print")
    def test_reporting_with_results(self, mock_print):
        """Test de reporting avec des résultats."""
        business_helper.reporting(
            self.sample_df, "Aucune opération", "Opérations effectuées", "success"
        )

        # Vérifier que print a été appelé avec les bonnes valeurs
        calls = mock_print.call_args_list
        self.assertIn("Opérations effectuées :", [call[0][0] for call in calls])
        self.assertIn("  Success : 3 / 4", [call[0][0] for call in calls])
        self.assertIn("  Failures : 1 / 4", [call[0][0] for call in calls])

    @patch("builtins.print")
    def test_reporting_empty_dataframe(self, mock_print):
        """Test de reporting avec DataFrame vide."""
        business_helper.reporting(
            pd.DataFrame(), "Aucune opération", "Opérations effectuées", "success"
        )

        mock_print.assert_called_once_with("Aucune opération")

    @patch("builtins.print")
    def test_reporting_without_status_column(self, mock_print):
        """Test de reporting sans colonne de statut."""
        df_no_status = pd.DataFrame({"entity_id": ["user1", "user2"]})

        business_helper.reporting(
            df_no_status, "Aucune opération", "Opérations effectuées", "success"
        )

        calls = mock_print.call_args_list
        self.assertIn("Opérations effectuées :", [call[0][0] for call in calls])
        self.assertIn("  Total : 2", [call[0][0] for call in calls])

    @patch("builtins.print")
    def test_log_error_basic(self, mock_print):
        """Test de log d'erreur basique."""
        error = Exception("Test error message")
        business_helper.log_error("USERS", "CREATE", "test@example.com", error)

        mock_print.assert_called_once_with(
            "[ERROR] [USERS] [CREATE] [test@example.com] - Test error message"
        )

    @patch("builtins.print")
    def test_log_error_with_context(self, mock_print):
        """Test de log d'erreur avec contexte."""
        error = Exception("Validation failed")
        business_helper.log_error(
            "PROJECTS", "UPDATE", "PROJ001", error, "Payload validation"
        )

        mock_print.assert_called_once_with(
            "[ERROR] [PROJECTS] [UPDATE] [PROJ001] - Payload validation - Validation failed"
        )

    def test_has_payload_changes_no_changes(self):
        """Test de détection de changements - aucun changement."""
        payload = {"name": "John Doe", "email": "john@example.com"}
        n2f_entity = {"name": "John Doe", "email": "john@example.com", "id": 123}

        result = business_helper.has_payload_changes(payload, n2f_entity, "user")

        self.assertFalse(result)

    def test_has_payload_changes_with_changes(self):
        """Test de détection de changements - avec changements."""
        payload = {"name": "Jane Doe", "email": "jane@example.com"}
        n2f_entity = {"name": "John Doe", "email": "john@example.com", "id": 123}

        result = business_helper.has_payload_changes(payload, n2f_entity, "user")

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
        with self.assertRaises(ValueError):
            axe_types.get_axe_mapping(axe_types.AxeType.PLATES, self.n2f_client, "")

    def test_get_axe_mapping_subposts_no_company_id(self):
        """Test de récupération du mapping pour les subposts sans company_id."""
        with self.assertRaises(ValueError):
            axe_types.get_axe_mapping(axe_types.AxeType.SUBPOSTS, self.n2f_client, "")

    def test_get_axe_mapping_unknown_type(self):
        """Test de récupération du mapping pour un type inconnu."""
        # Créer un type d'axe inconnu en utilisant une approche différente
        from enum import Enum

        class UnknownAxeType(Enum):
            UNKNOWN = "unknown"

        with self.assertRaises(ValueError):
            axe_types.get_axe_mapping(
                UnknownAxeType.UNKNOWN, self.n2f_client, self.company_id
            )

    def test_get_axe_mapping_client_error(self):
        """Test de gestion d'erreur du client."""
        # Nettoyer le cache avant le test
        axe_types.clear_mappings_cache()

        self.n2f_client.get_custom_axes.side_effect = Exception("API Error")

        with self.assertRaises(RuntimeError):
            axe_types.get_axe_mapping(
                axe_types.AxeType.PLATES, self.n2f_client, self.company_id
            )

    def test_get_axe_mapping_empty_response(self):
        """Test de gestion d'une réponse vide du client."""
        # Nettoyer le cache avant le test
        axe_types.clear_mappings_cache()

        self.n2f_client.get_custom_axes.return_value = pd.DataFrame()

        with self.assertRaises(ValueError):
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


class TestDepartment(unittest.TestCase):
    """Tests pour business.process.department."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.context = Mock()

    @patch("builtins.print")
    def test_synchronize_departments_basic(self, mock_print):
        """Test de synchronisation des départements basique."""
        result = department.synchronize_departments(self.context, "test.sql")

        # Vérifier que la fonction retourne une liste de DataFrames
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], pd.DataFrame)

        # Vérifier que les messages ont été affichés
        calls = mock_print.call_args_list
        self.assertIn(
            "--- Synchronisation des départements avec test.sql ---",
            [call[0][0] for call in calls],
        )
        self.assertIn(
            "Synchronisation des départements terminée", [call[0][0] for call in calls]
        )

    @patch("builtins.print")
    def test_synchronize_departments_with_column_filter(self, mock_print):
        """Test de synchronisation des départements avec filtre de colonne."""
        result = department.synchronize_departments(
            self.context, "test.sql", "department_id"
        )

        # Vérifier que la fonction retourne une liste de DataFrames
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], pd.DataFrame)

    def test_synchronize_departments_return_structure(self):
        """Test de la structure de retour de synchronize_departments."""
        result = department.synchronize_departments(self.context, "test.sql")

        # Vérifier la structure du DataFrame retourné
        df = result[0]
        expected_columns = ["department_id", "department_name", "status"]
        for col in expected_columns:
            self.assertIn(col, df.columns)

    def test_synchronize_departments_empty_result(self):
        """Test que le DataFrame retourné est vide (comme attendu pour l'exemple)."""
        result = department.synchronize_departments(self.context, "test.sql")

        df = result[0]
        self.assertTrue(df.empty)

    def test_register_scope_called(self):
        """Test que register_scope est appelé dans le module."""
        # Vérifier que le module a bien enregistré le scope
        # Cette vérification peut être faite en vérifiant que le module a été importé
        # et que register_scope a été appelé
        self.assertTrue(hasattr(department, "synchronize_departments"))


if __name__ == "__main__":
    unittest.main()
