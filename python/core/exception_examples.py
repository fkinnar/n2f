"""
Exemples d'utilisation des exceptions personnalisées.

Ce fichier montre comment utiliser les différentes exceptions
pour améliorer la gestion d'erreur dans le projet.
"""

from core.exceptions import (
    SyncException, ApiException, ValidationException, ConfigurationException,
    DatabaseException, AuthenticationException, NetworkException,
    wrap_api_call, handle_sync_exceptions
)


# Exemple 1: Gestion d'erreur d'API
def example_api_error_handling():
    """Exemple de gestion d'erreur d'API avec ApiException."""

    try:
        # Simulation d'un appel API qui échoue
        response_status = 404
        if response_status != 200:
            raise ApiException(
                message="User not found",
                status_code=response_status,
                endpoint="/users/john.doe@example.com",
                response_text="User with email john.doe@example.com does not exist",
                details="The user was deleted or never existed"
            )
    except ApiException as e:
        print(f"API Error: {e}")
        print(f"Status Code: {e.status_code}")
        print(f"Endpoint: {e.endpoint}")
        print(f"Response: {e.response_text}")
        print(f"Details: {e.details}")


# Exemple 2: Validation de données
def example_validation_error():
    """Exemple de gestion d'erreur de validation."""

    try:
        # Simulation d'une validation qui échoue
        email = "invalid-email"
        if "@" not in email:
            raise ValidationException(
                message="Invalid email format",
                field="email",
                value=email,
                expected_format="user@domain.com",
                details="Email must contain @ symbol"
            )
    except ValidationException as e:
        print(f"Validation Error: {e}")
        print(f"Field: {e.field}")
        print(f"Value: {e.value}")
        print(f"Expected Format: {e.expected_format}")


# Exemple 3: Erreur de configuration
def example_configuration_error():
    """Exemple de gestion d'erreur de configuration."""

    try:
        # Simulation d'une configuration manquante
        config_key = "database_url"
        if config_key not in {"database_host", "database_port"}:
            raise ConfigurationException(
                message="Missing required configuration",
                config_key=config_key,
                config_file="dev.yaml",
                details="Database URL is required for connection"
            )
    except ConfigurationException as e:
        print(f"Configuration Error: {e}")
        print(f"Config Key: {e.config_key}")
        print(f"Config File: {e.config_file}")


# Exemple 4: Erreur de base de données
def example_database_error():
    """Exemple de gestion d'erreur de base de données."""

    try:
        # Simulation d'une erreur de base de données
        sql_query = "SELECT * FROM users WHERE email = 'test@example.com'"
        raise DatabaseException(
            message="Table does not exist",
            sql_query=sql_query,
            table="users",
            details="The users table was dropped or renamed"
        )
    except DatabaseException as e:
        print(f"Database Error: {e}")
        print(f"SQL Query: {e.sql_query}")
        print(f"Table: {e.table}")


# Exemple 5: Erreur d'authentification
def example_authentication_error():
    """Exemple de gestion d'erreur d'authentification."""

    try:
        # Simulation d'une erreur d'authentification
        raise AuthenticationException(
            message="Invalid credentials",
            service="N2F",
            credentials_type="client_secret",
            details="The client secret has expired or is incorrect"
        )
    except AuthenticationException as e:
        print(f"Authentication Error: {e}")
        print(f"Service: {e.service}")
        print(f"Credentials Type: {e.credentials_type}")


# Exemple 6: Erreur réseau
def example_network_error():
    """Exemple de gestion d'erreur réseau."""

    try:
        # Simulation d'une erreur réseau
        raise NetworkException(
            message="Connection timeout",
            url="https://api.n2f.com/users",
            timeout=30.0,
            retry_count=3,
            details="The server did not respond within 30 seconds"
        )
    except NetworkException as e:
        print(f"Network Error: {e}")
        print(f"URL: {e.url}")
        print(f"Timeout: {e.timeout}s")
        print(f"Retry Count: {e.retry_count}")


# Exemple 7: Utilisation du décorateur pour les appels API
@wrap_api_call
def example_api_function():
    """Exemple de fonction API avec décorateur de gestion d'exceptions."""
    # Cette fonction sera automatiquement wrapper avec gestion d'exceptions
    return "API call successful"


# Exemple 8: Utilisation du décorateur pour la synchronisation
@handle_sync_exceptions
def example_sync_function():
    """Exemple de fonction de synchronisation avec décorateur de gestion d'exceptions."""
    # Cette fonction sera automatiquement wrapper avec gestion d'exceptions
    return "Synchronization successful"


# Exemple 9: Conversion d'exceptions en dictionnaire
def example_exception_serialization():
    """Exemple de sérialisation d'exceptions."""

    try:
        raise ApiException(
            message="API call failed",
            status_code=500,
            endpoint="/users",
            details="Internal server error"
        )
    except ApiException as e:
        # Convertir l'exception en dictionnaire pour la sérialisation
        error_dict = e.to_dict()
        print("Exception as dictionary:")
        for key, value in error_dict.items():
            print(f"  {key}: {value}")


# Exemple 10: Gestion hiérarchique d'exceptions
def example_hierarchical_exception_handling():
    """Exemple de gestion hiérarchique d'exceptions."""

    try:
        # Simulation d'une erreur d'API
        raise ApiException("API error")
    except ApiException as e:
        print(f"Caught ApiException: {e}")
    except SyncException as e:
        print(f"Caught SyncException: {e}")
    except Exception as e:
        print(f"Caught generic Exception: {e}")


def run_all_examples():
    """Exécute tous les exemples d'exceptions."""
    print("=== Exceptions personnalisées - Exemples d'utilisation ===\n")

    print("1. API Error Handling:")
    example_api_error_handling()
    print()

    print("2. Validation Error:")
    example_validation_error()
    print()

    print("3. Configuration Error:")
    example_configuration_error()
    print()

    print("4. Database Error:")
    example_database_error()
    print()

    print("5. Authentication Error:")
    example_authentication_error()
    print()

    print("6. Network Error:")
    example_network_error()
    print()

    print("7. Exception Serialization:")
    example_exception_serialization()
    print()

    print("8. Hierarchical Exception Handling:")
    example_hierarchical_exception_handling()
    print()

    print("9. Decorator Usage:")
    try:
        result = example_api_function()
        print(f"API function result: {result}")
    except Exception as e:
        print(f"API function error: {e}")

    try:
        result = example_sync_function()
        print(f"Sync function result: {result}")
    except Exception as e:
        print(f"Sync function error: {e}")


if __name__ == "__main__":
    run_all_examples()
