# 🧪 Tests Unitaires - N2F Synchronization

Ce répertoire contient tous les tests unitaires pour le projet de synchronisation N2F.

## 📋 Structure des Tests

```
tests/
├── __init__.py              # Package tests
├── run_tests.py             # Script principal d'exécution
├── README.md               # Ce fichier
├── test_exceptions.py      # Tests pour la hiérarchie d'exceptions
├── test_synchronizers.py   # Tests pour les synchroniseurs
└── test_config.py          # Tests pour la configuration
```

## 🚀 Exécution des Tests

### Exécuter tous les tests

```bash
# Depuis la racine du projet
python tests/run_tests.py

# Ou depuis le répertoire tests
python run_tests.py
```

### Lister tous les modules de test

```bash
python tests/run_tests.py list
```

### Exécuter un module de test spécifique

```bash
python tests/run_tests.py run test_exceptions
python tests/run_tests.py run test_synchronizers
python tests/run_tests.py run test_config
```

### Exécuter avec unittest directement

```bash
# Tous les tests
python -m unittest discover tests

# Module spécifique
python -m unittest tests.test_exceptions
python -m unittest tests.test_synchronizers
python -m unittest tests.test_config

# Test spécifique
python -m unittest tests.test_exceptions.TestSyncException.test_sync_exception_creation
```

## 📊 Couverture des Tests

### ✅ Tests Implémentés

#### 1. **test_exceptions.py**
- ✅ `SyncException` (classe de base)
- ✅ `ApiException` (erreurs d'API)
- ✅ `ValidationException` (erreurs de validation)
- ✅ `ConfigurationException` (erreurs de configuration)
- ✅ `DatabaseException` (erreurs de base de données)
- ✅ `AuthenticationException` (erreurs d'authentification)
- ✅ `NetworkException` (erreurs réseau)
- ✅ Hiérarchie d'exceptions

#### 2. **test_synchronizers.py**
- ✅ `EntitySynchronizer` (classe abstraite)
- ✅ `UserSynchronizer` (synchronisation utilisateurs)
- ✅ `AxeSynchronizer` (synchronisation axes)
- ✅ Opérations CRUD (Create, Read, Update, Delete)
- ✅ Gestion des données vides
- ✅ Gestion des erreurs

#### 3. **test_config.py**
- ✅ `SyncConfig` (configuration principale)
- ✅ `ConfigLoader` (chargement de configuration)
- ✅ `SyncRegistry` (registre des scopes)
- ✅ `RegistryEntry` (entrées du registre)
- ✅ Validation de configuration
- ✅ Découverte automatique des scopes

### 🔄 Tests à Implémenter (Phase 4.2)

#### 4. **test_cache.py** (À créer)
- [ ] `AdvancedCache` (système de cache)
- [ ] `CacheEntry` (entrées de cache)
- [ ] TTL et expiration
- [ ] Persistance
- [ ] Métriques de cache

#### 5. **test_metrics.py** (À créer)
- [ ] `SyncMetrics` (métriques de synchronisation)
- [ ] `OperationMetrics` (métriques d'opération)
- [ ] `ScopeMetrics` (métriques par scope)
- [ ] Export JSON
- [ ] Résumés console

#### 6. **test_retry.py** (À créer)
- [ ] `RetryManager` (gestionnaire de retry)
- [ ] Stratégies de backoff
- [ ] Gestion des erreurs fatales
- [ ] Métriques de retry

#### 7. **test_orchestrator.py** (À créer)
- [ ] `SyncOrchestrator` (orchestrateur principal)
- [ ] `ContextBuilder` (construction du contexte)
- [ ] `ScopeExecutor` (exécution des scopes)
- [ ] `LogManager` (gestion des logs)

#### 8. **test_integration.py** (À créer)
- [ ] Tests d'intégration end-to-end
- [ ] Tests avec base de données simulée
- [ ] Tests avec API simulée
- [ ] Tests de performance

## 🎯 Bonnes Pratiques

### Structure des Tests

```python
class TestComponentName(unittest.TestCase):
    """Tests pour ComponentName."""
    
    def setUp(self):
        """Configuration initiale pour les tests."""
        # Configuration commune à tous les tests de la classe
        pass
    
    def test_method_name(self):
        """Test de la méthode method_name."""
        # Arrange
        # Act
        # Assert
        pass
    
    def tearDown(self):
        """Nettoyage après les tests."""
        # Nettoyage si nécessaire
        pass
```

### Conventions de Nommage

- **Fichiers de test** : `test_<module_name>.py`
- **Classes de test** : `Test<ClassName>`
- **Méthodes de test** : `test_<method_name>_<scenario>`

### Assertions Recommandées

```python
# Égalité
self.assertEqual(actual, expected)
self.assertNotEqual(actual, expected)

# Types
self.assertIsInstance(obj, ClassName)
self.assertIs(type(obj), ClassName)

# Collections
self.assertIn(item, collection)
self.assertNotIn(item, collection)
self.assertTrue(collection)  # Non vide
self.assertFalse(collection)  # Vide

# Exceptions
with self.assertRaises(ExpectedException):
    function_that_should_raise()

# Approximations (pour les nombres à virgule flottante)
self.assertAlmostEqual(actual, expected, places=2)
```

### Mocks et Stubs

```python
from unittest.mock import Mock, patch, MagicMock

# Mock simple
mock_client = Mock()
mock_client.method.return_value = "expected_result"

# Mock avec patch
@patch('module.function_name')
def test_method(self, mock_function):
    mock_function.return_value = "mocked_result"
    # Test code here
```

## 📈 Métriques de Qualité

### Objectifs de Couverture

- **Couverture minimale** : 80%
- **Couverture cible** : 90%
- **Couverture critique** : 95% (pour les composants core)

### Métriques à Suivre

- **Nombre de tests** : Augmentation continue
- **Temps d'exécution** : < 30 secondes pour tous les tests
- **Taux de succès** : 100% en conditions normales
- **Complexité cyclomatique** : < 10 par méthode

## 🔧 Configuration

### Variables d'Environnement

```bash
# Pour les tests
export TESTING=True
export TEST_DATABASE_URL="sqlite:///test.db"
export TEST_API_BASE_URL="https://api-test.n2f.com"
```

### Fichiers de Configuration de Test

```yaml
# tests/test_config.yaml
database:
  host: "localhost"
  port: 1433
  database: "TEST_DB"

n2f:
  base_urls: "https://api-test.n2f.com"
  simulate: true

scopes:
  users:
    sql_filename: "test_users.sql"
    sql_column_filter: "test = 1"
```

## 🚨 Dépannage

### Problèmes Courants

1. **ImportError** : Vérifier que le path Python inclut le répertoire `python/`
2. **ModuleNotFoundError** : Vérifier que tous les modules sont installés
3. **AssertionError** : Vérifier les données de test et les assertions

### Debug des Tests

```python
# Ajouter des prints pour debug
def test_method(self):
    result = some_function()
    print(f"DEBUG: result = {result}")
    self.assertEqual(result, expected)
```

### Tests en Mode Verbose

```bash
python -m unittest -v tests.test_exceptions
```

## 📚 Ressources

- [Documentation unittest](https://docs.python.org/3/library/unittest.html)
- [Documentation mock](https://docs.python.org/3/library/unittest.mock.html)
- [Best Practices for Testing](https://realpython.com/python-testing/)

---

**Dernière mise à jour** : 28 août 2025  
**Version** : 1.0
