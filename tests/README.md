# Tests Unitaires - Projet N2F

## Vue d'ensemble

Ce répertoire contient tous les tests unitaires du projet N2F. La suite de tests
comprend **446 tests** qui couvrent les fonctionnalités principales du système de
synchronisation Agresso-N2F.

## Exécution des Tests

### Tous les tests

```bash
python tests/run_tests.py
```

### Tests spécifiques

```bash
python tests/run_tests.py --module test_config
```

### Lister tous les tests disponibles

```bash
python tests/run_tests.py --list
```

## Analyse de Couverture

### Exécuter l'analyse de couverture

```bash
python tests/run_coverage_simple.py
```

### Analyse détaillée avec lignes manquantes

```bash
python tests/run_coverage_simple.py --detailed
```

### Générer un rapport HTML

```bash
python tests/run_coverage_simple.py --html
```

Le rapport HTML sera généré dans le dossier `coverage_html/`.

## Couverture Actuelle

- **Couverture globale :** 66%
- **Lignes de code :** 3,224 lignes
- **Lignes couvertes :** 2,120 lignes
- **Tests exécutés :** 446 tests
- **Taux de réussite :** 100%

## Modules de Test

### Tests de Base

- `test_api_base.py` - Tests de l'API de base
- `test_api_specific.py` - Tests spécifiques de l'API
- `test_client_api.py` - Tests du client API
- `test_config.py` - Tests de configuration

### Tests Métier

- `test_business_modules.py` - Tests des modules métier
- `test_normalize.py` - Tests de normalisation
- `test_process_modules.py` - Tests des modules de traitement

### Tests Core

- `test_cache.py` - Tests du système de cache
- `test_exceptions.py` - Tests des exceptions
- `test_metrics.py` - Tests des métriques
- `test_orchestrator.py` - Tests de l'orchestrateur
- `test_retry.py` - Tests du système de retry

### Tests d'Intégration

- `test_integration.py` - Tests d'intégration
- `test_real_scenarios.py` - Tests de scénarios réels
- `test_sync_agresso_n2f.py` - Tests de synchronisation

## Structure des Tests

Chaque fichier de test suit la convention `test_*.py` et utilise le framework
`unittest` de Python. Les tests sont organisés par module et fonctionnalité.

### Exemple de Structure

```python
import unittest
from unittest.mock import Mock, patch

class TestExample(unittest.TestCase):

    def setUp(self):
        """Configuration initiale pour chaque test"""
        pass

    def test_successful_operation(self):
        """Test d'une opération réussie"""
        # Arrange
        # Act
        # Assert
        pass

    def test_error_handling(self):
        """Test de gestion d'erreur"""
        # Arrange
        # Act
        # Assert
        pass
```

## Bonnes Pratiques

1. **Nommage** : Utilisez des noms descriptifs pour les tests
2. **Isolation** : Chaque test doit être indépendant
3. **Mocking** : Utilisez des mocks pour les dépendances externes
4. **Assertions** : Utilisez des assertions spécifiques
5. **Documentation** : Documentez les cas de test complexes

## Dépendances

Les tests utilisent les dépendances suivantes :

- `unittest` (inclus dans Python)
- `coverage` (pour l'analyse de couverture)
- `mock` (pour le mocking)

## Résolution de Problèmes

### Tests qui échouent

1. Vérifiez les dépendances
2. Vérifiez la configuration
3. Vérifiez les variables d'environnement

### Couverture faible

1. Identifiez les modules avec faible couverture
2. Ajoutez des tests pour les cas manquants
3. Vérifiez les exclusions de couverture

## Contribution

Lors de l'ajout de nouveaux tests :

1. Suivez la convention de nommage
2. Ajoutez des tests pour les nouvelles fonctionnalités
3. Maintenez la couverture de code
4. Documentez les cas de test complexes
