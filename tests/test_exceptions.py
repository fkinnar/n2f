"""
Tests unitaires pour la hiérarchie d'exceptions personnalisées.
"""

import unittest

from core.exceptions import (
    SyncException,
    ApiException,
    ValidationException,
    ConfigurationException,
    DatabaseException,
    AuthenticationException,
    NetworkException,
)


class TestSyncException(unittest.TestCase):
    """Tests pour la classe de base SyncException."""

    def test_sync_exception_creation(self):
        """Test de création d'une exception de base."""
        exception = SyncException("Test message", "Test details", {"key": "value"})

        self.assertEqual(exception.message, "Test message")
        self.assertEqual(exception.details, "Test details")
        self.assertEqual(exception.context, {"key": "value"})

    def test_sync_exception_to_dict(self):
        """Test de la méthode to_dict()."""
        exception = SyncException("Test message", "Test details", {"key": "value"})
        result = exception.to_dict()

        expected = {
            "type": "SyncException",
            "message": "Test message",
            "details": "Test details",
            "context": {"key": "value"},
        }
        self.assertEqual(result, expected)

    def test_sync_exception_str_representation(self):
        """Test de la représentation string de l'exception."""
        exception = SyncException("Test message")
        self.assertIn("Test message", str(exception))


class TestApiException(unittest.TestCase):
    """Tests pour ApiException."""

    def test_api_exception_creation(self):
        """Test de création d'une ApiException."""
        exception = ApiException(
            "API Error",
            status_code=404,
            response_text="Not Found",
            endpoint="/users / 123",
        )

        self.assertEqual(exception.message, "API Error")
        self.assertEqual(exception.status_code, 404)
        self.assertEqual(exception.response_text, "Not Found")
        self.assertEqual(exception.endpoint, "/users / 123")

    def test_api_exception_to_dict(self):
        """Test de la méthode to_dict() pour ApiException."""
        exception = ApiException(
            "API Error",
            status_code=500,
            response_text="Internal Server Error",
            endpoint="/users",
        )
        result = exception.to_dict()

        expected = {
            "type": "ApiException",
            "message": "API Error",
            "details": None,
            "context": {},
            "status_code": 500,
            "response_text": "Internal Server Error",
            "endpoint": "/users",
        }
        self.assertEqual(result, expected)


class TestValidationException(unittest.TestCase):
    """Tests pour ValidationException."""

    def test_validation_exception_creation(self):
        """Test de création d'une ValidationException."""
        exception = ValidationException(
            "Invalid email",
            field="email",
            value="invalid - email",
            expected_format="user@domain.com",
        )

        self.assertEqual(exception.message, "Invalid email")
        self.assertEqual(exception.field, "email")
        self.assertEqual(exception.value, "invalid - email")
        self.assertEqual(exception.expected_format, "user@domain.com")

    def test_validation_exception_to_dict(self):
        """Test de la méthode to_dict() pour ValidationException."""
        exception = ValidationException(
            "Invalid field",
            field="username",
            value="",
            expected_format="non - empty string",
        )
        result = exception.to_dict()

        expected = {
            "type": "ValidationException",
            "message": "Invalid field",
            "details": None,
            "context": {},
            "field": "username",
            "value": "",
            "expected_format": "non - empty string",
        }
        self.assertEqual(result, expected)


class TestConfigurationException(unittest.TestCase):
    """Tests pour ConfigurationException."""

    def test_configuration_exception_creation(self):
        """Test de création d'une ConfigurationException."""
        exception = ConfigurationException(
            "Missing config", config_key="database.host", config_file="dev.yaml"
        )

        self.assertEqual(exception.message, "Missing config")
        self.assertEqual(exception.config_key, "database.host")
        self.assertEqual(exception.config_file, "dev.yaml")


class TestDatabaseException(unittest.TestCase):
    """Tests pour DatabaseException."""

    def test_database_exception_creation(self):
        """Test de création d'une DatabaseException."""
        exception = DatabaseException(
            "Connection failed", sql_query="SELECT * FROM users", table="users"
        )

        self.assertEqual(exception.message, "Connection failed")
        self.assertEqual(exception.sql_query, "SELECT * FROM users")
        self.assertEqual(exception.table, "users")


class TestAuthenticationException(unittest.TestCase):
    """Tests pour AuthenticationException."""

    def test_authentication_exception_creation(self):
        """Test de création d'une AuthenticationException."""
        exception = AuthenticationException(
            "Token expired", service="N2F API", credentials_type="OAuth2"
        )

        self.assertEqual(exception.message, "Token expired")
        self.assertEqual(exception.service, "N2F API")
        self.assertEqual(exception.credentials_type, "OAuth2")


class TestNetworkException(unittest.TestCase):
    """Tests pour NetworkException."""

    def test_network_exception_creation(self):
        """Test de création d'une NetworkException."""
        exception = NetworkException(
            "Connection timeout",
            url="https://api.n2f.com / users",
            timeout=30.0,
            retry_count=3,
        )

        self.assertEqual(exception.message, "Connection timeout")
        self.assertEqual(exception.url, "https://api.n2f.com / users")
        self.assertEqual(exception.timeout, 30.0)
        self.assertEqual(exception.retry_count, 3)


class TestExceptionHierarchy(unittest.TestCase):
    """Tests pour vérifier la hiérarchie d'exceptions."""

    def test_exception_inheritance(self):
        """Test que toutes les exceptions héritent de SyncException."""
        exceptions = [
            ApiException("test"),
            ValidationException("test"),
            ConfigurationException("test"),
            DatabaseException("test"),
            AuthenticationException("test"),
            NetworkException("test"),
        ]

        for exception in exceptions:
            self.assertIsInstance(exception, SyncException)
            self.assertIsInstance(exception, Exception)

    def test_exception_context_preservation(self):
        """Test que le contexte est préservé dans la hiérarchie."""
        context = {"user_id": "123", "operation": "create"}

        api_exception = ApiException("API Error", context=context)
        self.assertEqual(api_exception.context, context)

        validation_exception = ValidationException("Validation Error", context=context)
        self.assertEqual(validation_exception.context, context)


if __name__ == "__main__":
    unittest.main()
