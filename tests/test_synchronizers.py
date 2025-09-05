import n2f.api_result
from business.process.base_synchronizer import EntitySynchronizer

"""
Tests unitaires pour les synchronizers.

Ce module teste les fonctionnalités des synchronizers :
- EntitySynchronizer (classe abstraite)
- UserSynchronizer (implémentation concrète)
- AxeSynchronizer (implémentation concrète)
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import tempfile
import sys
import os

# Ajout du chemin du projet pour les imports
from business.process.user_synchronizer import UserSynchronizer
from business.process.axe_synchronizer import AxeSynchronizer
from n2f.api_result import ApiResult
from core.exceptions import SyncException


class TestEntitySynchronizer(unittest.TestCase):
    """Tests pour la classe abstraite EntitySynchronizer."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.mock_n2f_client = Mock()
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
                return ApiResult(success=True, response_data={"id": "new_id"})

            def _perform_update_operation(
                self, entity, payload, n2f_entity, df_n2f_companies=None
            ):
                return ApiResult(success=True, response_data={"id": "updated_id"})

            def _perform_delete_operation(self, entity, df_n2f_companies=None):
                return ApiResult(success=True, response_data={"id": "deleted_id"})

        self.synchronizer = ConcreteSynchronizer(
            self.mock_n2f_client, self.sandbox, self.scope
        )

    def test_initialization(self):
        """Test de l'initialisation du synchronizer."""
        self.assertEqual(self.synchronizer.n2f_client, self.mock_n2f_client)
        self.assertEqual(self.synchronizer.sandbox, self.sandbox)
        self.assertEqual(self.synchronizer.scope, self.scope)

    def test_get_entities_to_create(self):
        """Test de l'identification des entités à créer."""
        # Données de test
        df_agresso = pd.DataFrame(
            {
                "agresso_id": ["user1", "user2", "user3"],
                "name": ["User 1", "User 2", "User 3"],
            }
        )

        df_n2f = pd.DataFrame({"n2f_id": ["user1"], "name": ["User 1"]})

        # Appel de la méthode
        result = self.synchronizer._get_entities_to_create(df_agresso, df_n2f)

        # Vérifications
        self.assertEqual(len(result), 2)  # user2 et user3 doivent être créés
        self.assertIn("user2", result["agresso_id"].values)
        self.assertIn("user3", result["agresso_id"].values)
        self.assertNotIn("user1", result["agresso_id"].values)

    def test_get_entities_to_update(self):
        """Test de l'identification des entités à mettre à jour."""
        # Données de test
        df_agresso = pd.DataFrame(
            {
                "agresso_id": ["user1", "user2"],
                "name": ["User 1 Updated", "User 2"],
            }
        )

        df_n2f = pd.DataFrame(
            {"n2f_id": ["user1", "user2"], "name": ["User 1", "User 2"]}
        )

        # Appel de la méthode
        result = self.synchronizer._get_entities_to_update(df_agresso, df_n2f)

        # Vérifications
        self.assertEqual(
            len(result), 2
        )  # Les deux utilisateurs doivent être mis à jour
        self.assertIn("user1", result["agresso_id"].values)
        self.assertIn("user2", result["agresso_id"].values)

    def test_get_entities_to_delete(self):
        """Test de l'identification des entités à supprimer."""
        # Données de test
        df_agresso = pd.DataFrame({"agresso_id": ["user1"], "name": ["User 1"]})

        df_n2f = pd.DataFrame(
            {
                "n2f_id": ["user1", "user2", "user3"],
                "name": ["User 1", "User 2", "User 3"],
            }
        )

        # Appel de la méthode
        result = self.synchronizer._get_entities_to_delete(df_agresso, df_n2f)

        # Vérifications
        self.assertEqual(len(result), 2)  # user2 et user3 doivent être supprimés
        self.assertIn("user2", result["n2f_id"].values)
        self.assertIn("user3", result["n2f_id"].values)
        self.assertNotIn("user1", result["n2f_id"].values)

    def test_create_entities_empty(self):
        """Test de création d'entités avec des données vides."""
        df_agresso = pd.DataFrame()
        df_n2f = pd.DataFrame()

        result_df, status_col = self.synchronizer.create_entities(df_agresso, df_n2f)

        self.assertTrue(result_df.empty)
        self.assertEqual(status_col, "created")

    def test_create_entities_success(self):
        """Test de création d'entités avec succès."""
        # Données de test
        df_agresso = pd.DataFrame(
            {
                "agresso_id": ["user1", "user2"],
                "name": ["User 1", "User 2"],
            }
        )

        df_n2f = pd.DataFrame({"n2f_id": [], "name": []})

        # Mock de l'opération de création
        with patch.object(
            self.synchronizer, "_perform_create_operation"
        ) as mock_create:
            mock_create.return_value = ApiResult(
                success=True, response_data={"id": "new_id"}
            )

            result_df, status_col = self.synchronizer.create_entities(
                df_agresso, df_n2f
            )

        # Vérifications
        self.assertEqual(len(result_df), 2)
        self.assertEqual(status_col, "created")
        self.assertTrue(result_df[status_col].all())

    def test_create_entities_with_error(self):
        """Test de création d'entités avec erreur."""
        # Données de test
        df_agresso = pd.DataFrame({"agresso_id": ["user1"], "name": ["User 1"]})

        df_n2f = pd.DataFrame({"n2f_id": [], "name": []})

        # Mock de l'opration de cration qui choue
        with patch.object(
            self.synchronizer, "_perform_create_operation"
        ) as mock_create:
            mock_create.side_effect = SyncException("API Error")

            result_df, status_col = self.synchronizer.create_entities(
                df_agresso, df_n2f
            )

        # Vérifications
        self.assertEqual(len(result_df), 1)
        self.assertEqual(status_col, "created")
        self.assertFalse(result_df[status_col].iloc[0])

    def test_update_entities_empty(self):
        """Test de mise à jour d'entités avec des données vides."""
        df_agresso = pd.DataFrame()
        df_n2f = pd.DataFrame()

        result_df, status_col = self.synchronizer.update_entities(df_agresso, df_n2f)

        self.assertTrue(result_df.empty)
        self.assertEqual(status_col, "updated")

    def test_update_entities_success(self):
        """Test de mise à jour d'entités avec succès."""
        # Données de test
        df_agresso = pd.DataFrame({"agresso_id": ["user1"], "name": ["User 1 Updated"]})

        df_n2f = pd.DataFrame({"n2f_id": ["user1"], "name": ["User 1"]})

        # Mock de l'opération de mise à jour
        with patch.object(
            self.synchronizer, "_perform_update_operation"
        ) as mock_update:
            mock_update.return_value = ApiResult(
                success=True, response_data={"id": "updated_id"}
            )

            result_df, status_col = self.synchronizer.update_entities(
                df_agresso, df_n2f
            )

        # Vérifications
        self.assertEqual(len(result_df), 1)
        self.assertEqual(status_col, "updated")
        self.assertTrue(result_df[status_col].all())

    def test_delete_entities_empty(self):
        """Test de suppression d'entités avec des données vides."""
        df_agresso = pd.DataFrame()
        df_n2f = pd.DataFrame()

        result_df, status_col = self.synchronizer.delete_entities(df_agresso, df_n2f)

        self.assertTrue(result_df.empty)
        self.assertEqual(status_col, "deleted")

    def test_delete_entities_success(self):
        """Test de suppression d'entités avec succès."""
        # Données de test
        df_agresso = pd.DataFrame({"agresso_id": ["user1"], "name": ["User 1"]})

        df_n2f = pd.DataFrame(
            {
                "n2f_id": ["user1", "user2"],
                "name": ["User 1", "User 2"],
            }
        )

        # Mock de l'opération de suppression
        with patch.object(
            self.synchronizer, "_perform_delete_operation"
        ) as mock_delete:
            mock_delete.return_value = ApiResult(
                success=True, response_data={"id": "deleted_id"}
            )

            result_df, status_col = self.synchronizer.delete_entities(
                df_agresso, df_n2f
            )

        # Vérifications
        self.assertEqual(len(result_df), 1)  # user2 doit être supprimé
        self.assertEqual(status_col, "deleted")
        self.assertTrue(result_df[status_col].all())

    def test_create_error_result(self):
        """Test de création d'un résultat d'erreur."""
        result = self.synchronizer._create_error_result(
            "CREATE", "test_id", "Test error"
        )

        self.assertIsInstance(result, ApiResult)
        self.assertFalse(result.success)
        self.assertEqual(result.error_details, "Test error")

    def test_get_n2f_entity_not_found(self):
        """Test de _get_n2f_entity quand l'entité n'est pas trouvée."""
        entity = pd.Series({"agresso_id": "user_not_found"})
        n2f_index = {"user1": pd.Series({"n2f_id": "user1"})}
        result = self.synchronizer._get_n2f_entity(entity, n2f_index)
        self.assertTrue(result.empty)


class TestUserSynchronizer(unittest.TestCase):
    """Tests pour la classe UserSynchronizer."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.mock_n2f_client = Mock()
        self.sandbox = True
        self.synchronizer = UserSynchronizer(self.mock_n2f_client, self.sandbox)

    def test_initialization(self):
        """Test de l'initialisation du UserSynchronizer."""
        self.assertEqual(self.synchronizer.n2f_client, self.mock_n2f_client)
        self.assertEqual(self.synchronizer.sandbox, self.sandbox)
        self.assertEqual(self.synchronizer.scope, "users")

    def test_get_entity_id(self):
        """Test de récupération de l'ID de l'entité utilisateur."""
        entity = pd.Series({"AdresseEmail": "test@example.com", "name": "Test User"})
        entity_id = self.synchronizer.get_entity_id(entity)

        self.assertEqual(entity_id, "test@example.com")

    def test_get_agresso_id_column(self):
        """Test de récupération de la colonne d'ID Agresso."""
        column = self.synchronizer.get_agresso_id_column()
        self.assertEqual(column, "AdresseEmail")

    def test_get_n2f_id_column(self):
        """Test de récupération de la colonne d'ID N2F."""
        column = self.synchronizer.get_n2f_id_column()
        self.assertEqual(column, "mail")

    def test_build_payload(self):
        """Test de construction du payload utilisateur."""
        entity = pd.Series({"AdresseEmail": "test@example.com", "name": "Test User"})
        df_agresso = pd.DataFrame({"AdresseEmail": ["test@example.com"]})
        df_n2f = pd.DataFrame({"mail": []})

        with patch("n2f.process.user.build_user_payload") as mock_build:
            mock_build.return_value = {"email": "test@example.com", "name": "Test User"}

            payload = self.synchronizer.build_payload(entity, df_agresso, df_n2f)

        mock_build.assert_called_once_with(
            entity, df_agresso, df_n2f, self.mock_n2f_client, None, self.sandbox
        )
        self.assertEqual(payload, {"email": "test@example.com", "name": "Test User"})

    def test_perform_create_operation(self):
        """Test de l'opération de création d'utilisateur."""
        entity = pd.Series({"AdresseEmail": "test@example.com"})
        payload = {"email": "test@example.com", "name": "Test User"}

        mock_result = ApiResult(success=True, response_data={"id": "new_user_id"})
        self.mock_n2f_client.create_user.return_value = mock_result

        result = self.synchronizer._perform_create_operation(entity, payload)

        self.mock_n2f_client.create_user.assert_called_once_with(payload)
        self.assertEqual(result, mock_result)

    def test_perform_update_operation(self):
        """Test de l'opération de mise à jour d'utilisateur."""
        entity = pd.Series({"AdresseEmail": "test@example.com"})
        payload = {"email": "test@example.com", "name": "Test User Updated"}
        n2f_entity = {"id": "user_id", "mail": "test@example.com"}

        mock_result = ApiResult(success=True, response_data={"id": "updated_user_id"})
        self.mock_n2f_client.update_user.return_value = mock_result

        result = self.synchronizer._perform_update_operation(
            entity, payload, n2f_entity
        )

        self.mock_n2f_client.update_user.assert_called_once_with(payload)
        self.assertEqual(result, mock_result)

    def test_perform_delete_operation(self):
        """Test de l'opération de suppression d'utilisateur."""
        entity = pd.Series({"AdresseEmail": "test@example.com"})

        mock_result = ApiResult(success=True, response_data={"id": "deleted_user_id"})
        self.mock_n2f_client.delete_user.return_value = mock_result

        result = self.synchronizer._perform_delete_operation(entity)

        self.mock_n2f_client.delete_user.assert_called_once_with("test@example.com")
        self.assertEqual(result, mock_result)


class TestAxeSynchronizer(unittest.TestCase):
    """Tests pour la classe AxeSynchronizer."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.mock_n2f_client = Mock()
        self.sandbox = True
        self.axe_id = "test_axe_id"
        self.scope = "projects"
        self.synchronizer = AxeSynchronizer(
            self.mock_n2f_client, self.sandbox, self.axe_id, self.scope
        )

    def test_initialization(self):
        """Test de l'initialisation du AxeSynchronizer."""
        self.assertEqual(self.synchronizer.n2f_client, self.mock_n2f_client)
        self.assertEqual(self.synchronizer.sandbox, self.sandbox)
        self.assertEqual(self.synchronizer.scope, self.scope)
        self.assertEqual(self.synchronizer.axe_id, self.axe_id)

    def test_get_entity_id(self):
        """Test de récupération de l'ID de l'entité axe."""
        entity = pd.Series({"code": "AXE001", "name": "Test Axe"})
        entity_id = self.synchronizer.get_entity_id(entity)

        self.assertEqual(entity_id, "AXE001")

    def test_get_agresso_id_column(self):
        """Test de récupération de la colonne d'ID Agresso."""
        column = self.synchronizer.get_agresso_id_column()
        self.assertEqual(column, "code")

    def test_get_n2f_id_column(self):
        """Test de récupération de la colonne d'ID N2F."""
        column = self.synchronizer.get_n2f_id_column()
        self.assertEqual(column, "code")

    def test_build_payload(self):
        """Test de construction du payload axe."""
        entity = pd.Series({"code": "AXE001", "name": "Test Axe"})
        df_agresso = pd.DataFrame({"code": ["AXE001"]})
        df_n2f = pd.DataFrame({"code": []})

        with patch("n2f.process.axe.build_axe_payload") as mock_build:
            mock_build.return_value = {"code": "AXE001", "name": "Test Axe"}

            payload = self.synchronizer.build_payload(entity, df_agresso, df_n2f)

        mock_build.assert_called_once_with(entity, self.sandbox)
        self.assertEqual(payload, {"code": "AXE001", "name": "Test Axe"})

    def test_perform_create_operation_success(self):
        """Test de l'opération de création d'axe avec succès."""
        entity = pd.Series(
            {"code": "AXE001", "name": "Test Project", "client": "TEST_CLIENT"}
        )
        payload = {"code": "AXE001", "name": "Test Project"}
        df_n2f_companies = pd.DataFrame(
            {"code": ["TEST_CLIENT"], "id": ["company_id_123"]}
        )

        # Mock de lookup_company_id
        with patch("n2f.process.user.lookup_company_id") as mock_lookup:
            mock_lookup.return_value = "company_id_123"

            # Mock de upsert_axe_value
            mock_result = ApiResult(success=True, response_data={"id": "new_axe_id"})
            self.mock_n2f_client.upsert_axe_value.return_value = mock_result

            result = self.synchronizer._perform_create_operation(
                entity, payload, df_n2f_companies
            )

            mock_lookup.assert_called_once_with(
                "TEST_CLIENT", df_n2f_companies, self.sandbox
            )
            self.mock_n2f_client.upsert_axe_value.assert_called_once_with(
                "company_id_123", self.axe_id, payload, "create", self.scope
            )
            self.assertEqual(result, mock_result)

    def test_perform_create_operation_company_not_found(self):
        """Test de l'opération de création d'axe avec entreprise non trouvée."""
        entity = pd.Series(
            {"code": "AXE001", "name": "Test Project", "client": "UNKNOWN_CLIENT"}
        )
        payload = {"code": "AXE001", "name": "Test Project"}
        df_n2f_companies = pd.DataFrame(
            {"code": ["TEST_CLIENT"], "id": ["company_id_123"]}
        )

        # Mock de lookup_company_id retournant None
        with patch("n2f.process.user.lookup_company_id") as mock_lookup:
            mock_lookup.return_value = None

            result = self.synchronizer._perform_create_operation(
                entity, payload, df_n2f_companies
            )

            mock_lookup.assert_called_once_with(
                "UNKNOWN_CLIENT", df_n2f_companies, self.sandbox
            )
            self.assertFalse(result.success)
            self.assertIn("Company not found", result.error_details)

    def test_perform_update_operation_success(self):
        """Test de l'opération de mise à jour d'axe avec succès."""
        entity = pd.Series(
            {"code": "AXE001", "name": "Test Project", "client": "TEST_CLIENT"}
        )
        payload = {"code": "AXE001", "name": "Updated Project"}
        n2f_entity = {"id": "axe_id", "code": "AXE001"}
        df_n2f_companies = pd.DataFrame(
            {"code": ["TEST_CLIENT"], "id": ["company_id_123"]}
        )

        # Mock de lookup_company_id
        with patch("n2f.process.user.lookup_company_id") as mock_lookup:
            mock_lookup.return_value = "company_id_123"

            # Mock de upsert_axe_value
            mock_result = ApiResult(
                success=True, response_data={"id": "updated_axe_id"}
            )
            self.mock_n2f_client.upsert_axe_value.return_value = mock_result

            result = self.synchronizer._perform_update_operation(
                entity, payload, n2f_entity, df_n2f_companies
            )

            mock_lookup.assert_called_once_with(
                "TEST_CLIENT", df_n2f_companies, self.sandbox
            )
            self.mock_n2f_client.upsert_axe_value.assert_called_once_with(
                "company_id_123", self.axe_id, payload, "update", self.scope
            )
            self.assertEqual(result, mock_result)

    def test_perform_update_operation_company_not_found(self):
        """Test de l'opération de mise à jour d'axe avec entreprise non trouvée."""
        entity = pd.Series(
            {"code": "AXE001", "name": "Test Project", "client": "UNKNOWN_CLIENT"}
        )
        payload = {"code": "AXE001", "name": "Updated Project"}
        n2f_entity = {"id": "axe_id", "code": "AXE001"}
        df_n2f_companies = pd.DataFrame(
            {"code": ["TEST_CLIENT"], "id": ["company_id_123"]}
        )

        # Mock de lookup_company_id retournant None
        with patch("n2f.process.user.lookup_company_id") as mock_lookup:
            mock_lookup.return_value = None

            result = self.synchronizer._perform_update_operation(
                entity, payload, n2f_entity, df_n2f_companies
            )

            mock_lookup.assert_called_once_with(
                "UNKNOWN_CLIENT", df_n2f_companies, self.sandbox
            )
            self.assertFalse(result.success)
            self.assertIn("Company not found", result.error_details)

    def test_perform_delete_operation_success(self):
        """Test de l'opération de suppression d'axe avec succès."""
        entity = pd.Series(
            {"code": "AXE001", "name": "Test Project", "company_id": "company_id_123"}
        )

        # Mock de delete_axe_value
        mock_result = ApiResult(success=True, response_data={"id": "deleted_axe_id"})
        self.mock_n2f_client.delete_axe_value.return_value = mock_result

        result = self.synchronizer._perform_delete_operation(entity)

        self.mock_n2f_client.delete_axe_value.assert_called_once_with(
            "company_id_123", self.axe_id, "AXE001", self.scope
        )
        self.assertEqual(result, mock_result)

    def test_perform_delete_operation_company_id_missing(self):
        """Test de l'opération de suppression d'axe sans company_id."""
        entity = pd.Series({"code": "AXE001", "name": "Test Project"})

        result = self.synchronizer._perform_delete_operation(entity)

        self.assertFalse(result.success)
        self.assertIn("Company ID not found", result.error_details)


if __name__ == "__main__":
    unittest.main()
