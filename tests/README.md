# Tests N2F

Ce répertoire contient tous les tests unitaires et d'intégration pour le projet N2F.

## 📁 Structure des tests

### Tests unitaires
- `test_cache.py` - Tests du système de cache
- `test_config.py` - Tests de configuration
- `test_exceptions.py` - Tests des exceptions personnalisées
- `test_metrics.py` - Tests des métriques
- `test_orchestrator.py` - Tests de l'orchestrateur
- `test_retry.py` - Tests du système de retry
- `test_synchronizers.py` - Tests des synchroniseurs

### Tests d'intégration
- `test_integration.py` - Tests d'intégration généraux
- `test_real_scenarios.py` - Tests de scénarios réels

## 🧪 Exécution des tests

### Tous les tests
```bash
python tests/run_tests.py
```

### Tests spécifiques
```bash
python tests/run_tests.py --module tests.test_orchestrator
```

### Lister les tests disponibles
```bash
python tests/run_tests.py --list
```

## 📊 Couverture des tests

### Tests unitaires (156/156 ✅)
- ✅ **Cache** : 20/20 tests réussis
- ✅ **Configuration** : 25/25 tests réussis  
- ✅ **Exceptions** : 15/15 tests réussis
- ✅ **Métriques** : 15/15 tests réussis
- ✅ **Orchestrateur** : 25/25 tests réussis
- ✅ **Retry** : 35/35 tests réussis
- ✅ **Synchroniseurs** : 21/21 tests réussis

### Tests d'intégration (9/33 ⚠️)
- ⚠️ **Intégration générale** : 6/13 tests réussis
- ⚠️ **Scénarios réels** : 3/20 tests réussis

**Total : 165/189 tests réussis (87.3%)**

## 🔧 Configuration

Les tests utilisent des configurations mockées et des données de test pour éviter les dépendances externes.

### Variables d'environnement de test
- `AGRESSO_DB_USER` : Utilisateur de test
- `AGRESSO_DB_PASSWORD` : Mot de passe de test
- `N2F_CLIENT_ID` : Client ID de test
- `N2F_CLIENT_SECRET` : Client secret de test

## 📝 Notes de développement

### Tests d'intégration
Les tests d'intégration simulent des scénarios réels avec :
- Données utilisateurs réalistes
- Données d'axes personnalisés
- Tests de performance
- Tests de récupération d'erreur
- Tests de charge

### Mocking
Les tests utilisent des mocks pour :
- Base de données Agresso
- API N2F
- Système de cache
- Gestionnaire de mémoire
- Métriques

## 🚀 Améliorations futures

1. **Correction des tests d'intégration** - Résoudre les problèmes de mocking
2. **Tests de performance** - Ajouter des benchmarks
3. **Tests de sécurité** - Tests d'authentification et autorisation
4. **Tests de compatibilité** - Tests avec différentes versions d'API
