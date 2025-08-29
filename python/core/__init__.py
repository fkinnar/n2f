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
from .registry import (
    SyncRegistry,
    RegistryEntry,
    get_registry,
    register_scope
)
from .orchestrator import (
    SyncOrchestrator,
    ContextBuilder,
    ScopeExecutor,
    LogManager,
    SyncResult
)
from .cache import (
    AdvancedCache,
    CacheEntry,
    CacheMetrics,
    get_cache,
    cache_get,
    cache_set,
    cache_invalidate,
    cache_clear,
    cache_stats
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

    # Registry
    "SyncRegistry",
    "RegistryEntry",
    "get_registry",
    "register_scope",

    # Orchestrator
    "SyncOrchestrator",
    "ContextBuilder",
    "ScopeExecutor",
    "LogManager",
    "SyncResult",

    # Cache
    "AdvancedCache",
    "CacheEntry",
    "CacheMetrics",
    "get_cache",
    "cache_get",
    "cache_set",
    "cache_invalidate",
    "cache_clear",
    "cache_stats",

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
