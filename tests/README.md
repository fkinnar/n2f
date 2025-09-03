# Tests Unitaires - Projet N2F

## Vue d'ensemble

Ce rÃ©pertoire contient tous les tests unitaires du projet N2F. La suite de tests
comprend **446 tests** qui couvrent les fonctionnalitÃ©s principales du systÃ¨me de
synchronisation Agresso-N2F.

## ExÃ©cution des Tests

### Tous les tests

```bash
python tests/run_tests.py
```

### Tests spÃ©cifiques

```bash
python tests/run_tests.py --module test_config
```

### Lister tous les tests disponibles

```bash
python tests/run_tests.py --list
```

## Analyse de Couverture

### ExÃ©cuter l'analyse de couverture

```bash
python tests/run_coverage_simple.py
```

### Analyse dÃ©taillÃ©e avec lignes manquantes

```bash
python tests/run_coverage_simple.py --detailed
```

### GÃ©nÃ©rer un rapport HTML

```bash
python tests/run_coverage_simple.py --html
```

Le rapport HTML sera gÃ©nÃ©rÃ© dans le dossier `coverage_html/`.

## Couverture Actuelle

- **Couverture globale :** 66%
- **Lignes de code :** 3,224 lignes
- **Lignes couvertes :** 2,120 lignes
- **Tests exÃ©cutÃ©s :** 446 tests
- **Taux de rÃ©ussite :** 100%

## Modules de Test

### Tests de Base

- `test_api_base.py` - Tests de l'API de base
- `test_api_specific.py` - Tests spÃ©cifiques de l'API
- `test_client_api.py` - Tests du client API
- `test_config.py` - Tests de configuration

### Tests MÃ©tier

- `test_business_modules.py` - Tests des modules mÃ©tier
- `test_normalize.py` - Tests de normalisation
- `test_process_modules.py` - Tests des modules de traitement

### Tests Core

- `test_cache.py` - Tests du systÃ¨me de cache
- `test_exceptions.py` - Tests des exceptions
- `test_metrics.py` - Tests des mÃ©triques
- `test_orchestrator.py` - Tests de l'orchestrateur
- `test_retry.py` - Tests du systÃ¨me de retry

### Tests d'IntÃ©gration

- `test_integration.py` - Tests d'intÃ©gration
- `test_real_scenarios.py` - Tests de scÃ©narios rÃ©els
- `test_sync_agresso_n2f.py` - Tests de synchronisation

## Structure des Tests

Chaque fichier de test suit la convention `test_*.py` et utilise le framework `unittest`
de Python. Les tests sont organisÃ©s par module et fonctionnalitÃ©.

### Exemple de Structure

```python
import unittest
from unittest.mock import Mock, patch

class TestExample(unittest.TestCase):

    def setUp(self):
        """Configuration initiale pour chaque test"""
        pass

    def test_successful_operation(self):
        """Test d'une opÃ©ration rÃ©ussie"""
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
1. **Isolation** : Chaque test doit Ãªtre indÃ©pendant
1. **Mocking** : Utilisez des mocks pour les dÃ©pendances externes
1. **Assertions** : Utilisez des assertions spÃ©cifiques
1. **Documentation** : Documentez les cas de test complexes

## DÃ©pendances

Les tests utilisent les dÃ©pendances suivantes :

- `unittest` (inclus dans Python)
- `coverage` (pour l'analyse de couverture)
- `mock` (pour le mocking)

## RÃ©solution de ProblÃ¨mes

### Tests qui Ã©chouent

1. VÃ©rifiez les dÃ©pendances
1. VÃ©rifiez la configuration
1. VÃ©rifiez les variables d'environnement

### Couverture faible

1. Identifiez les modules avec faible couverture
1. Ajoutez des tests pour les cas manquants
1. VÃ©rifiez les exclusions de couverture

## Contribution

Lors de l'ajout de nouveaux tests :

1. Suivez la convention de nommage
1. Ajoutez des tests pour les nouvelles fonctionnalitÃ©s
1. Maintenez la couverture de code
1. Documentez les cas de test complexes
