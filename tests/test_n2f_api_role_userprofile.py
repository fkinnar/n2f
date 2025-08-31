#!/usr/bin/env python3
"""
Tests pour les modules n2f/api/role.py et n2f/api/userprofile.py.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Ajouter le répertoire python au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from n2f.api.role import get_roles
from n2f.api.userprofile import get_userprofiles


class TestN2fApiRole(unittest.TestCase):
    """Tests pour n2f/api/role.py."""

    def setUp(self):
        """Configuration initiale."""
        self.base_url = "https://test.api.com"
        self.client_id = "test_client"
        self.client_secret = "test_secret"

    @patch('n2f.api.role.retreive')
    def test_get_roles_success(self, mock_retreive):
        """Test de récupération des rôles avec succès."""
        # Mock de la réponse
        mock_response = {
            "response": [
                {"id": 1, "name": "Admin", "description": "Administrator"},
                {"id": 2, "name": "User", "description": "Regular user"}
            ]
        }
        mock_retreive.return_value = mock_response

        # Appeler la fonction
        result = get_roles(self.base_url, self.client_id, self.client_secret)

        # Vérifications
        mock_retreive.assert_called_once_with(
            "roles",
            self.base_url,
            self.client_id,
            self.client_secret,
            simulate=False
        )

        self.assertEqual(result, mock_response["response"])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Admin")
        self.assertEqual(result[1]["name"], "User")

    @patch('n2f.api.role.retreive')
    def test_get_roles_with_simulate(self, mock_retreive):
        """Test de récupération des rôles en mode simulation."""
        # Mock de la réponse
        mock_response = {
            "response": [
                {"id": 1, "name": "Test Role", "description": "Test description"}
            ]
        }
        mock_retreive.return_value = mock_response

        # Appeler la fonction avec simulate=True
        result = get_roles(self.base_url, self.client_id, self.client_secret, simulate=True)

        # Vérifications
        mock_retreive.assert_called_once_with(
            "roles",
            self.base_url,
            self.client_id,
            self.client_secret,
            simulate=True
        )

        self.assertEqual(result, mock_response["response"])

    @patch('n2f.api.role.retreive')
    def test_get_roles_empty_response(self, mock_retreive):
        """Test de récupération des rôles avec réponse vide."""
        # Mock de la réponse vide
        mock_response = {
            "response": []
        }
        mock_retreive.return_value = mock_response

        # Appeler la fonction
        result = get_roles(self.base_url, self.client_id, self.client_secret)

        # Vérifications
        self.assertEqual(result, [])
        self.assertEqual(len(result), 0)

    @patch('n2f.api.role.retreive')
    def test_get_roles_api_error(self, mock_retreive):
        """Test de récupération des rôles avec erreur API."""
        # Mock d'une exception
        mock_retreive.side_effect = Exception("API Error")

        # Vérifier que l'exception est levée
        with self.assertRaises(Exception):
            get_roles(self.base_url, self.client_id, self.client_secret)


class TestN2fApiUserprofile(unittest.TestCase):
    """Tests pour n2f/api/userprofile.py."""

    def setUp(self):
        """Configuration initiale."""
        self.base_url = "https://test.api.com"
        self.client_id = "test_client"
        self.client_secret = "test_secret"

    @patch('n2f.api.userprofile.retreive')
    def test_get_userprofiles_success(self, mock_retreive):
        """Test de récupération des profils utilisateurs avec succès."""
        # Mock de la réponse
        mock_response = {
            "response": [
                {"id": 1, "name": "Standard", "description": "Standard profile"},
                {"id": 2, "name": "Premium", "description": "Premium profile"},
                {"id": 3, "name": "Admin", "description": "Administrator profile"}
            ]
        }
        mock_retreive.return_value = mock_response

        # Appeler la fonction
        result = get_userprofiles(self.base_url, self.client_id, self.client_secret)

        # Vérifications
        mock_retreive.assert_called_once_with(
            "userprofiles",
            self.base_url,
            self.client_id,
            self.client_secret,
            simulate=False
        )

        self.assertEqual(result, mock_response["response"])
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["name"], "Standard")
        self.assertEqual(result[1]["name"], "Premium")
        self.assertEqual(result[2]["name"], "Admin")

    @patch('n2f.api.userprofile.retreive')
    def test_get_userprofiles_with_simulate(self, mock_retreive):
        """Test de récupération des profils utilisateurs en mode simulation."""
        # Mock de la réponse
        mock_response = {
            "response": [
                {"id": 1, "name": "Test Profile", "description": "Test description"}
            ]
        }
        mock_retreive.return_value = mock_response

        # Appeler la fonction avec simulate=True
        result = get_userprofiles(self.base_url, self.client_id, self.client_secret, simulate=True)

        # Vérifications
        mock_retreive.assert_called_once_with(
            "userprofiles",
            self.base_url,
            self.client_id,
            self.client_secret,
            simulate=True
        )

        self.assertEqual(result, mock_response["response"])

    @patch('n2f.api.userprofile.retreive')
    def test_get_userprofiles_empty_response(self, mock_retreive):
        """Test de récupération des profils utilisateurs avec réponse vide."""
        # Mock de la réponse vide
        mock_response = {
            "response": []
        }
        mock_retreive.return_value = mock_response

        # Appeler la fonction
        result = get_userprofiles(self.base_url, self.client_id, self.client_secret)

        # Vérifications
        self.assertEqual(result, [])
        self.assertEqual(len(result), 0)

    @patch('n2f.api.userprofile.retreive')
    def test_get_userprofiles_api_error(self, mock_retreive):
        """Test de récupération des profils utilisateurs avec erreur API."""
        # Mock d'une exception
        mock_retreive.side_effect = Exception("API Error")

        # Vérifier que l'exception est levée
        with self.assertRaises(Exception):
            get_userprofiles(self.base_url, self.client_id, self.client_secret)

    @patch('n2f.api.userprofile.retreive')
    def test_get_userprofiles_complex_data(self, mock_retreive):
        """Test de récupération des profils utilisateurs avec données complexes."""
        # Mock de la réponse avec données complexes
        mock_response = {
            "response": [
                {
                    "id": 1,
                    "name": "Complex Profile",
                    "description": "A complex profile",
                    "permissions": ["read", "write", "delete"],
                    "settings": {
                        "theme": "dark",
                        "language": "en",
                        "notifications": True
                    },
                    "metadata": {
                        "created_at": "2023-01-01T00:00:00Z",
                        "updated_at": "2023-01-02T00:00:00Z",
                        "version": "1.0"
                    }
                }
            ]
        }
        mock_retreive.return_value = mock_response

        # Appeler la fonction
        result = get_userprofiles(self.base_url, self.client_id, self.client_secret)

        # Vérifications
        self.assertEqual(result, mock_response["response"])
        self.assertEqual(len(result), 1)

        profile = result[0]
        self.assertEqual(profile["name"], "Complex Profile")
        self.assertEqual(profile["permissions"], ["read", "write", "delete"])
        self.assertEqual(profile["settings"]["theme"], "dark")
        self.assertEqual(profile["metadata"]["version"], "1.0")


if __name__ == '__main__':
    unittest.main()
