"""
Tests unitaires pour les synchroniseurs d'entités.
"""

import unittest
import sys
import os
import pandas as pd
from unittest.mock import Mock, patch, MagicMock

# Ajouter le répertoire python au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from business.process.base_synchronizer import EntitySynchronizer
from business.process.user_synchronizer import UserSynchronizer
from business.process.axe_synchronizer import AxeSynchronizer
from n2f.api_result import ApiResult


class TestEntitySynchronizer(unittest.TestCase):
    """Tests pour la classe abstraite EntitySynchronizer."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.mock_client = Mock()
        self.sandbox = True
        self.scope = "test_scope"
        
        # Créer une classe concrète pour tester la classe abstraite
        class ConcreteSynchronizer(EntitySynchronizer):
            def build_payload(self, entity, df_agresso, df_n2f, df_n2f_companies=None):
                return {"id": entity.get("id"), "name": entity.get("name")}
            
            def get_entity_id(self, entity):
                return entity.get("id")
            
            def get_agresso_id_column(self):
                return "id"
            
            def get_n2f_id_column(self):
                return "id"
            
            def _perform_create_operation(self, entity, payload, df_n2f_companies=None):
                return ApiResult.success_result("Created", action_type="create", object_id=entity.get("id"))
            
            def _perform_update_operation(self, entity, payload, n2f_entity, df_n2f_companies=None):
                return ApiResult.success_result("Updated", action_type="update", object_id=entity.get("id"))
            
            def _perform_delete_operation(self, entity, df_n2f_companies=None):
                return ApiResult.success_result("Deleted", action_type="delete", object_id=entity.get("id"))
        
        self.synchronizer = ConcreteSynchronizer(self.mock_client, self.sandbox, self.scope)

    def test_initialization(self):
        """Test de l'initialisation du synchroniseur."""
        self.assertEqual(self.synchronizer.n2f_client, self.mock_client)
        self.assertEqual(self.synchronizer.sandbox, self.sandbox)
        self.assertEqual(self.synchronizer.scope, self.scope)

    def test_create_entities_empty_data(self):
        """Test de création d'entités avec des données vides."""
        df_agresso = pd.DataFrame()
        df_n2f = pd.DataFrame()
        
        result_df, summary = self.synchronizer.create_entities(df_agresso, df_n2f)
        
        self.assertTrue(result_df.empty)
        self.assertIn("No entities to create", summary)

    def test_create_entities_success(self):
        """Test de création d'entités avec succès."""
        df_agresso = pd.DataFrame([
            {"id": "1", "name": "User 1"},
            {"id": "2", "name": "User 2"}
        ])
        df_n2f = pd.DataFrame()  # Pas d'entités existantes
        
        result_df, summary = self.synchronizer.create_entities(df_agresso, df_n2f)
        
        self.assertEqual(len(result_df), 2)
        self.assertIn("Success: 2", summary)
        self.assertIn("Failures: 0", summary)

    def test_update_entities_empty_data(self):
        """Test de mise à jour d'entités avec des données vides."""
        df_agresso = pd.DataFrame()
        df_n2f = pd.DataFrame()
        
        result_df, summary = self.synchronizer.update_entities(df_agresso, df_n2f)
        
        self.assertTrue(result_df.empty)
        self.assertIn("No entities to update", summary)

    def test_update_entities_success(self):
        """Test de mise à jour d'entités avec succès."""
        df_agresso = pd.DataFrame([
            {"id": "1", "name": "User 1 Updated"},
            {"id": "2", "name": "User 2 Updated"}
        ])
        df_n2f = pd.DataFrame([
            {"id": "1", "name": "User 1"},
            {"id": "2", "name": "User 2"}
        ])
        
        result_df, summary = self.synchronizer.update_entities(df_agresso, df_n2f)
        
        self.assertEqual(len(result_df), 2)
        self.assertIn("Success: 2", summary)
        self.assertIn("Failures: 0", summary)

    def test_delete_entities_empty_data(self):
        """Test de suppression d'entités avec des données vides."""
        df_agresso = pd.DataFrame()
        df_n2f = pd.DataFrame()
        
        result_df, summary = self.synchronizer.delete_entities(df_agresso, df_n2f)
        
        self.assertTrue(result_df.empty)
        self.assertIn("No entities to delete", summary)

    def test_delete_entities_success(self):
        """Test de suppression d'entités avec succès."""
        df_agresso = pd.DataFrame()  # Pas d'entités dans Agresso
        df_n2f = pd.DataFrame([
            {"id": "1", "name": "User 1"},
            {"id": "2", "name": "User 2"}
        ])
        
        result_df, summary = self.synchronizer.delete_entities(df_agresso, df_n2f)
        
        self.assertEqual(len(result_df), 2)
        self.assertIn("Success: 2", summary)
        self.assertIn("Failures: 0", summary)


class TestUserSynchronizer(unittest.TestCase):
    """Tests pour UserSynchronizer."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.mock_client = Mock()
        self.sandbox = True
        self.synchronizer = UserSynchronizer(self.mock_client, self.sandbox)

    def test_initialization(self):
        """Test de l'initialisation du UserSynchronizer."""
        self.assertEqual(self.synchronizer.scope, "users")
        self.assertEqual(self.synchronizer.sandbox, self.sandbox)

    def test_get_entity_id(self):
        """Test de l'extraction de l'ID utilisateur."""
        entity = pd.Series({"AdresseEmail": "test@example.com", "Nom": "Test User"})
        entity_id = self.synchronizer.get_entity_id(entity)
        self.assertEqual(entity_id, "test@example.com")

    def test_get_agresso_id_column(self):
        """Test de la colonne ID Agresso."""
        column = self.synchronizer.get_agresso_id_column()
        self.assertEqual(column, "AdresseEmail")

    def test_get_n2f_id_column(self):
        """Test de la colonne ID N2F."""
        column = self.synchronizer.get_n2f_id_column()
        self.assertEqual(column, "mail")

    @patch('business.process.user_synchronizer.build_user_payload')
    def test_build_payload(self, mock_build_payload):
        """Test de la construction du payload utilisateur."""
        entity = pd.Series({"AdresseEmail": "test@example.com", "Nom": "Test User"})
        df_agresso = pd.DataFrame()
        df_n2f = pd.DataFrame()
        
        expected_payload = {"mail": "test@example.com", "firstname": "Test", "lastname": "User"}
        mock_build_payload.return_value = expected_payload
        
        payload = self.synchronizer.build_payload(entity, df_agresso, df_n2f)
        
        self.assertEqual(payload, expected_payload)
        mock_build_payload.assert_called_once_with(
            entity, df_agresso, df_n2f, self.mock_client, None, self.sandbox
        )

    def test_perform_create_operation(self):
        """Test de l'opération de création."""
        entity = pd.Series({"AdresseEmail": "test@example.com"})
        payload = {"mail": "test@example.com", "firstname": "Test", "lastname": "User"}
        
        expected_result = ApiResult.success_result("User created")
        self.mock_client.create_user.return_value = expected_result
        
        result = self.synchronizer._perform_create_operation(entity, payload)
        
        self.assertEqual(result, expected_result)
        self.mock_client.create_user.assert_called_once_with(payload)

    def test_perform_update_operation(self):
        """Test de l'opération de mise à jour."""
        entity = pd.Series({"AdresseEmail": "test@example.com"})
        payload = {"mail": "test@example.com", "firstname": "Test", "lastname": "User"}
        n2f_entity = {"mail": "test@example.com", "firstname": "Old", "lastname": "Name"}
        
        expected_result = ApiResult.success_result("User updated")
        self.mock_client.update_user.return_value = expected_result
        
        result = self.synchronizer._perform_update_operation(entity, payload, n2f_entity)
        
        self.assertEqual(result, expected_result)
        self.mock_client.update_user.assert_called_once_with(payload)

    def test_perform_delete_operation(self):
        """Test de l'opération de suppression."""
        entity = pd.Series({"AdresseEmail": "test@example.com"})
        
        expected_result = ApiResult.success_result("User deleted")
        self.mock_client.delete_user.return_value = expected_result
        
        result = self.synchronizer._perform_delete_operation(entity)
        
        self.assertEqual(result, expected_result)
        self.mock_client.delete_user.assert_called_once_with("test@example.com")


class TestAxeSynchronizer(unittest.TestCase):
    """Tests pour AxeSynchronizer."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.mock_client = Mock()
        self.sandbox = True
        self.synchronizer = AxeSynchronizer(self.mock_client, self.sandbox, "projects")

    def test_initialization(self):
        """Test de l'initialisation du AxeSynchronizer."""
        self.assertEqual(self.synchronizer.scope, "projects")
        self.assertEqual(self.synchronizer.sandbox, self.sandbox)

    def test_get_entity_id(self):
        """Test de l'extraction de l'ID axe."""
        entity = pd.Series({"CodeAxe": "PROJ001", "LibelleAxe": "Project 1"})
        entity_id = self.synchronizer.get_entity_id(entity)
        self.assertEqual(entity_id, "PROJ001")

    def test_get_agresso_id_column(self):
        """Test de la colonne ID Agresso."""
        column = self.synchronizer.get_agresso_id_column()
        self.assertEqual(column, "CodeAxe")

    def test_get_n2f_id_column(self):
        """Test de la colonne ID N2F."""
        column = self.synchronizer.get_n2f_id_column()
        self.assertEqual(column, "code")

    @patch('business.process.axe_synchronizer.build_axe_payload')
    def test_build_payload(self, mock_build_payload):
        """Test de la construction du payload axe."""
        entity = pd.Series({"CodeAxe": "PROJ001", "LibelleAxe": "Project 1"})
        df_agresso = pd.DataFrame()
        df_n2f = pd.DataFrame()
        
        expected_payload = {"code": "PROJ001", "label": "Project 1"}
        mock_build_payload.return_value = expected_payload
        
        payload = self.synchronizer.build_payload(entity, df_agresso, df_n2f)
        
        self.assertEqual(payload, expected_payload)
        mock_build_payload.assert_called_once_with(
            entity, df_agresso, df_n2f, self.mock_client, None, self.sandbox
        )

    def test_perform_create_operation(self):
        """Test de l'opération de création d'axe."""
        entity = pd.Series({"CodeAxe": "PROJ001"})
        payload = {"code": "PROJ001", "label": "Project 1"}
        
        expected_result = ApiResult.success_result("Axe created")
        self.mock_client.upsert_axe_value.return_value = expected_result
        
        result = self.synchronizer._perform_create_operation(entity, payload)
        
        self.assertEqual(result, expected_result)
        self.mock_client.upsert_axe_value.assert_called_once_with(
            "company_id", "axe_id", payload, "create", "projects"
        )

    def test_perform_update_operation(self):
        """Test de l'opération de mise à jour d'axe."""
        entity = pd.Series({"CodeAxe": "PROJ001"})
        payload = {"code": "PROJ001", "label": "Project 1 Updated"}
        n2f_entity = {"code": "PROJ001", "label": "Project 1"}
        
        expected_result = ApiResult.success_result("Axe updated")
        self.mock_client.upsert_axe_value.return_value = expected_result
        
        result = self.synchronizer._perform_update_operation(entity, payload, n2f_entity)
        
        self.assertEqual(result, expected_result)
        self.mock_client.upsert_axe_value.assert_called_once_with(
            "company_id", "axe_id", payload, "update", "projects"
        )

    def test_perform_delete_operation(self):
        """Test de l'opération de suppression d'axe."""
        entity = pd.Series({"CodeAxe": "PROJ001"})
        
        expected_result = ApiResult.success_result("Axe deleted")
        self.mock_client.upsert_axe_value.return_value = expected_result
        
        result = self.synchronizer._perform_delete_operation(entity)
        
        self.assertEqual(result, expected_result)
        self.mock_client.upsert_axe_value.assert_called_once_with(
            "company_id", "axe_id", {}, "delete", "projects"
        )


if __name__ == '__main__':
    unittest.main()
