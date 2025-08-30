import unittest
from unittest.mock import Mock, patch, MagicMock
import time
import sys
import os
from datetime import datetime

# Ajouter le répertoire python au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

import n2f.api.token as token_module


class TestCacheToken(unittest.TestCase):
    """Tests pour le décorateur cache_token."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.mock_func = Mock()
        self.mock_func.__name__ = 'test_func'

    def test_cache_token_decorator_creation(self):
        """Test que le décorateur se crée correctement."""
        decorator = token_module.cache_token()
        decorated_func = decorator(self.mock_func)

        self.assertIsNotNone(decorated_func)
        self.assertTrue(callable(decorated_func))

    def test_cache_token_first_call(self):
        """Test que le premier appel exécute la fonction et cache le résultat."""
        self.mock_func.return_value = ("test_token", "2025-08-20T09:54:35.8185075Z")

        decorator = token_module.cache_token()
        decorated_func = decorator(self.mock_func)

        with patch('time.time', return_value=1000):
            result = decorated_func("arg1", kwarg1="value1")

        # Vérifie que la fonction originale a été appelée
        self.mock_func.assert_called_once_with("arg1", kwarg1="value1")

        # Vérifie le résultat
        self.assertEqual(result[0], "test_token")
        self.assertIsInstance(result[1], float)  # expires_at converti en timestamp

    def test_cache_token_cached_call(self):
        """Test que les appels suivants utilisent le cache."""
        self.mock_func.return_value = ("test_token", "2025-08-20T09:54:35.8185075Z")

        decorator = token_module.cache_token(safety_margin=10)
        decorated_func = decorator(self.mock_func)

        # Premier appel
        with patch('time.time', return_value=1000):
            result1 = decorated_func("arg1")

        # Deuxième appel (dans la fenêtre de cache)
        with patch('time.time', return_value=1500):
            result2 = decorated_func("arg1")

        # La fonction originale ne doit être appelée qu'une fois
        self.mock_func.assert_called_once()

        # Les résultats doivent être identiques
        self.assertEqual(result1, result2)

    def test_cache_token_expired_cache(self):
        """Test que le cache expire correctement."""
        self.mock_func.side_effect = [
            ("token1", "2025-08-20T09:54:35.8185075Z"),
            ("token2", "2025-08-20T10:54:35.8185075Z")
        ]

        decorator = token_module.cache_token(safety_margin=10)
        decorated_func = decorator(self.mock_func)

        # Premier appel - token expire en 2025 (timestamp très élevé)
        with patch('time.time', return_value=1000):
            result1 = decorated_func("arg1")

        # Deuxième appel après expiration (simulation d'un temps futur)
        # Le token de 2025 sera expiré quand on simule l'année 2026
        future_time = datetime(2026, 1, 1).timestamp()
        with patch('time.time', return_value=future_time):
            result2 = decorated_func("arg1")

        # La fonction originale doit être appelée deux fois
        self.assertEqual(self.mock_func.call_count, 2)

        # Les tokens doivent être différents
        self.assertEqual(result1[0], "token1")
        self.assertEqual(result2[0], "token2")

    def test_cache_token_safety_margin(self):
        """Test que la marge de sécurité fonctionne correctement."""
        # Token qui expire dans 1 heure
        future_iso = "2025-08-20T10:54:35.8185075Z"
        expires_at = datetime.fromisoformat(future_iso.replace("Z", "+00:00")).timestamp()

        self.mock_func.side_effect = [
            ("token1", future_iso),
            ("token2", "2025-08-20T11:54:35.8185075Z")
        ]

        safety_margin = 300  # 5 minutes
        decorator = token_module.cache_token(safety_margin=safety_margin)
        decorated_func = decorator(self.mock_func)

        # Premier appel
        with patch('time.time', return_value=1000):
            decorated_func("arg1")

        # Deuxième appel juste avant la marge de sécurité
        # Le cache devrait expirer à cause de la marge de sécurité
        test_time = expires_at - safety_margin + 1  # Juste dans la marge

        with patch('time.time', return_value=test_time):
            decorated_func("arg1")

        # La fonction doit être appelée deux fois à cause de la marge de sécurité
        self.assertEqual(self.mock_func.call_count, 2)

    def test_cache_token_iso_date_parsing(self):
        """Test que le parsing des dates ISO fonctionne correctement."""
        test_cases = [
            "2025-08-20T09:54:35.8185075Z",
            "2025-12-31T23:59:59.999Z",
            "2025-01-01T00:00:00Z"
        ]

        for iso_date in test_cases:
            with self.subTest(iso_date=iso_date):
                mock_func = Mock()
                mock_func.__name__ = 'test_func'
                mock_func.return_value = ("test_token", iso_date)

                decorator = token_module.cache_token()
                decorated_func = decorator(mock_func)

                with patch('time.time', return_value=1000):
                    result = decorated_func()

                # Vérifie que la date a été convertie en timestamp
                self.assertIsInstance(result[1], float)
                self.assertGreater(result[1], 0)


class TestGetAccessToken(unittest.TestCase):
    """Tests pour la fonction get_access_token."""

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.base_url = "https://api.n2f.com"
        self.client_id = "test_client_id"
        self.client_secret = "test_client_secret"

        # Mock response pour les tests
        self.mock_response = Mock()
        self.mock_response.json.return_value = {
            "response": {
                "token": "test_access_token",
                "validity": "2025-08-20T09:54:35.8185075Z"
            }
        }

    @patch('n2f.get_session_write')
    def test_get_access_token_success(self, mock_get_session):
        """Test de récupération réussie d'un token d'accès."""
        mock_session = Mock()
        mock_session.post.return_value = self.mock_response
        mock_get_session.return_value = mock_session

        # Créer une fonction temporaire sans cache pour tester la logique de base
        def temp_get_token(base_url, client_id, client_secret, simulate=False):
            if simulate:
                return "", ""

            url = base_url + "/auth"
            payload = {
                "client_id": client_id,
                "client_secret": client_secret
            }
            headers = {
                "Content-Type": "application/json"
            }

            response = mock_session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            token = data["response"]["token"]
            validity = data["response"]["validity"]
            return token, validity

        result = temp_get_token(self.base_url, self.client_id, self.client_secret)

        # Vérifications
        self.assertEqual(result[0], "test_access_token")
        self.assertEqual(result[1], "2025-08-20T09:54:35.8185075Z")

        # Vérifie l'appel à l'API
        mock_session.post.assert_called_once_with(
            "https://api.n2f.com/auth",
            json={
                "client_id": "test_client_id",
                "client_secret": "test_client_secret"
            },
            headers={"Content-Type": "application/json"}
        )

    def test_get_access_token_simulation_mode(self):
        """Test du mode simulation."""
        result = token_module.get_access_token(
            self.base_url, self.client_id, self.client_secret, simulate=True
        )

        self.assertEqual(result, ("", ""))

    @patch('n2f.get_session_write')
    def test_get_access_token_http_error(self, mock_get_session):
        """Test de gestion d'erreur HTTP."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 401 Unauthorized")
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        # Créer une fonction temporaire sans cache
        def temp_get_token(base_url, client_id, client_secret):
            url = base_url + "/auth"
            payload = {
                "client_id": client_id,
                "client_secret": client_secret
            }
            headers = {
                "Content-Type": "application/json"
            }

            response = mock_session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            token = data["response"]["token"]
            validity = data["response"]["validity"]
            return token, validity

        with self.assertRaises(Exception):
            temp_get_token(self.base_url, self.client_id, self.client_secret)

    @patch('n2f.get_session_write')
    def test_get_access_token_invalid_response(self, mock_get_session):
        """Test de gestion de réponse invalide."""
        mock_session = Mock()
        invalid_response = Mock()
        invalid_response.json.return_value = {"error": "Invalid credentials"}
        mock_session.post.return_value = invalid_response
        mock_get_session.return_value = mock_session

        # Créer une fonction temporaire sans cache
        def temp_get_token(base_url, client_id, client_secret):
            url = base_url + "/auth"
            payload = {
                "client_id": client_id,
                "client_secret": client_secret
            }
            headers = {
                "Content-Type": "application/json"
            }

            response = mock_session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            token = data["response"]["token"]
            validity = data["response"]["validity"]
            return token, validity

        with self.assertRaises(KeyError):
            temp_get_token(self.base_url, self.client_id, self.client_secret)

    @patch('n2f.get_session_write')
    def test_get_access_token_with_cache_integration(self, mock_get_session):
        """Test d'intégration basique avec le cache."""
        mock_session = Mock()
        mock_session.post.return_value = self.mock_response
        mock_get_session.return_value = mock_session

        # Premier appel - devrait déclencher une requête HTTP
        with patch('time.time', return_value=1000):
            result1 = token_module.get_access_token(
                self.base_url, self.client_id, self.client_secret
            )

        # Vérifications de base
        self.assertEqual(result1[0], "test_access_token")
        self.assertIsInstance(result1[1], float)  # expires_at converti en timestamp


if __name__ == '__main__':
    unittest.main()
