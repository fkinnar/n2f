"""
Tests unitaires pour le module src / core/exceptions.py.

Ce module teste toutes les classes d'exceptions personnalisées et les fonctions
    utilitaires.
"""

import unittest
from unittest.mock import Mock, patch
import json

from core.exceptions import (
    SyncException,
    ApiException,
    ValidationException,
    ConfigurationException,
    DatabaseException,
    AuthenticationException,
    NetworkException,
    wrap_api_call,
    handle_sync_exceptions,
)


class TestSyncException(unittest.TestCase):
    """Tests pour la classe de base SyncException."""

    def test_sync_exception_basic(self):
        """Test de création d'une exception de base."""
        exc = SyncException("Test message")
        self.assertEqual(exc.message, "Test message")
        self.assertIsNone(exc.details)
        self.assertEqual(exc.context, {})

    def test_sync_exception_with_details(self):
        """Test de création d'une exception avec détails."""
        exc = SyncException("Test message", "Test details")
        self.assertEqual(exc.message, "Test message")
        self.assertEqual(exc.details, "Test details")
        self.assertEqual(exc.context, {})

    def test_sync_exception_with_context(self):
        """Test de création d'une exception avec contexte."""
        context = {"key": "value", "number": 42}
        exc = SyncException("Test message", "Test details", context)
        self.assertEqual(exc.message, "Test message")
        self.assertEqual(exc.details, "Test details")
        self.assertEqual(exc.context, context)

    def test_sync_exception_str_representation(self):
        """Test de la représentation string de l'exception."""
        exc = SyncException("Test message")
        self.assertEqual(str(exc), "Test message")

        exc_with_details = SyncException("Test message", "Test details")
        self.assertEqual(str(exc_with_details), "Test message - Details: Test details")

    def test_sync_exception_to_dict(self):
        """Test de la conversion en dictionnaire."""
        context = {"key": "value"}
        exc = SyncException("Test message", "Test details", context)

        result = exc.to_dict()
        expected = {
            "type": "SyncException",
            "message": "Test message",
            "details": "Test details",
            "context": context,
        }
        self.assertEqual(result, expected)


class TestApiException(unittest.TestCase):
    """Tests pour la classe ApiException."""

    def test_api_exception_basic(self):
        """Test de création d'une exception API de base."""
        exc = ApiException("API error")
        self.assertEqual(exc.message, "API error")
        self.assertIsNone(exc.status_code)
        self.assertIsNone(exc.response_text)
        self.assertIsNone(exc.endpoint)

    def test_api_exception_with_all_fields(self):
        """Test de création d'une exception API avec tous les champs."""
        exc = ApiException(
            message="API error",
            status_code=404,
            response_text="Not found",
            endpoint="/api / users",
            details="User not found",
            context={"user_id": "123"},
        )
        self.assertEqual(exc.message, "API error")
        self.assertEqual(exc.status_code, 404)
        self.assertEqual(exc.response_text, "Not found")
        self.assertEqual(exc.endpoint, "/api / users")
        self.assertEqual(exc.details, "User not found")
        self.assertEqual(exc.context, {"user_id": "123"})

    def test_api_exception_to_dict(self):
        """Test de la conversion en dictionnaire."""
        exc = ApiException(
            message="API error",
            status_code=500,
            response_text="Internal error",
            endpoint="/api / data",
            details="Server error",
            context={"request_id": "abc123"},
        )

        result = exc.to_dict()
        expected = {
            "type": "ApiException",
            "message": "API error",
            "details": "Server error",
            "context": {"request_id": "abc123"},
            "status_code": 500,
            "response_text": "Internal error",
            "endpoint": "/api / data",
        }
        self.assertEqual(result, expected)


class TestValidationException(unittest.TestCase):
    """Tests pour la classe ValidationException."""

    def test_validation_exception_basic(self):
        """Test de création d'une exception de validation de base."""
        exc = ValidationException("Validation error")
        self.assertEqual(exc.message, "Validation error")
        self.assertIsNone(exc.field)
        self.assertIsNone(exc.value)
        self.assertIsNone(exc.expected_format)

    def test_validation_exception_with_all_fields(self):
        """Test de création d'une exception de validation avec tous les champs."""
        exc = ValidationException(
            message="Invalid email",
            field="email",
            value="invalid - email",
            expected_format="user@domain.com",
            details="Email format is invalid",
            context={"form": "registration"},
        )
        self.assertEqual(exc.message, "Invalid email")
        self.assertEqual(exc.field, "email")
        self.assertEqual(exc.value, "invalid - email")
        self.assertEqual(exc.expected_format, "user@domain.com")
        self.assertEqual(exc.details, "Email format is invalid")
        self.assertEqual(exc.context, {"form": "registration"})

    def test_validation_exception_to_dict(self):
        """Test de la conversion en dictionnaire."""
        exc = ValidationException(
            message="Invalid age",
            field="age",
            value=-5,
            expected_format="positive integer",
            details="Age must be positive",
            context={"user": "john"},
        )

        result = exc.to_dict()
        expected = {
            "type": "ValidationException",
            "message": "Invalid age",
            "details": "Age must be positive",
            "context": {"user": "john"},
            "field": "age",
            "value": "-5",
            "expected_format": "positive integer",
        }
        self.assertEqual(result, expected)

    def test_validation_exception_to_dict_with_none_value(self):
        """Test de la conversion en dictionnaire avec une valeur None."""
        exc = ValidationException(
            message="Missing field",
            field="required_field",
            value=None,
            expected_format="any value",
        )

        result = exc.to_dict()
        self.assertIsNone(result["value"])


class TestConfigurationException(unittest.TestCase):
    """Tests pour la classe ConfigurationException."""

    def test_configuration_exception_basic(self):
        """Test de création d'une exception de configuration de base."""
        exc = ConfigurationException("Config error")
        self.assertEqual(exc.message, "Config error")
        self.assertIsNone(exc.config_key)
        self.assertIsNone(exc.config_file)

    def test_configuration_exception_with_all_fields(self):
        """Test de création d'une exception de configuration avec tous les champs."""
        exc = ConfigurationException(
            message="Missing config key",
            config_key="database_url",
            config_file="config.json",
            details="Database URL is required",
            context={"environment": "production"},
        )
        self.assertEqual(exc.message, "Missing config key")
        self.assertEqual(exc.config_key, "database_url")
        self.assertEqual(exc.config_file, "config.json")
        self.assertEqual(exc.details, "Database URL is required")
        self.assertEqual(exc.context, {"environment": "production"})

    def test_configuration_exception_to_dict(self):
        """Test de la conversion en dictionnaire."""
        exc = ConfigurationException(
            message="Invalid config",
            config_key="api_key",
            config_file="settings.yaml",
            details="API key is invalid",
            context={"service": "n2f"},
        )

        result = exc.to_dict()
        expected = {
            "type": "ConfigurationException",
            "message": "Invalid config",
            "details": "API key is invalid",
            "context": {"service": "n2f"},
            "config_key": "api_key",
            "config_file": "settings.yaml",
        }
        self.assertEqual(result, expected)


class TestDatabaseException(unittest.TestCase):
    """Tests pour la classe DatabaseException."""

    def test_database_exception_basic(self):
        """Test de création d'une exception de base de données de base."""
        exc = DatabaseException("Database error")
        self.assertEqual(exc.message, "Database error")
        self.assertIsNone(exc.sql_query)
        self.assertIsNone(exc.table)

    def test_database_exception_with_all_fields(self):
        """Test de création d'une exception de base de données avec tous les champs."""
        exc = DatabaseException(
            message="Connection failed",
            sql_query="SELECT * FROM users",
            table="users",
            details="Connection timeout",
            context={"database": "agresso"},
        )
        self.assertEqual(exc.message, "Connection failed")
        self.assertEqual(exc.sql_query, "SELECT * FROM users")
        self.assertEqual(exc.table, "users")
        self.assertEqual(exc.details, "Connection timeout")
        self.assertEqual(exc.context, {"database": "agresso"})

    def test_database_exception_to_dict(self):
        """Test de la conversion en dictionnaire."""
        exc = DatabaseException(
            message="Query failed",
            sql_query="INSERT INTO projects VALUES (?)",
            table="projects",
            details="Constraint violation",
            context={"operation": "insert"},
        )

        result = exc.to_dict()
        expected = {
            "type": "DatabaseException",
            "message": "Query failed",
            "details": "Constraint violation",
            "context": {"operation": "insert"},
            "sql_query": "INSERT INTO projects VALUES (?)",
            "table": "projects",
        }
        self.assertEqual(result, expected)


class TestAuthenticationException(unittest.TestCase):
    """Tests pour la classe AuthenticationException."""

    def test_authentication_exception_basic(self):
        """Test de création d'une exception d'authentification de base."""
        exc = AuthenticationException("Auth error")
        self.assertEqual(exc.message, "Auth error")
        self.assertIsNone(exc.service)
        self.assertIsNone(exc.credentials_type)

    def test_authentication_exception_with_all_fields(self):
        """Test de création d'une exception d'authentification avec tous les champs."""
        exc = AuthenticationException(
            message="Invalid token",
            service="N2F",
            credentials_type="bearer_token",
            details="Token expired",
            context={"user": "admin"},
        )
        self.assertEqual(exc.message, "Invalid token")
        self.assertEqual(exc.service, "N2F")
        self.assertEqual(exc.credentials_type, "bearer_token")
        self.assertEqual(exc.details, "Token expired")
        self.assertEqual(exc.context, {"user": "admin"})

    def test_authentication_exception_to_dict(self):
        """Test de la conversion en dictionnaire."""
        exc = AuthenticationException(
            message="Invalid credentials",
            service="Agresso",
            credentials_type="username_password",
            details="Wrong password",
            context={"attempt": 3},
        )

        result = exc.to_dict()
        expected = {
            "type": "AuthenticationException",
            "message": "Invalid credentials",
            "details": "Wrong password",
            "context": {"attempt": 3},
            "service": "Agresso",
            "credentials_type": "username_password",
        }
        self.assertEqual(result, expected)


class TestNetworkException(unittest.TestCase):
    """Tests pour la classe NetworkException."""

    def test_network_exception_basic(self):
        """Test de création d'une exception réseau de base."""
        exc = NetworkException("Network error")
        self.assertEqual(exc.message, "Network error")
        self.assertIsNone(exc.url)
        self.assertIsNone(exc.timeout)
        self.assertIsNone(exc.retry_count)

    def test_network_exception_with_all_fields(self):
        """Test de création d'une exception réseau avec tous les champs."""
        exc = NetworkException(
            message="Connection timeout",
            url="https://api.n2f.com / users",
            timeout=30.0,
            retry_count=3,
            details="Server not responding",
            context={"method": "GET"},
        )
        self.assertEqual(exc.message, "Connection timeout")
        self.assertEqual(exc.url, "https://api.n2f.com / users")
        self.assertEqual(exc.timeout, 30.0)
        self.assertEqual(exc.retry_count, 3)
        self.assertEqual(exc.details, "Server not responding")
        self.assertEqual(exc.context, {"method": "GET"})

    def test_network_exception_to_dict(self):
        """Test de la conversion en dictionnaire."""
        exc = NetworkException(
            message="DNS resolution failed",
            url="https://api.example.com",
            timeout=10.0,
            retry_count=1,
            details="Cannot resolve hostname",
            context={"environment": "development"},
        )

        result = exc.to_dict()
        expected = {
            "type": "NetworkException",
            "message": "DNS resolution failed",
            "details": "Cannot resolve hostname",
            "context": {"environment": "development"},
            "url": "https://api.example.com",
            "timeout": 10.0,
            "retry_count": 1,
        }
        self.assertEqual(result, expected)


class TestDecorators(unittest.TestCase):
    """Tests pour les décorateurs utilitaires."""

    def test_wrap_api_call_success(self):
        """Test du décorateur wrap_api_call avec succès."""

        @wrap_api_call
        def test_function():
            return "success"

        result = test_function()
        self.assertEqual(result, "success")

    def test_wrap_api_call_with_api_exception(self):
        """Test du décorateur wrap_api_call avec ApiException."""

        @wrap_api_call
        def test_function():
            raise ApiException("API error")

        with self.assertRaises(ApiException) as context:
            test_function()

        self.assertEqual(context.exception.message, "API error")

    def test_wrap_api_call_with_generic_exception(self):
        """Test du décorateur wrap_api_call avec une exception générique."""

        @wrap_api_call
        def test_function():
            raise ValueError("Generic error")

        with self.assertRaises(ApiException) as context:
            test_function()

        self.assertIn("Unexpected error in API call", context.exception.message)
        self.assertEqual(context.exception.details, "Generic error")
        self.assertIn("test_function", context.exception.context["function"])

    def test_wrap_api_call_with_arguments(self):
        """Test du décorateur wrap_api_call avec des arguments."""

        @wrap_api_call
        def test_function(arg1, arg2, kwarg1=None):
            raise RuntimeError("Runtime error")

        with self.assertRaises(ApiException) as context:
            test_function("value1", "value2", kwarg1="kwvalue")

        self.assertIn("Unexpected error in API call", context.exception.message)
        self.assertIn("test_function", context.exception.context["function"])

    def test_handle_sync_exceptions_success(self):
        """Test du décorateur handle_sync_exceptions avec succès."""

        @handle_sync_exceptions
        def test_function():
            return "success"

        result = test_function()
        self.assertEqual(result, "success")

    def test_handle_sync_exceptions_with_sync_exception(self):
        """Test du décorateur handle_sync_exceptions avec SyncException."""

        @handle_sync_exceptions
        def test_function():
            raise SyncException("Sync error")

        with self.assertRaises(SyncException) as context:
            test_function()

        self.assertEqual(context.exception.message, "Sync error")

    def test_handle_sync_exceptions_with_generic_exception(self):
        """Test du décorateur handle_sync_exceptions avec une exception générique."""

        @handle_sync_exceptions
        def test_function():
            raise TypeError("Type error")

        with self.assertRaises(SyncException) as context:
            test_function()

        self.assertIn("Unexpected error in synchronization", context.exception.message)
        self.assertEqual(context.exception.details, "Type error")
        self.assertIn("test_function", context.exception.context["function"])

    def test_handle_sync_exceptions_with_arguments(self):
        """Test du décorateur handle_sync_exceptions avec des arguments."""

        @handle_sync_exceptions
        def test_function(arg1, arg2, kwarg1=None):
            raise OSError("OS error")

        with self.assertRaises(SyncException) as context:
            test_function("value1", "value2", kwarg1="kwvalue")

        self.assertIn("Unexpected error in synchronization", context.exception.message)
        self.assertIn("test_function", context.exception.context["function"])


if __name__ == "__main__":
    unittest.main()
