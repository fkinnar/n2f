# Module Examples - Core

Ce rÃ©pertoire contient tous les exemples d'utilisation des composants du module `core`.

## Structure

```text
examples/
â”œâ”€â”€ __init__.py              # Exports du module examples
â”œâ”€â”€ cache_example.py         # Exemples d'utilisation du cache avancÃ©
â”œâ”€â”€ memory_example.py        # Exemples d'utilisation du gestionnaire de mÃ©moire
â”œâ”€â”€ metrics_example.py       # Exemples d'utilisation du systÃ¨me de mÃ©triques
â”œâ”€â”€ orchestrator_example.py  # Exemples d'utilisation de l'orchestrateur
â”œâ”€â”€ retry_example.py         # Exemples d'utilisation du systÃ¨me de retry
â”œâ”€â”€ exception_examples.py    # Exemples d'utilisation des exceptions personnalisÃ©es
â””â”€â”€ README.md               # Ce fichier
```

## Utilisation

### Import direct d'une fonction spÃ©cifique

```python
from core.examples import example_cache_basic_usage
from core.examples import example_memory_basic_usage
from core.examples import example_metrics_basic_usage
```

### Import du module complet

```python
import core.examples

# AccÃ¨s Ã  toutes les fonctions d'exemple
core.examples.example_cache_basic_usage()
core.examples.example_memory_basic_usage()
```

### ExÃ©cution directe d'un fichier d'exemple

```bash
# Depuis le rÃ©pertoire racine du projet
python src/core/examples/cache_example.py
python src/core/examples/memory_example.py
```

## Fonctions disponibles

### Cache Examples

- `example_cache_basic_usage()` - Utilisation basique du cache
- `example_ttl_expiration()` - Gestion de l'expiration TTL
- `example_cache_invalidation()` - Invalidation sÃ©lective
- `example_performance_metrics()` - MÃ©triques de performance
- `example_persistent_cache()` - Cache persistant
- `example_cache_eviction()` - Ã‰viction automatique

### Memory Examples

- `example_memory_basic_usage()` - Utilisation basique du gestionnaire de mÃ©moire
- `example_memory_pressure()` - Gestion de la pression mÃ©moire
- `example_scope_management()` - Gestion par scope
- `example_metrics_detailed()` - MÃ©triques dÃ©taillÃ©es
- `example_integration_with_sync()` - IntÃ©gration avec la synchronisation

### Metrics Examples

- `example_metrics_basic_usage()` - Utilisation basique du systÃ¨me de mÃ©triques
- `example_detailed_metrics()` - MÃ©triques dÃ©taillÃ©es
- `example_performance_monitoring()` - Monitoring de performance
- `example_error_tracking()` - Suivi des erreurs
- `example_export_and_analysis()` - Export et analyse
- `example_memory_monitoring()` - Monitoring mÃ©moire

### Orchestrator Examples

- `example_orchestrator_basic_usage()` - Utilisation basique de l'orchestrateur
- `example_multiple_scopes()` - Gestion de plusieurs scopes
- `example_all_scopes()` - Gestion de tous les scopes
- `example_error_handling()` - Gestion d'erreur

### Retry Examples

- `example_basic_retry()` - Utilisation basique du retry
- `example_different_strategies()` - DiffÃ©rentes stratÃ©gies de retry
- `example_decorators()` - Utilisation des dÃ©corateurs
- `example_fatal_error_handling()` - Gestion des erreurs fatales
- `example_metrics_analysis()` - Analyse des mÃ©triques de retry
- `example_integration_with_metrics()` - IntÃ©gration avec les mÃ©triques
- `example_custom_retryable_exceptions()` - Exceptions personnalisÃ©es

### Exception Examples

- `example_api_error_handling()` - Gestion d'erreur d'API
- `example_validation_error()` - Gestion d'erreur de validation
- `example_configuration_error()` - Gestion d'erreur de configuration
- `example_database_error()` - Gestion d'erreur de base de donnÃ©es
- `example_authentication_error()` - Gestion d'erreur d'authentification
- `example_network_error()` - Gestion d'erreur rÃ©seau
- `example_api_function()` - Fonction API avec gestion d'erreur
- `example_sync_function()` - Fonction de synchronisation avec gestion d'erreur
- `example_exception_serialization()` - SÃ©rialisation des exceptions
- `example_hierarchical_exception_handling()` - Gestion hiÃ©rarchique des exceptions
- `run_all_examples()` - ExÃ©cution de tous les exemples

## Notes

- Tous les exemples sont conÃ§us pour Ãªtre exÃ©cutÃ©s de maniÃ¨re autonome
- Les exemples utilisent des donnÃ©es simulÃ©es et des mocks quand nÃ©cessaire
- Chaque exemple peut Ãªtre exÃ©cutÃ© individuellement pour tester une fonctionnalitÃ©
  spÃ©cifique
- Les exemples incluent des commentaires dÃ©taillÃ©s expliquant chaque Ã©tape
