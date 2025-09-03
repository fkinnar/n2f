import n2f.client
import n2f.api_result
from core import SyncContext

import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

from n2f.client import N2fApiClient
from n2f.api_result import ApiResult


class TestN2fApiClient(unittest.TestCase):
    """Tests unitaires pour N2fApiClient."""

    def setUp(self) -> None:
        """Configure l'environnement de test."""
        # Mock du contexte
        self.mock_context: Mock = Mock(spec=SyncContext)
        self.mock_context.client_id = "test_client_id"
        self.mock_context.client_secret = "test_client_secret"

        # Mock de la configuration N2F
        self.mock_n2f_config: Mock = Mock()
        self.mock_n2f_config.base_urls = "https://api.n2f.test"
        self.mock_n2f_config.simulate = False

        # Configuration du mock context
        self.mock_context.get_config_value.return_value = self.mock_n2f_config

        # Création du client
        self.client: N2fApiClient = N2fApiClient(self.mock_context)

    def test_init_with_valid_context(self) -> None:
        """Test l'initialisation avec un contexte valide."""
        self.assertEqual(self.client.base_url, "https://api.n2f.test")
        self.assertEqual(self.client.client_id, "test_client_id")
        self.assertEqual(self.client.client_secret, "test_client_secret")
        self.assertFalse(self.client.simulate)
        self.assertIsNone(self.client._access_token)

    def test_init_with_simulation_mode(self) -> None:
        """Test l'initialisation en mode simulation."""
        self.mock_n2f_config.simulate = True
        client: N2fApiClient = N2fApiClient(self.mock_context)
        self.assertTrue(client.simulate)

    def test_init_with_dict_config_format(self) -> None:
        """Test l'initialisation avec l'ancien format de configuration (dict)."""
        # Mock de l'ancien format
        dict_config: dict = {"base_urls": "https://api.n2f.old", "simulate": True}
        self.mock_context.get_config_value.return_value = dict_config

        client: N2fApiClient = N2fApiClient(self.mock_context)
        self.assertEqual(client.base_url, "https://api.n2f.old")
        self.assertTrue(client.simulate)

    @patch("n2f.client.get_access_token")
    def test_get_token_success(self, mock_get_token: Mock) -> None:
        """Test la récupération réussie d'un token."""
        mock_get_token.return_value = ("test_token", "2025-12-31T23:59:59Z")

        token: str = self.client._get_token()

        self.assertEqual(token, "test_token")
        mock_get_token.assert_called_once_with(
            "https://api.n2f.test",
            "test_client_id",
            "test_client_secret",
            simulate=False,
        )

    @patch("n2f.client.get_access_token")
    def test_get_token_cached(self, mock_get_token: Mock) -> None:
        """Test que le token est mis en cache après la première récupération."""
        mock_get_token.return_value = ("test_token", "2025-12-31T23:59:59Z")

        # Premier appel
        token1: str = self.client._get_token()
        # Deuxième appel
        token2: str = self.client._get_token()

        self.assertEqual(token1, token2)
        # get_access_token ne doit être appelé qu'une seule fois
        mock_get_token.assert_called_once()

    @patch("n2f.client.get_access_token")
    def test_get_token_simulation_mode(self, mock_get_token: Mock) -> None:
        """Test la récupération de token en mode simulation."""
        self.client.simulate = True
        mock_get_token.return_value = ("", "")

        token: str = self.client._get_token()

        self.assertEqual(token, "")
        mock_get_token.assert_called_once_with(
            "https://api.n2f.test",
            "test_client_id",
            "test_client_secret",
            simulate=True,
        )

    @patch("n2f.client.n2f.get_session_get")
    @patch("n2f.client.get_access_token")
    def test_request_success(self, mock_get_token: Mock, mock_session: Mock) -> None:
        """Test une requête API réussie."""
        # Mock du token
        mock_get_token.return_value = ("test_token", "2025-12-31T23:59:59Z")

        # Mock de la réponse
        mock_response: Mock = Mock()
        mock_response.json.return_value = {
            "response": {
                "data": [
                    {"id": "1", "name": "Test User"},
                    {"id": "2", "name": "Test User 2"},
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_session.return_value.get.return_value = mock_response

        result: List[Dict[str, str]] = self.client._request("users", 0, 100)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "1")
        self.assertEqual(result[1]["name"], "Test User 2")

        # Vérification de l'appel API
        mock_session.return_value.get.assert_called_once_with(
            "https://api.n2f.test/users",
            headers={"Authorization": "Bearer test_token"},
            params={"start": 0, "limit": 100},
        )

    @patch("n2f.client.n2f.get_session_get")
    @patch("n2f.client.get_access_token")
    def test_request_simulation_mode(
        self, mock_get_token: Mock, mock_session: Mock
    ) -> None:
        """Test une requête en mode simulation."""
        self.client.simulate = True

        result: List[Dict[str, str]] = self.client._request("users", 0, 100)

        self.assertEqual(result, [])
        # Aucun appel API ne doit être fait en mode simulation
        mock_session.return_value.get.assert_not_called()

    @patch("n2f.client.n2f.get_session_get")
    @patch("n2f.client.get_access_token")
    def test_request_http_error(self, mock_get_token: Mock, mock_session: Mock) -> None:
        """Test la gestion d'erreur HTTP."""
        mock_get_token.return_value = ("test_token", "2025-12-31T23:59:59Z")

        # Mock d'une erreur HTTP
        mock_response: Mock = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_session.return_value.get.return_value = mock_response

        with self.assertRaises(Exception):
            self.client._request("users", 0, 100)

    @patch("n2f.client.cache_get")
    @patch("n2f.client.cache_set")
    @patch("n2f.client.n2f.get_session_get")
    @patch("n2f.client.get_access_token")
    def test_get_users_with_cache_hit(
        self, mock_get_token, mock_session, mock_set_cache, mock_get_cache
    ):
        """Test la récupération d'utilisateurs avec cache hit."""
        # Mock du cache
        cached_data = pd.DataFrame([{"id": "1", "name": "Cached User"}])
        mock_get_cache.return_value = cached_data

        result = self.client.get_users(use_cache=True)

        self.assertTrue(result.equals(cached_data))
        mock_get_cache.assert_called_once()
        # Pas d'appel API car données en cache
        mock_session.return_value.get.assert_not_called()

    @patch("n2f.client.cache_get")
    @patch("n2f.client.cache_set")
    @patch("n2f.client.n2f.get_session_get")
    @patch("n2f.client.get_access_token")
    def test_get_users_with_cache_miss(
        self, mock_get_token, mock_session, mock_set_cache, mock_get_cache
    ):
        """Test la récupération d'utilisateurs avec cache miss."""
        # Mock du cache miss
        mock_get_cache.return_value = None

        # Mock du token
        mock_get_token.return_value = ("test_token", "2025-12-31T23:59:59Z")

        # Mock de la réponse API
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "data": [{"id": "1", "name": "User 1"}, {"id": "2", "name": "User 2"}]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_session.return_value.get.return_value = mock_response

        result = self.client.get_users(use_cache=True)

        self.assertEqual(len(result), 2)
        self.assertEqual(result.iloc[0]["name"], "User 1")

        # Vérification que les données ont été mises en cache
        mock_set_cache.assert_called_once()

    @patch("n2f.client.cache_get")
    @patch("n2f.client.cache_set")
    @patch("n2f.client.n2f.get_session_get")
    @patch("n2f.client.get_access_token")
    def test_get_users_pagination(
        self, mock_get_token, mock_session, mock_set_cache, mock_get_cache
    ):
        """Test la pagination pour get_users."""
        mock_get_cache.return_value = None
        mock_get_token.return_value = ("test_token", "2025-12-31T23:59:59Z")

        # Première page (200 éléments)
        mock_response1 = Mock()
        mock_response1.json.return_value = {
            "response": {
                "data": [{"id": str(i), "name": f"User {i}"} for i in range(200)]
            }
        }
        mock_response1.raise_for_status.return_value = None

        # Deuxième page (50 éléments - fin de pagination)
        mock_response2 = Mock()
        mock_response2.json.return_value = {
            "response": {
                "data": [{"id": str(i), "name": f"User {i}"} for i in range(200, 250)]
            }
        }
        mock_response2.raise_for_status.return_value = None

        # Configuration des appels séquentiels
        mock_session.return_value.get.side_effect = [mock_response1, mock_response2]

        result = self.client.get_users(use_cache=True)

        self.assertEqual(len(result), 250)
        # Vérification que deux appels API ont été faits
        self.assertEqual(mock_session.return_value.get.call_count, 2)

    @patch("n2f.client.cache_get")
    @patch("n2f.client.cache_set")
    @patch("n2f.client.n2f.get_session_get")
    @patch("n2f.client.get_access_token")
    def test_get_roles(
        self, mock_get_token, mock_session, mock_set_cache, mock_get_cache
    ):
        """Test la récupération des rôles."""
        mock_get_cache.return_value = None
        mock_get_token.return_value = ("test_token", "2025-12-31T23:59:59Z")

        # Mock de la réponse pour les rôles
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": [{"id": "1", "name": "Admin"}, {"id": "2", "name": "User"}]
        }
        mock_response.raise_for_status.return_value = None
        mock_session.return_value.get.return_value = mock_response

        result = self.client.get_roles(use_cache=True)

        self.assertEqual(len(result), 2)
        self.assertEqual(result.iloc[0]["name"], "Admin")

        # Vérification de l'URL appelée
        mock_session.return_value.get.assert_called_once_with(
            "https://api.n2f.test/roles", headers={"Authorization": "Bearer test_token"}
        )

    @patch("n2f.client.cache_get")
    @patch("n2f.client.cache_set")
    @patch("n2f.client.n2f.get_session_get")
    @patch("n2f.client.get_access_token")
    def test_get_userprofiles(
        self, mock_get_token, mock_session, mock_set_cache, mock_get_cache
    ):
        """Test la récupération des profils utilisateurs."""
        mock_get_cache.return_value = None
        mock_get_token.return_value = ("test_token", "2025-12-31T23:59:59Z")

        # Mock de la réponse pour les profils
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": [
                {"id": "1", "name": "Profile 1"},
                {"id": "2", "name": "Profile 2"},
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_session.return_value.get.return_value = mock_response

        result = self.client.get_userprofiles(use_cache=True)

        self.assertEqual(len(result), 2)
        self.assertEqual(result.iloc[0]["name"], "Profile 1")

    @patch("n2f.client.n2f.get_session_write")
    @patch("n2f.client.get_access_token")
    def test_upsert_success(self, mock_get_token, mock_session):
        """Test un upsert réussi."""
        mock_get_token.return_value = ("test_token", "2025-12-31T23:59:59Z")

        # Mock de la réponse
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "123", "status": "created"}
        mock_response.content = b'{"id": "123", "status": "created"}'
        mock_session.return_value.post.return_value = mock_response

        payload = {"name": "Test User", "email": "test@example.com"}
        result = self.client._upsert(
            "/users", payload, "create", "user", "test@example.com", "users"
        )

        self.assertTrue(result.success)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.action_type, "create")
        self.assertEqual(result.object_type, "user")
        self.assertEqual(result.object_id, "test@example.com")
        self.assertEqual(result.scope, "users")

    @patch("n2f.client.n2f.get_session_write")
    @patch("n2f.client.get_access_token")
    def test_upsert_http_error(self, mock_get_token, mock_session):
        """Test un upsert avec erreur HTTP."""
        mock_get_token.return_value = ("test_token", "2025-12-31T23:59:59Z")

        # Mock d'une erreur HTTP
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_session.return_value.post.return_value = mock_response

        payload = {"name": "Test User", "email": "test@example.com"}
        result = self.client._upsert(
            "/users", payload, "create", "user", "test@example.com", "users"
        )

        self.assertFalse(result.success)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.error_details, "Bad Request")

    @patch("n2f.client.n2f.get_session_write")
    @patch("n2f.client.get_access_token")
    def test_upsert_exception(self, mock_get_token, mock_session):
        """Test un upsert avec exception."""
        mock_get_token.return_value = ("test_token", "2025-12-31T23:59:59Z")
        mock_session.return_value.post.side_effect = Exception("Network error")

        payload = {"name": "Test User", "email": "test@example.com"}
        result = self.client._upsert(
            "/users", payload, "create", "user", "test@example.com", "users"
        )

        self.assertFalse(result.success)
        self.assertIn("Network error", result.error_details)

    def test_upsert_simulation_mode(self):
        """Test un upsert en mode simulation."""
        self.client.simulate = True

        payload = {"name": "Test User", "email": "test@example.com"}
        result = self.client._upsert(
            "/users", payload, "create", "user", "test@example.com", "users"
        )

        self.assertTrue(result.success)
        self.assertEqual(result.message, "Simulated upsert")
        self.assertEqual(result.action_type, "create")

    @patch("n2f.client.n2f.get_session_write")
    @patch("n2f.client.get_access_token")
    def test_delete_success(self, mock_get_token, mock_session):
        """Test une suppression réussie."""
        mock_get_token.return_value = ("test_token", "2025-12-31T23:59:59Z")

        # Mock de la réponse
        mock_response = Mock()
        mock_response.status_code = 204
        mock_session.return_value.delete.return_value = mock_response

        result = self.client._delete(
            "/users", "test@example.com", "delete", "user", "users"
        )

        self.assertTrue(result.success)
        self.assertEqual(result.status_code, 204)
        self.assertEqual(result.action_type, "delete")
        self.assertEqual(result.object_type, "user")

    @patch("n2f.client.n2f.get_session_write")
    @patch("n2f.client.get_access_token")
    def test_delete_http_error(self, mock_get_token, mock_session):
        """Test une suppression avec erreur HTTP."""
        mock_get_token.return_value = ("test_token", "2025-12-31T23:59:59Z")

        # Mock d'une erreur HTTP
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_session.return_value.delete.return_value = mock_response

        result = self.client._delete(
            "/users", "test@example.com", "delete", "user", "users"
        )

        self.assertFalse(result.success)
        self.assertEqual(result.status_code, 404)
        self.assertEqual(result.error_details, "Not Found")

    def test_delete_simulation_mode(self):
        """Test une suppression en mode simulation."""
        self.client.simulate = True

        result = self.client._delete(
            "/users", "test@example.com", "delete", "user", "users"
        )

        self.assertTrue(result.success)
        self.assertEqual(result.message, "Simulated delete")
        self.assertEqual(result.action_type, "delete")

    def test_create_user(self):
        """Test la création d'un utilisateur."""
        with patch.object(self.client, "_upsert") as mock_upsert:
            mock_upsert.return_value = ApiResult(success=True, message="Created")

            payload = {"mail": "test@example.com", "name": "Test User"}
            result = self.client.create_user(payload)

            mock_upsert.assert_called_once_with(
                "/users", payload, "create", "user", "test@example.com", "users"
            )

    def test_update_user(self):
        """Test la mise à jour d'un utilisateur."""
        with patch.object(self.client, "_upsert") as mock_upsert:
            mock_upsert.return_value = ApiResult(success=True, message="Updated")

            payload = {"mail": "test@example.com", "name": "Updated User"}
            result = self.client.update_user(payload)

            mock_upsert.assert_called_once_with(
                "/users", payload, "update", "user", "test@example.com", "users"
            )

    def test_delete_user(self):
        """Test la suppression d'un utilisateur."""
        with patch.object(self.client, "_delete") as mock_delete:
            mock_delete.return_value = ApiResult(success=True, message="Deleted")

            result = self.client.delete_user("test@example.com")

            mock_delete.assert_called_once_with(
                "/users",
                "test@example.com",
                "delete",
                "user",
                "test@example.com",
                "users",
            )

    @patch("n2f.client.cache_get")
    @patch("n2f.client.cache_set")
    @patch("n2f.client.n2f.get_session_get")
    @patch("n2f.client.get_access_token")
    def test_get_custom_axes(
        self, mock_get_token, mock_session, mock_set_cache, mock_get_cache
    ):
        """Test la récupération des axes personnalisés."""
        mock_get_cache.return_value = None
        mock_get_token.return_value = ("test_token", "2025-12-31T23:59:59Z")

        # Mock de la réponse
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "data": [{"id": "1", "name": "Axis 1"}, {"id": "2", "name": "Axis 2"}]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_session.return_value.get.return_value = mock_response

        result = self.client.get_custom_axes("company123", use_cache=True)

        self.assertEqual(len(result), 2)
        self.assertEqual(result.iloc[0]["name"], "Axis 1")

        # Vérification de l'URL appelée
        mock_session.return_value.get.assert_called_once_with(
            "https://api.n2f.test/companies/company123/axes",
            headers={"Authorization": "Bearer test_token"},
        )

    @patch("n2f.client.cache_get")
    @patch("n2f.client.cache_set")
    @patch("n2f.client.n2f.get_session_get")
    @patch("n2f.client.get_access_token")
    def test_get_axe_values(
        self, mock_get_token, mock_session, mock_set_cache, mock_get_cache
    ):
        """Test la récupération des valeurs d'axe."""
        mock_get_cache.return_value = None
        mock_get_token.return_value = ("test_token", "2025-12-31T23:59:59Z")

        # Mock de la réponse
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "data": [
                    {"code": "VAL1", "name": "Value 1"},
                    {"code": "VAL2", "name": "Value 2"},
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_session.return_value.get.return_value = mock_response

        result = self.client.get_axe_values("company123", "axis456", use_cache=True)

        self.assertEqual(len(result), 2)
        self.assertEqual(result.iloc[0]["code"], "VAL1")

        # Vérification de l'URL appelée
        mock_session.return_value.get.assert_called_once_with(
            "https://api.n2f.test/companies/company123/axes/axis456",
            headers={"Authorization": "Bearer test_token"},
            params={"start": 0, "limit": 200},
        )

    def test_upsert_axe_value(self):
        """Test l'upsert d'une valeur d'axe."""
        with patch.object(self.client, "_upsert") as mock_upsert:
            mock_upsert.return_value = ApiResult(success=True, message="Upserted")

            payload = {"code": "VAL1", "name": "Value 1"}
            result = self.client.upsert_axe_value(
                "company123", "axis456", payload, "upsert", "axes"
            )

            mock_upsert.assert_called_once_with(
                "/companies/company123/axes/axis456",
                payload,
                "upsert",
                "axe",
                "VAL1",
                "axes",
            )

    def test_delete_axe_value(self):
        """Test la suppression d'une valeur d'axe."""
        with patch.object(self.client, "_delete") as mock_delete:
            mock_delete.return_value = ApiResult(success=True, message="Deleted")

            result = self.client.delete_axe_value(
                "company123", "axis456", "VAL1", "axes"
            )

            mock_delete.assert_called_once_with(
                "/companies/company123/axes/VAL1",
                "VAL1",
                "delete",
                "axe",
                "VAL1",
                "axes",
            )

    def test_get_users_without_cache(self):
        """Test la récupération d'utilisateurs sans utiliser le cache."""
        with patch.object(self.client, "_request") as mock_request:
            mock_request.return_value = [{"id": "1", "name": "User 1"}]

            result = self.client.get_users(use_cache=False)

            self.assertEqual(len(result), 1)
            mock_request.assert_called_once_with("users", 0, 200)

    def test_get_companies_with_cache_miss(self):
        """Test la récupération d'entreprises avec cache miss."""
        with patch("n2f.client.cache_get") as mock_get_cache:
            with patch("n2f.client.cache_set") as mock_set_cache:
                with patch.object(self.client, "_request") as mock_request:
                    mock_get_cache.return_value = None
                    mock_request.return_value = [{"id": "1", "name": "Company 1"}]

                    result = self.client.get_companies(use_cache=True)

                    self.assertEqual(len(result), 1)
                    mock_get_cache.assert_called_once()
                    mock_set_cache.assert_called_once()

    def test_get_roles_simulation_mode(self):
        """Test la récupération des rôles en mode simulation."""
        self.client.simulate = True

        result = self.client.get_roles(use_cache=True)

        self.assertTrue(result.empty)
        self.assertEqual(len(result), 0)

    def test_get_userprofiles_simulation_mode(self):
        """Test la récupération des profils en mode simulation."""
        self.client.simulate = True

        result = self.client.get_userprofiles(use_cache=True)

        self.assertTrue(result.empty)
        self.assertEqual(len(result), 0)

    def test_get_custom_axes_simulation_mode(self):
        """Test la récupération des axes personnalisés en mode simulation."""
        self.client.simulate = True

        result = self.client.get_custom_axes("company123", use_cache=True)

        self.assertTrue(result.empty)
        self.assertEqual(len(result), 0)

    def test_get_axe_values_simulation_mode(self):
        """Test la récupération des valeurs d'axe en mode simulation."""
        self.client.simulate = True

        result = self.client.get_axe_values("company123", "axis456", use_cache=True)

        self.assertTrue(result.empty)
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
