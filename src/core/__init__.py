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
    create_default_config,
)
from .registry import SyncRegistry, RegistryEntry, get_registry, register_scope
from .orchestrator import (
    SyncOrchestrator,
    ContextBuilder,
    ScopeExecutor,
    LogManager,
    SyncResult,
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
    cache_stats,
)

# Examples module
from .examples import *
from .context import SyncContext
from .logging import add_api_logging_columns, export_api_logs
from .memory_manager import (
    MemoryManager,
    DataFrameInfo,
    MemoryMetrics,
    get_memory_manager,
    register_dataframe,
    get_dataframe,
    cleanup_scope,
    cleanup_all,
    print_memory_summary,
    get_memory_stats,
)
from .metrics import (
    SyncMetrics,
    OperationMetrics,
    ScopeMetrics,
    get_metrics,
    start_operation,
    end_operation,
    record_memory_usage,
    get_summary,
    print_summary,
    export_metrics,
)
from .retry import (
    RetryConfig,
    RetryStrategy,
    RetryableError,
    FatalError,
    RetryMetrics,
    RetryManager,
    get_retry_manager,
    retry,
    api_retry,
    database_retry,
    execute_with_retry,
    get_retry_metrics,
    reset_retry_metrics,
    print_retry_summary,
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
    handle_sync_exceptions,
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
    # Examples
    # (Tous les exemples sont disponibles via le module examples)
    # Context
    "SyncContext",
    # Logging
    "add_api_logging_columns",
    "export_api_logs",
    # Memory Manager
    "MemoryManager",
    "DataFrameInfo",
    "MemoryMetrics",
    "get_memory_manager",
    "register_dataframe",
    "get_dataframe",
    "cleanup_scope",
    "cleanup_all",
    "print_memory_summary",
    "get_memory_stats",
    # Metrics System
    "SyncMetrics",
    "OperationMetrics",
    "ScopeMetrics",
    "get_metrics",
    "start_operation",
    "end_operation",
    "record_memory_usage",
    "get_summary",
    "print_summary",
    "export_metrics",
    # Retry System
    "RetryConfig",
    "RetryStrategy",
    "RetryableError",
    "FatalError",
    "RetryMetrics",
    "RetryManager",
    "get_retry_manager",
    "retry",
    "api_retry",
    "database_retry",
    "execute_with_retry",
    "get_retry_metrics",
    "reset_retry_metrics",
    "print_retry_summary",
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
