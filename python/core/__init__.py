"""
Module core pour la synchronisation N2F.

Ce module contient les composants fondamentaux de l'architecture :
- Configuration centralisée
- Exceptions personnalisées
- Utilitaires de base
"""

from .config import (
    SyncConfig,
    DatabaseConfig,
    ApiConfig,
    ScopeConfig,
    ConfigLoader,
    create_default_config
)
from .exceptions import (
    SyncException,
    ApiException,
    ValidationException,
    ConfigurationException,
    DatabaseException,
    AuthenticationException,
    NetworkException,
    wrap_api_call,
    handle_sync_exceptions
)

__all__ = [
    # Configuration
    "SyncConfig",
    "DatabaseConfig", 
    "ApiConfig",
    "ScopeConfig",
    "ConfigLoader",
    "create_default_config",
    
    # Exceptions
    "SyncException",
    "ApiException",
    "ValidationException",
    "ConfigurationException",
    "DatabaseException",
    "AuthenticationException",
    "NetworkException",
    "wrap_api_call",
    "handle_sync_exceptions",
]
