# Module Examples - Core

Ce répertoire contient tous les exemples d'utilisation des composants du module `core`.

## Structure

```
examples/
├── __init__.py              # Exports du module examples
├── cache_example.py         # Exemples d'utilisation du cache avancé
├── memory_example.py        # Exemples d'utilisation du gestionnaire de mémoire
├── metrics_example.py       # Exemples d'utilisation du système de métriques
├── orchestrator_example.py  # Exemples d'utilisation de l'orchestrateur
├── retry_example.py         # Exemples d'utilisation du système de retry
├── exception_examples.py    # Exemples d'utilisation des exceptions personnalisées
└── README.md               # Ce fichier
```

## Utilisation

### Import direct d'une fonction spécifique

```python
from core.examples import example_cache_basic_usage
from core.examples import example_memory_basic_usage
from core.examples import example_metrics_basic_usage
```

### Import du module complet

```python
import core.examples

# Accès à toutes les fonctions d'exemple
core.examples.example_cache_basic_usage()
core.examples.example_memory_basic_usage()
```

### Exécution directe d'un fichier d'exemple

```bash
# Depuis le répertoire racine du projet
python src/core/examples/cache_example.py
python src/core/examples/memory_example.py
```

## Fonctions disponibles

### Cache Examples
- `example_cache_basic_usage()` - Utilisation basique du cache
- `example_ttl_expiration()` - Gestion de l'expiration TTL
- `example_cache_invalidation()` - Invalidation sélective
- `example_performance_metrics()` - Métriques de performance
- `example_persistent_cache()` - Cache persistant
- `example_cache_eviction()` - Éviction automatique

### Memory Examples
- `example_memory_basic_usage()` - Utilisation basique du gestionnaire de mémoire
- `example_memory_pressure()` - Gestion de la pression mémoire
- `example_scope_management()` - Gestion par scope
- `example_metrics_detailed()` - Métriques détaillées
- `example_integration_with_sync()` - Intégration avec la synchronisation

### Metrics Examples
- `example_metrics_basic_usage()` - Utilisation basique du système de métriques
- `example_detailed_metrics()` - Métriques détaillées
- `example_performance_monitoring()` - Monitoring de performance
- `example_error_tracking()` - Suivi des erreurs
- `example_export_and_analysis()` - Export et analyse
- `example_memory_monitoring()` - Monitoring mémoire

### Orchestrator Examples
- `example_orchestrator_basic_usage()` - Utilisation basique de l'orchestrateur
- `example_multiple_scopes()` - Gestion de plusieurs scopes
- `example_all_scopes()` - Gestion de tous les scopes
- `example_error_handling()` - Gestion d'erreur

### Retry Examples
- `example_basic_retry()` - Utilisation basique du retry
- `example_different_strategies()` - Différentes stratégies de retry
- `example_decorators()` - Utilisation des décorateurs
- `example_fatal_error_handling()` - Gestion des erreurs fatales
- `example_metrics_analysis()` - Analyse des métriques de retry
- `example_integration_with_metrics()` - Intégration avec les métriques
- `example_custom_retryable_exceptions()` - Exceptions personnalisées

### Exception Examples
- `example_api_error_handling()` - Gestion d'erreur d'API
- `example_validation_error()` - Gestion d'erreur de validation
- `example_configuration_error()` - Gestion d'erreur de configuration
- `example_database_error()` - Gestion d'erreur de base de données
- `example_authentication_error()` - Gestion d'erreur d'authentification
- `example_network_error()` - Gestion d'erreur réseau
- `example_api_function()` - Fonction API avec gestion d'erreur
- `example_sync_function()` - Fonction de synchronisation avec gestion d'erreur
- `example_exception_serialization()` - Sérialisation des exceptions
- `example_hierarchical_exception_handling()` - Gestion hiérarchique des exceptions
- `run_all_examples()` - Exécution de tous les exemples

## Notes

- Tous les exemples sont conçus pour être exécutés de manière autonome
- Les exemples utilisent des données simulées et des mocks quand nécessaire
- Chaque exemple peut être exécuté individuellement pour tester une fonctionnalité spécifique
- Les exemples incluent des commentaires détaillés expliquant chaque étape
