"""
Module examples pour le module core.

Ce module contient des exemples d'utilisation des composants du module core :
- Cache avancé
- Gestionnaire de mémoire
- Métriques de synchronisation
- Orchestrateur de synchronisation
- Système de retry
"""

from .cache_example import (
    example_cache_basic_usage,
    example_ttl_expiration,
    example_cache_invalidation,
    example_performance_metrics,
    example_persistent_cache,
    example_cache_eviction
)

from .memory_example import (
    example_memory_basic_usage,
    example_memory_pressure,
    example_scope_management,
    example_metrics_detailed,
    example_integration_with_sync
)

from .metrics_example import (
    example_metrics_basic_usage,
    example_detailed_metrics,
    example_performance_monitoring,
    example_error_tracking,
    example_export_and_analysis,
    example_memory_monitoring
)

from .orchestrator_example import (
    example_orchestrator_basic_usage,
    example_multiple_scopes,
    example_all_scopes,
    example_error_handling
)

from .retry_example import (
    example_basic_retry,
    example_different_strategies,
    example_decorators,
    example_fatal_error_handling,
    example_metrics_analysis,
    example_integration_with_metrics,
    example_custom_retryable_exceptions
)

from .exception_examples import (
    example_api_error_handling,
    example_validation_error,
    example_configuration_error,
    example_database_error,
    example_authentication_error,
    example_network_error,
    example_api_function,
    example_sync_function,
    example_exception_serialization,
    example_hierarchical_exception_handling,
    run_all_examples
)

__all__ = [
    # Cache examples
    "example_cache_basic_usage",
    "example_ttl_expiration",
    "example_cache_invalidation",
    "example_performance_metrics",
    "example_persistent_cache",
    "example_cache_eviction",
    
    # Memory examples
    "example_memory_basic_usage",
    "example_memory_pressure",
    "example_scope_management",
    "example_metrics_detailed",
    "example_integration_with_sync",
    
    # Metrics examples
    "example_metrics_basic_usage",
    "example_detailed_metrics",
    "example_performance_monitoring",
    "example_error_tracking",
    "example_export_and_analysis",
    "example_memory_monitoring",
    
    # Orchestrator examples
    "example_orchestrator_basic_usage",
    "example_multiple_scopes",
    "example_all_scopes",
    "example_error_handling",
    
    # Retry examples
    "example_basic_retry",
    "example_different_strategies",
    "example_decorators",
    "example_fatal_error_handling",
    "example_metrics_analysis",
    "example_integration_with_metrics",
    "example_custom_retryable_exceptions",
    
    # Exception examples
    "example_api_error_handling",
    "example_validation_error",
    "example_configuration_error",
    "example_database_error",
    "example_authentication_error",
    "example_network_error",
    "example_api_function",
    "example_sync_function",
    "example_exception_serialization",
    "example_hierarchical_exception_handling",
    "run_all_examples"
]
