import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

import n2f.api.base as base_api


class TestRetrieve(unittest.TestCase):
    """Tests pour la fonction retreive."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.entity = "users"
        self.base_url = "https://api.n2f.com"
        self.client_id = "test_client_id"
        self.client_secret = "test_client_secret"

        # Mock response pour les tests
        self.mock_response = Mock()
        self.mock_response.json.return_value = {
            "response": [{"id": 1, "name": "User 1"}, {"id": 2, "name": "User 2"}]
        }

    def test_retreive_simulation_mode(self):
        """Test du mode simulation."""
        result = base_api.retreive(
            self.entity,
            self.base_url,
            self.client_id,
            self.client_secret,
            simulate=True,
        )

        self.assertEqual(result, [])

    @patch("n2f.api.base.get_access_token")
    @patch("n2f.get_session_get")
    def test_retreive_success(self, mock_get_session, mock_get_token):
        """Test de récupération réussie d'entités."""
        # Configuration des mocks
        mock_get_token.return_value = ("test_token", "2025-08-20T09:54:35.8185075Z")
        mock_session = Mock()
        mock_session.get.return_value = self.mock_response
        mock_get_session.return_value = mock_session

        result = base_api.retreive(
            self.entity, self.base_url, self.client_id, self.client_secret
        )

        # Vérifications
        expected_response = {
            "response": [{"id": 1, "name": "User 1"}, {"id": 2, "name": "User 2"}]
        }
        self.assertEqual(result, expected_response)

        # Vérifie l'appel au token
        mock_get_token.assert_called_once_with(
            self.base_url, self.client_id, self.client_secret, simulate=False
        )

        # Vérifie l'appel à l'API
        mock_session.get.assert_called_once_with(
            "https://api.n2f.com/users",
            headers={"Authorization": "Bearer test_token"},
            params={"start": 0, "limit": 200},
        )

    @patch("n2f.api.base.get_access_token")
    @patch("n2f.get_session_get")
    def test_retreive_with_pagination(self, mock_get_session, mock_get_token):
        """Test de récupération avec pagination personnalisée."""
        mock_get_token.return_value = ("test_token", "2025-08-20T09:54:35.8185075Z")
        mock_session = Mock()
        mock_session.get.return_value = self.mock_response
        mock_get_session.return_value = mock_session

        result = base_api.retreive(
            "companies",
            self.base_url,
            self.client_id,
            self.client_secret,
            start=50,
            limit=100,
        )

        # Vérifie l'appel à l'API avec les bons paramètres
        mock_session.get.assert_called_once_with(
            "https://api.n2f.com/companies",
            headers={"Authorization": "Bearer test_token"},
            params={"start": 50, "limit": 100},
        )

    @patch("n2f.api.base.get_access_token")
    @patch("n2f.get_session_get")
    def test_retreive_http_error(self, mock_get_session, mock_get_token):
        """Test de gestion d'erreur HTTP."""
        mock_get_token.return_value = ("test_token", "2025-08-20T09:54:35.8185075Z")
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 404 Not Found")
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session

        with self.assertRaises(Exception):
            base_api.retreive(
                self.entity, self.base_url, self.client_id, self.client_secret
            )


class TestUpsert(unittest.TestCase):
    """Tests pour la fonction upsert."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.base_url = "https://api.n2f.com"
        self.endpoint = "/users"
        self.client_id = "test_client_id"
        self.client_secret = "test_client_secret"
        self.payload = {"name": "Test User", "email": "test@example.com"}

    def test_upsert_simulation_mode(self):
        """Test du mode simulation."""
        result = base_api.upsert(
            self.base_url,
            self.endpoint,
            self.client_id,
            self.client_secret,
            self.payload,
            simulate=True,
        )

        self.assertEqual(result, False)

    @patch("n2f.api.base.get_access_token")
    @patch("n2f.get_session_write")
    def test_upsert_success(self, mock_get_session, mock_get_token):
        """Test d'upsert réussi."""
        mock_get_token.return_value = ("test_token", "2025-08-20T09:54:35.8185075Z")
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 201
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = base_api.upsert(
            self.base_url,
            self.endpoint,
            self.client_id,
            self.client_secret,
            self.payload,
        )

        # Vérifications
        self.assertTrue(result)

        # Vérifie l'appel au token
        mock_get_token.assert_called_once_with(
            self.base_url, self.client_id, self.client_secret, simulate=False
        )

        # Vérifie l'appel à l'API
        mock_session.post.assert_called_once_with(
            "https://api.n2f.com/users",
            headers={
                "Authorization": "Bearer test_token",
                "Content-Type": "application/json",
            },
            json=self.payload,
        )

    @patch("n2f.api.base.get_access_token")
    @patch("n2f.get_session_write")
    def test_upsert_different_status_codes(self, mock_get_session, mock_get_token):
        """Test d'upsert avec différents codes de statut."""
        mock_get_token.return_value = ("test_token", "2025-08-20T09:54:35.8185075Z")
        mock_session = Mock()
        mock_get_session.return_value = mock_session

        # Test des codes de succès
        success_codes = [200, 201, 204, 299]
        for status_code in success_codes:
            with self.subTest(status_code=status_code):
                mock_response = Mock()
                mock_response.status_code = status_code
                mock_session.post.return_value = mock_response

                result = base_api.upsert(
                    self.base_url,
                    self.endpoint,
                    self.client_id,
                    self.client_secret,
                    self.payload,
                )

                self.assertTrue(result)

        # Test des codes d'échec
        failure_codes = [400, 401, 404, 500]
        for status_code in failure_codes:
            with self.subTest(status_code=status_code):
                mock_response = Mock()
                mock_response.status_code = status_code
                mock_session.post.return_value = mock_response

                result = base_api.upsert(
                    self.base_url,
                    self.endpoint,
                    self.client_id,
                    self.client_secret,
                    self.payload,
                )

                self.assertFalse(result)

    @patch("n2f.api.base.get_access_token")
    @patch("n2f.get_session_write")
    def test_upsert_different_endpoints(self, mock_get_session, mock_get_token):
        """Test d'upsert sur différents endpoints."""
        mock_get_token.return_value = ("test_token", "2025-08-20T09:54:35.8185075Z")
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        endpoints = ["/users", "/companies", "/projects", "/customaxes"]

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                result = base_api.upsert(
                    self.base_url,
                    endpoint,
                    self.client_id,
                    self.client_secret,
                    self.payload,
                )

                self.assertTrue(result)

                # Vérifie que l'URL est correcte
                expected_url = f"https://api.n2f.com{endpoint}"
                mock_session.post.assert_called_with(
                    expected_url,
                    headers={
                        "Authorization": "Bearer test_token",
                        "Content-Type": "application/json",
                    },
                    json=self.payload,
                )


class TestDelete(unittest.TestCase):
    """Tests pour la fonction delete."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.base_url = "https://api.n2f.com"
        self.endpoint = "users"
        self.client_id = "test_client_id"
        self.client_secret = "test_client_secret"
        self.id = "test@example.com"

    def test_delete_simulation_mode(self):
        """Test du mode simulation."""
        result = base_api.delete(
            self.base_url,
            self.endpoint,
            self.client_id,
            self.client_secret,
            self.id,
            simulate=True,
        )

        self.assertEqual(result, False)

    @patch("n2f.api.base.get_access_token")
    @patch("n2f.get_session_write")
    def test_delete_success(self, mock_get_session, mock_get_token):
        """Test de suppression réussie."""
        mock_get_token.return_value = ("test_token", "2025-08-20T09:54:35.8185075Z")
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.delete.return_value = mock_response
        mock_get_session.return_value = mock_session

        result = base_api.delete(
            self.base_url, self.endpoint, self.client_id, self.client_secret, self.id
        )

        # Vérifications
        self.assertTrue(result)

        # Vérifie l'appel au token
        mock_get_token.assert_called_once_with(
            self.base_url, self.client_id, self.client_secret, simulate=False
        )

        # Vérifie l'appel à l'API
        mock_session.delete.assert_called_once_with(
            "https://api.n2f.com/users/test@example.com",
            headers={"Authorization": "Bearer test_token"},
        )

    @patch("n2f.api.base.get_access_token")
    @patch("n2f.get_session_write")
    def test_delete_different_status_codes(self, mock_get_session, mock_get_token):
        """Test de suppression avec différents codes de statut."""
        mock_get_token.return_value = ("test_token", "2025-08-20T09:54:35.8185075Z")
        mock_session = Mock()
        mock_get_session.return_value = mock_session

        # Test des codes de succès
        success_codes = [200, 204, 299]
        for status_code in success_codes:
            with self.subTest(status_code=status_code):
                mock_response = Mock()
                mock_response.status_code = status_code
                mock_session.delete.return_value = mock_response

                result = base_api.delete(
                    self.base_url,
                    self.endpoint,
                    self.client_id,
                    self.client_secret,
                    self.id,
                )

                self.assertTrue(result)

        # Test des codes d'échec
        failure_codes = [400, 401, 404, 500]
        for status_code in failure_codes:
            with self.subTest(status_code=status_code):
                mock_response = Mock()
                mock_response.status_code = status_code
                mock_session.delete.return_value = mock_response

                result = base_api.delete(
                    self.base_url,
                    self.endpoint,
                    self.client_id,
                    self.client_secret,
                    self.id,
                )

                self.assertFalse(result)

    @patch("n2f.api.base.get_access_token")
    @patch("n2f.get_session_write")
    def test_delete_different_identifiers(self, mock_get_session, mock_get_token):
        """Test de suppression avec différents types d'identifiants."""
        mock_get_token.return_value = ("test_token", "2025-08-20T09:54:35.8185075Z")
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.delete.return_value = mock_response
        mock_get_session.return_value = mock_session

        test_cases = [
            ("users", "test@example.com"),
            ("companies", "company123"),
            ("projects", "proj456"),
            ("customaxes", "axe789"),
        ]

        for endpoint, identifier in test_cases:
            with self.subTest(endpoint=endpoint, identifier=identifier):
                result = base_api.delete(
                    self.base_url,
                    endpoint,
                    self.client_id,
                    self.client_secret,
                    identifier,
                )

                self.assertTrue(result)

                # Vérifie que l'URL est correcte
                expected_url = f"https://api.n2f.com/{endpoint}/{identifier}"
                mock_session.delete.assert_called_with(
                    expected_url, headers={"Authorization": "Bearer test_token"}
                )


if __name__ == "__main__":
    unittest.main()
