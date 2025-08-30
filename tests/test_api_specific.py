import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

import n2f.api.user as user_api
import n2f.api.company as company_api
import n2f.api.customaxe as customaxe_api
import n2f.api.project as project_api

class TestUserApi(unittest.TestCase):
    """Tests pour n2f.api.user."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.base_url = "https://api.n2f.com"
        self.client_id = "test_client_id"
        self.client_secret = "test_client_secret"
        self.payload = {"mail": "test@example.com", "name": "Test User"}

    @patch('n2f.api.user.retreive')
    def test_get_users_success(self, mock_retreive):
        """Test de récupération réussie d'utilisateurs."""
        mock_response = {
            "response": {
                "data": [
                    {"id": "1", "mail": "user1@example.com"},
                    {"id": "2", "mail": "user2@example.com"}
                ]
            }
        }
        mock_retreive.return_value = mock_response

        result = user_api.get_users(self.base_url, self.client_id, self.client_secret)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["mail"], "user1@example.com")
        mock_retreive.assert_called_once_with("users", self.base_url, self.client_id, self.client_secret, 0, 200, False)

    @patch('n2f.api.user.retreive')
    def test_get_users_with_pagination(self, mock_retreive):
        """Test de récupération d'utilisateurs avec pagination."""
        mock_response = {"response": {"data": []}}
        mock_retreive.return_value = mock_response

        user_api.get_users(self.base_url, self.client_id, self.client_secret, start=50, limit=100)

        mock_retreive.assert_called_once_with("users", self.base_url, self.client_id, self.client_secret, 50, 100, False)

    @patch('n2f.api.user.retreive')
    def test_get_users_simulation_mode(self, mock_retreive):
        """Test de récupération d'utilisateurs en mode simulation."""
        mock_response = {"response": {"data": []}}
        mock_retreive.return_value = mock_response

        result = user_api.get_users(self.base_url, self.client_id, self.client_secret, simulate=True)

        mock_retreive.assert_called_once_with("users", self.base_url, self.client_id, self.client_secret, 0, 200, True)

    @patch('n2f.api.user.retreive')
    def test_get_users_empty_response(self, mock_retreive):
        """Test de récupération d'utilisateurs avec réponse vide."""
        mock_response = {"response": {}}  # Pas de "data"
        mock_retreive.return_value = mock_response

        result = user_api.get_users(self.base_url, self.client_id, self.client_secret)

        self.assertEqual(result, [])

    @patch('n2f.api.user.upsert')
    def test_create_user_success(self, mock_upsert):
        """Test de création d'utilisateur réussie."""
        mock_upsert.return_value = True

        result = user_api.create_user(self.base_url, self.client_id, self.client_secret, self.payload)

        self.assertTrue(result)
        mock_upsert.assert_called_once_with(self.base_url, "/users", self.client_id, self.client_secret, self.payload, False)

    @patch('n2f.api.user.upsert')
    def test_create_user_simulation_mode(self, mock_upsert):
        """Test de création d'utilisateur en mode simulation."""
        mock_upsert.return_value = True

        result = user_api.create_user(self.base_url, self.client_id, self.client_secret, self.payload, simulate=True)

        mock_upsert.assert_called_once_with(self.base_url, "/users", self.client_id, self.client_secret, self.payload, True)

    @patch('n2f.api.user.upsert')
    def test_update_user_success(self, mock_upsert):
        """Test de mise à jour d'utilisateur réussie."""
        mock_upsert.return_value = True

        result = user_api.update_user(self.base_url, self.client_id, self.client_secret, self.payload)

        self.assertTrue(result)
        mock_upsert.assert_called_once_with(self.base_url, "/users", self.client_id, self.client_secret, self.payload, False)

    @patch('n2f.api.user.delete')
    def test_delete_user_success(self, mock_delete):
        """Test de suppression d'utilisateur réussie."""
        mock_delete.return_value = True

        result = user_api.delete_user(self.base_url, self.client_id, self.client_secret, "test@example.com")

        self.assertTrue(result)
        mock_delete.assert_called_once_with(self.base_url, "/users", self.client_id, self.client_secret, "test@example.com", False)

    @patch('n2f.api.user.delete')
    def test_delete_user_simulation_mode(self, mock_delete):
        """Test de suppression d'utilisateur en mode simulation."""
        mock_delete.return_value = True

        result = user_api.delete_user(self.base_url, self.client_id, self.client_secret, "test@example.com", simulate=True)

        mock_delete.assert_called_once_with(self.base_url, "/users", self.client_id, self.client_secret, "test@example.com", True)

class TestCompanyApi(unittest.TestCase):
    """Tests pour n2f.api.company."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.base_url = "https://api.n2f.com"
        self.client_id = "test_client_id"
        self.client_secret = "test_client_secret"

    @patch('n2f.api.company.retreive')
    def test_get_companies_success(self, mock_retreive):
        """Test de récupération réussie d'entreprises."""
        mock_response = {
            "response": {
                "data": [
                    {"id": "1", "name": "Company 1"},
                    {"id": "2", "name": "Company 2"}
                ]
            }
        }
        mock_retreive.return_value = mock_response

        result = company_api.get_companies(self.base_url, self.client_id, self.client_secret)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Company 1")
        mock_retreive.assert_called_once_with("companies", self.base_url, self.client_id, self.client_secret, 0, 200, False)

    @patch('n2f.api.company.retreive')
    def test_get_companies_with_pagination(self, mock_retreive):
        """Test de récupération d'entreprises avec pagination."""
        mock_response = {"response": {"data": []}}
        mock_retreive.return_value = mock_response

        company_api.get_companies(self.base_url, self.client_id, self.client_secret, start=25, limit=50)

        mock_retreive.assert_called_once_with("companies", self.base_url, self.client_id, self.client_secret, 25, 50, False)

    @patch('n2f.api.company.retreive')
    def test_get_companies_simulation_mode(self, mock_retreive):
        """Test de récupération d'entreprises en mode simulation."""
        mock_response = {"response": {"data": []}}
        mock_retreive.return_value = mock_response

        result = company_api.get_companies(self.base_url, self.client_id, self.client_secret, simulate=True)

        mock_retreive.assert_called_once_with("companies", self.base_url, self.client_id, self.client_secret, 0, 200, True)

    @patch('n2f.api.company.retreive')
    def test_get_companies_empty_response(self, mock_retreive):
        """Test de récupération d'entreprises avec réponse vide."""
        mock_response = {"response": {}}  # Pas de "data"
        mock_retreive.return_value = mock_response

        result = company_api.get_companies(self.base_url, self.client_id, self.client_secret)

        self.assertEqual(result, [])

class TestCustomAxeApi(unittest.TestCase):
    """Tests pour n2f.api.customaxe."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.base_url = "https://api.n2f.com"
        self.client_id = "test_client_id"
        self.client_secret = "test_client_secret"
        self.company_id = "company123"
        self.axe_id = "axe456"

    @patch('n2f.api.customaxe.get_access_token')
    @patch('n2f.get_session_get')
    def test_get_customaxes_success(self, mock_get_session, mock_get_token):
        """Test de récupération réussie d'axes personnalisés."""
        mock_get_token.return_value = ("test_token", "2025-12-31T23:59:59Z")
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "data": [
                    {"id": "1", "name": "Axis 1"},
                    {"id": "2", "name": "Axis 2"}
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = customaxe_api.get_customaxes(self.base_url, self.client_id, self.client_secret, self.company_id, 0, 100)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Axis 1")
        mock_session.get.assert_called_once_with(
            f"{self.base_url}/companies/{self.company_id}/axes",
            headers={"Authorization": "Bearer test_token"},
            params={"start": 0, "limit": 100}
        )

    @patch('n2f.api.customaxe.get_access_token')
    @patch('n2f.get_session_get')
    def test_get_customaxes_simulation_mode(self, mock_get_session, mock_get_token):
        """Test de récupération d'axes personnalisés en mode simulation."""
        result = customaxe_api.get_customaxes(self.base_url, self.client_id, self.client_secret, self.company_id, 0, 100, simulate=True)

        self.assertEqual(result, [])
        mock_get_token.assert_not_called()
        mock_get_session.assert_not_called()

    @patch('n2f.api.customaxe.get_access_token')
    @patch('n2f.get_session_get')
    def test_get_customaxes_values_success(self, mock_get_session, mock_get_token):
        """Test de récupération réussie de valeurs d'axe personnalisé."""
        mock_get_token.return_value = ("test_token", "2025-12-31T23:59:59Z")
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "data": [
                    {"code": "VAL1", "name": "Value 1"},
                    {"code": "VAL2", "name": "Value 2"}
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = customaxe_api.get_customaxes_values(self.base_url, self.client_id, self.client_secret, self.company_id, self.axe_id, 0, 100)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["code"], "VAL1")
        mock_session.get.assert_called_once_with(
            f"{self.base_url}/companies/{self.company_id}/axes/{self.axe_id}",
            headers={"Authorization": "Bearer test_token"},
            params={"start": 0, "limit": 100}
        )

    @patch('n2f.api.customaxe.get_access_token')
    @patch('n2f.get_session_get')
    def test_get_customaxes_values_simulation_mode(self, mock_get_session, mock_get_token):
        """Test de récupération de valeurs d'axe en mode simulation."""
        result = customaxe_api.get_customaxes_values(self.base_url, self.client_id, self.client_secret, self.company_id, self.axe_id, 0, 100, simulate=True)

        self.assertEqual(result, [])
        mock_get_token.assert_not_called()
        mock_get_session.assert_not_called()

    @patch('n2f.api.customaxe.get_access_token')
    @patch('n2f.get_session_get')
    def test_get_customaxes_http_error(self, mock_get_session, mock_get_token):
        """Test de gestion d'erreur HTTP pour get_customaxes."""
        mock_get_token.return_value = ("test_token", "2025-12-31T23:59:59Z")
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 404 Not Found")
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        with self.assertRaises(Exception):
            customaxe_api.get_customaxes(self.base_url, self.client_id, self.client_secret, self.company_id, 0, 100)

    @patch('n2f.api.customaxe.get_access_token')
    @patch('n2f.get_session_get')
    def test_get_customaxes_values_http_error(self, mock_get_session, mock_get_token):
        """Test de gestion d'erreur HTTP pour get_customaxes_values."""
        mock_get_token.return_value = ("test_token", "2025-12-31T23:59:59Z")
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 404 Not Found")
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        with self.assertRaises(Exception):
            customaxe_api.get_customaxes_values(self.base_url, self.client_id, self.client_secret, self.company_id, self.axe_id, 0, 100)

class TestProjectApi(unittest.TestCase):
    """Tests pour n2f.api.project."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.base_url = "https://api.n2f.com"
        self.client_id = "test_client_id"
        self.client_secret = "test_client_secret"
        self.company_id = "company123"
        self.payload = {"name": "Test Project", "code": "PROJ001"}

    @patch('n2f.api.project.get_customaxes_values')
    def test_get_projects_success(self, mock_get_customaxes_values):
        """Test de récupération réussie de projets."""
        mock_response = [
            {"id": "1", "name": "Project 1"},
            {"id": "2", "name": "Project 2"}
        ]
        mock_get_customaxes_values.return_value = mock_response

        result = project_api.get_projects(self.base_url, self.client_id, self.client_secret, self.company_id, 0, 100)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Project 1")
        mock_get_customaxes_values.assert_called_once_with(
            self.base_url, self.client_id, self.client_secret, self.company_id, "projects", 0, 100, False
        )

    @patch('n2f.api.project.get_customaxes_values')
    def test_get_projects_with_pagination(self, mock_get_customaxes_values):
        """Test de récupération de projets avec pagination."""
        mock_get_customaxes_values.return_value = []

        project_api.get_projects(self.base_url, self.client_id, self.client_secret, self.company_id, 10, 50)

        mock_get_customaxes_values.assert_called_once_with(
            self.base_url, self.client_id, self.client_secret, self.company_id, "projects", 10, 50, False
        )

    @patch('n2f.api.project.get_customaxes_values')
    def test_get_projects_simulation_mode(self, mock_get_customaxes_values):
        """Test de récupération de projets en mode simulation."""
        mock_get_customaxes_values.return_value = []

        result = project_api.get_projects(self.base_url, self.client_id, self.client_secret, self.company_id, 0, 100, simulate=True)

        mock_get_customaxes_values.assert_called_once_with(
            self.base_url, self.client_id, self.client_secret, self.company_id, "projects", 0, 100, True
        )

    @patch('n2f.api.project.upsert')
    def test_create_project_success(self, mock_upsert):
        """Test de création de projet réussie."""
        mock_upsert.return_value = True

        result = project_api.create_project(self.base_url, self.client_id, self.client_secret, self.company_id, self.payload)

        self.assertTrue(result)
        mock_upsert.assert_called_once_with(
            self.base_url, f"/companies/{self.company_id}/axes/projects", 
            self.client_id, self.client_secret, self.payload, False
        )

    @patch('n2f.api.project.upsert')
    def test_update_project_success(self, mock_upsert):
        """Test de mise à jour de projet réussie."""
        mock_upsert.return_value = True

        result = project_api.update_project(self.base_url, self.client_id, self.client_secret, self.company_id, self.payload)

        self.assertTrue(result)
        mock_upsert.assert_called_once_with(
            self.base_url, f"/companies/{self.company_id}/axes/projects", 
            self.client_id, self.client_secret, self.payload, False
        )

    @patch('n2f.api.project.delete')
    def test_delete_project_success(self, mock_delete):
        """Test de suppression de projet réussie."""
        mock_delete.return_value = True

        result = project_api.delete_project(self.base_url, self.client_id, self.client_secret, self.company_id, "PROJ001")

        self.assertTrue(result)
        mock_delete.assert_called_once_with(
            self.base_url, f"/companies/{self.company_id}/axes/projects/", 
            self.client_id, self.client_secret, "PROJ001", False
        )

if __name__ == '__main__':
    unittest.main()
