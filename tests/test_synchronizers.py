"""
Tests unitaires pour les synchroniseurs d'entités.

Ce module teste les classes de synchronisation et leurs méthodes
pour la gestion des entités entre Agresso et N2F.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import sys
import os

# Ajout du chemin du projet pour les imports
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
                return {"test": "payload"}
            
            def get_entity_id(self, entity):
                return entity.get("id", "default_id")
            
            def get_agresso_id_column(self):
                return "agresso_id"
            
            def get_n2f_id_column(self):
                return "n2f_id"
            
            def _perform_create_operation(self, entity, payload, df_n2f_companies=None):
                return ApiResult(success=True, message="Created", response_data={"id": "new_id"})
            
            def _perform_update_operation(self, entity, payload, n2f_entity, df_n2f_companies=None):
                return ApiResult(success=True, message="Updated", response_data={"id": "updated_id"})
            
            def _perform_delete_operation(self, entity):
                return ApiResult(success=True, message="Deleted", response_data={"id": "deleted_id"})
        
        self.synchronizer = ConcreteSynchronizer(self.mock_client, self.sandbox, self.scope)

    def test_initialization(self):
        """Test de l'initialisation du synchroniseur."""
        self.assertEqual(self.synchronizer.n2f_client, self.mock_client)
        self.assertEqual(self.synchronizer.sandbox, self.sandbox)
        self.assertEqual(self.synchronizer.scope, self.scope)

    def test_create_entities_empty_data(self):
        """Test de création d'entités avec des données vides."""
        empty_df = pd.DataFrame()
        
        result_df, status_col = self.synchronizer.create_entities(empty_df, empty_df)
        
        self.assertTrue(result_df.empty)
        self.assertEqual(status_col, "created")

    def test_create_entities_success(self):
        """Test de création d'entités avec succès."""
        # Données Agresso avec entités à créer
        df_agresso = pd.DataFrame({
            "agresso_id": ["user1", "user2"],
            "name": ["User 1", "User 2"],
            "email": ["user1@test.com", "user2@test.com"]
        })
        
        # Données N2F vides (aucune entité existante)
        df_n2f = pd.DataFrame()
        
        # Mock des méthodes privées
        with patch.object(self.synchronizer, '_get_entities_to_create', return_value=df_agresso):
            with patch.object(self.synchronizer, 'build_payload', return_value={"test": "payload"}):
                with patch.object(self.synchronizer, '_perform_create_operation', 
                                return_value=ApiResult(success=True, message="Created", response_data={"id": "new_id"})):
                    
                    result_df, status_col = self.synchronizer.create_entities(df_agresso, df_n2f)
                    
                    self.assertFalse(result_df.empty)
                    self.assertEqual(status_col, "created")
                    self.assertTrue(all(result_df[status_col]))

    def test_update_entities_empty_data(self):
        """Test de mise à jour d'entités avec des données vides."""
        empty_df = pd.DataFrame()
        
        result_df, status_col = self.synchronizer.update_entities(empty_df, empty_df)
        
        self.assertTrue(result_df.empty)
        self.assertEqual(status_col, "updated")

    def test_update_entities_success(self):
        """Test de mise à jour d'entités avec succès."""
        # Données Agresso
        df_agresso = pd.DataFrame({
            "agresso_id": ["user1", "user2"],
            "name": ["User 1", "User 2"],
            "email": ["user1@test.com", "user2@test.com"]
        })
        
        # Données N2F avec entités existantes
        df_n2f = pd.DataFrame({
            "n2f_id": ["user1", "user2"],
            "name": ["Old User 1", "Old User 2"],
            "email": ["user1@test.com", "user2@test.com"]
        })
        
        # Mock des méthodes privées
        with patch.object(self.synchronizer, '_get_entities_to_update', return_value=df_agresso):
            with patch.object(self.synchronizer, 'build_payload', return_value={"test": "payload"}):
                with patch.object(self.synchronizer, '_perform_update_operation', 
                                return_value=ApiResult(success=True, message="Updated", response_data={"id": "updated_id"})):
                    
                    result_df, status_col = self.synchronizer.update_entities(df_agresso, df_n2f)
                    
                    self.assertFalse(result_df.empty)
                    self.assertEqual(status_col, "updated")
                    self.assertTrue(all(result_df[status_col]))

    def test_delete_entities_empty_data(self):
        """Test de suppression d'entités avec des données vides."""
        empty_df = pd.DataFrame()
        
        result_df, status_col = self.synchronizer.delete_entities(empty_df, empty_df)
        
        self.assertTrue(result_df.empty)
        self.assertEqual(status_col, "deleted")

    def test_delete_entities_success(self):
        """Test de suppression d'entités avec succès."""
        # Données Agresso vides (aucune entité à supprimer)
        df_agresso = pd.DataFrame()
        
        # Données N2F avec entités à supprimer
        df_n2f = pd.DataFrame({
            "n2f_id": ["user1", "user2"],
            "name": ["User 1", "User 2"],
            "email": ["user1@test.com", "user2@test.com"]
        })
        
        # Mock des méthodes privées
        with patch.object(self.synchronizer, '_get_entities_to_delete', return_value=df_n2f):
            with patch.object(self.synchronizer, '_perform_delete_operation', 
                            return_value=ApiResult(success=True, message="Deleted", response_data={"id": "deleted_id"})):
                
                result_df, status_col = self.synchronizer.delete_entities(df_agresso, df_n2f)
                
                self.assertFalse(result_df.empty)
                self.assertEqual(status_col, "deleted")
                self.assertTrue(all(result_df[status_col]))


class TestUserSynchronizer(unittest.TestCase):
    """Tests pour la classe UserSynchronizer."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.mock_client = Mock()
        self.sandbox = True
        self.synchronizer = UserSynchronizer(self.mock_client, self.sandbox)

    def test_initialization(self):
        """Test de l'initialisation du UserSynchronizer."""
        self.assertEqual(self.synchronizer.n2f_client, self.mock_client)
        self.assertEqual(self.synchronizer.sandbox, self.sandbox)
        self.assertEqual(self.synchronizer.scope, "users")

    def test_build_payload(self):
        """Test de la construction du payload utilisateur."""
        entity = pd.Series({
            "AdresseEmail": "test@example.com",
            "Nom": "Test User",
            "Prenom": "Test"
        })
        
        df_agresso = pd.DataFrame()
        df_n2f = pd.DataFrame()
        
        # Mock de la fonction build_user_payload
        with patch('n2f.process.user.build_user_payload') as mock_build:
            mock_build.return_value = {"email": "test@example.com", "name": "Test User"}
            
            payload = self.synchronizer.build_payload(entity, df_agresso, df_n2f)
            
            mock_build.assert_called_once_with(
                entity, df_agresso, df_n2f, self.mock_client, None, self.sandbox
            )
            self.assertEqual(payload, {"email": "test@example.com", "name": "Test User"})

    def test_get_entity_id(self):
        """Test de l'extraction de l'ID utilisateur."""
        entity = pd.Series({
            "AdresseEmail": "test@example.com",
            "Nom": "Test User"
        })
        
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

    def test_perform_create_operation(self):
        """Test de l'opération de création."""
        entity = pd.Series({"AdresseEmail": "test@example.com"})
        payload = {"email": "test@example.com", "name": "Test User"}
        
        # Mock de la méthode create_user
        self.mock_client.create_user.return_value = ApiResult(success=True, message="Created", response_data={"id": "new_user_id"})
        
        result = self.synchronizer._perform_create_operation(entity, payload)
        
        self.mock_client.create_user.assert_called_once_with(payload)
        self.assertTrue(result.success)

    def test_perform_update_operation(self):
        """Test de l'opération de mise à jour."""
        entity = pd.Series({"AdresseEmail": "test@example.com"})
        payload = {"email": "test@example.com", "name": "Updated User"}
        n2f_entity = {"id": "user_id", "email": "test@example.com"}
        
        # Mock de la méthode update_user
        self.mock_client.update_user.return_value = ApiResult(success=True, message="Updated", response_data={"id": "updated_user_id"})
        
        result = self.synchronizer._perform_update_operation(entity, payload, n2f_entity)
        
        self.mock_client.update_user.assert_called_once_with(payload)
        self.assertTrue(result.success)

    def test_perform_delete_operation(self):
        """Test de l'opération de suppression."""
        entity = pd.Series({"AdresseEmail": "test@example.com"})
        
        # Mock de la méthode delete_user
        self.mock_client.delete_user.return_value = ApiResult(success=True, message="Deleted", response_data={"id": "deleted_user_id"})
        
        result = self.synchronizer._perform_delete_operation(entity)
        
        self.mock_client.delete_user.assert_called_once_with("test@example.com")
        self.assertTrue(result.success)


class TestAxeSynchronizer(unittest.TestCase):
    """Tests pour la classe AxeSynchronizer."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.mock_client = Mock()
        self.sandbox = True
        self.axe_id = "test_axe_id"
        self.scope = "projects"
        self.synchronizer = AxeSynchronizer(self.mock_client, self.sandbox, self.axe_id, self.scope)

    def test_initialization(self):
        """Test de l'initialisation du AxeSynchronizer."""
        self.assertEqual(self.synchronizer.n2f_client, self.mock_client)
        self.assertEqual(self.synchronizer.sandbox, self.sandbox)
        self.assertEqual(self.synchronizer.scope, self.scope)
        self.assertEqual(self.synchronizer.axe_id, self.axe_id)

    def test_build_payload(self):
        """Test de la construction du payload axe."""
        entity = pd.Series({
            "code": "TEST001",
            "name": "Test Project",
            "client": "TEST_CLIENT"
        })
        
        df_agresso = pd.DataFrame()
        df_n2f = pd.DataFrame()
        
        # Mock de la fonction build_axe_payload
        with patch('n2f.process.axe.build_axe_payload') as mock_build:
            mock_build.return_value = {"code": "TEST001", "name": "Test Project"}
            
            payload = self.synchronizer.build_payload(entity, df_agresso, df_n2f)
            
            mock_build.assert_called_once_with(entity, self.sandbox)
            self.assertEqual(payload, {"code": "TEST001", "name": "Test Project"})

    def test_get_entity_id(self):
        """Test de l'extraction de l'ID axe."""
        entity = pd.Series({
            "code": "TEST001",
            "name": "Test Project"
        })
        
        entity_id = self.synchronizer.get_entity_id(entity)
        self.assertEqual(entity_id, "TEST001")

    def test_get_agresso_id_column(self):
        """Test de la colonne ID Agresso."""
        column = self.synchronizer.get_agresso_id_column()
        self.assertEqual(column, "code")

    def test_get_n2f_id_column(self):
        """Test de la colonne ID N2F."""
        column = self.synchronizer.get_n2f_id_column()
        self.assertEqual(column, "code")

    def test_perform_create_operation_success(self):
        """Test de l'opération de création d'axe avec succès."""
        entity = pd.Series({
            "code": "TEST001",
            "name": "Test Project",
            "client": "TEST_CLIENT"
        })
        payload = {"code": "TEST001", "name": "Test Project"}
        df_n2f_companies = pd.DataFrame({
            "code": ["TEST_CLIENT"],
            "id": ["company_id_123"]
        })
        
        # Mock de lookup_company_id
        with patch('n2f.process.user.lookup_company_id') as mock_lookup:
            mock_lookup.return_value = "company_id_123"
            
            # Mock de upsert_axe_value
            self.mock_client.upsert_axe_value.return_value = ApiResult(success=True, message="Created", response_data={"id": "new_axe_id"})
            
            result = self.synchronizer._perform_create_operation(entity, payload, df_n2f_companies)
            
            mock_lookup.assert_called_once_with("TEST_CLIENT", df_n2f_companies, self.sandbox)
            self.mock_client.upsert_axe_value.assert_called_once_with(
                "company_id_123", self.axe_id, payload, "create", self.scope
            )
            self.assertTrue(result.success)

    def test_perform_create_operation_company_not_found(self):
        """Test de l'opération de création d'axe avec entreprise non trouvée."""
        entity = pd.Series({
            "code": "TEST001",
            "name": "Test Project",
            "client": "UNKNOWN_CLIENT"
        })
        payload = {"code": "TEST001", "name": "Test Project"}
        df_n2f_companies = pd.DataFrame({
            "code": ["TEST_CLIENT"],
            "id": ["company_id_123"]
        })
        
        # Mock de lookup_company_id retournant None
        with patch('n2f.process.user.lookup_company_id') as mock_lookup:
            mock_lookup.return_value = None
            
            result = self.synchronizer._perform_create_operation(entity, payload, df_n2f_companies)
            
            mock_lookup.assert_called_once_with("UNKNOWN_CLIENT", df_n2f_companies, self.sandbox)
            self.assertFalse(result.success)
            self.assertIn("Company not found", result.error_details)

    def test_perform_update_operation(self):
        """Test de l'opération de mise à jour d'axe."""
        entity = pd.Series({
            "code": "TEST001",
            "name": "Test Project",
            "client": "TEST_CLIENT"
        })
        payload = {"code": "TEST001", "name": "Updated Project"}
        n2f_entity = {"id": "axe_id", "code": "TEST001"}
        df_n2f_companies = pd.DataFrame({
            "code": ["TEST_CLIENT"],
            "id": ["company_id_123"]
        })
        
        # Mock de lookup_company_id
        with patch('n2f.process.user.lookup_company_id') as mock_lookup:
            mock_lookup.return_value = "company_id_123"
            
            # Mock de upsert_axe_value
            self.mock_client.upsert_axe_value.return_value = ApiResult(success=True, message="Updated", response_data={"id": "updated_axe_id"})
            
            result = self.synchronizer._perform_update_operation(entity, payload, n2f_entity, df_n2f_companies)
            
            mock_lookup.assert_called_once_with("TEST_CLIENT", df_n2f_companies, self.sandbox)
            self.mock_client.upsert_axe_value.assert_called_once_with(
                "company_id_123", self.axe_id, payload, "update", self.scope
            )
            self.assertTrue(result.success)

    def test_perform_delete_operation(self):
        """Test de l'opération de suppression d'axe."""
        entity = pd.Series({
            "code": "TEST001",
            "name": "Test Project",
            "client": "TEST_CLIENT"
        })
        
        # Mock de delete_axe_value pour la suppression
        self.mock_client.delete_axe_value.return_value = ApiResult(success=True, message="Deleted", response_data={"id": "deleted_axe_id"})
        
        # Ajouter company_id à l'entité pour le test
        entity_with_company = entity.copy()
        entity_with_company["company_id"] = "company_id_123"
        
        result = self.synchronizer._perform_delete_operation(entity_with_company)
        
        self.mock_client.delete_axe_value.assert_called_once_with(
            "company_id_123", self.axe_id, "TEST001", self.scope
        )
        self.assertTrue(result.success)


if __name__ == '__main__':
    unittest.main()
