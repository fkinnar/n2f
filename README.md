# 🔄 N2F Synchronization Tool

Outil de synchronisation entre Agresso et N2F pour la gestion des utilisateurs,
projets, plaques et sous-posts.

## 📋 Vue d'ensemble

Ce projet permet de synchroniser automatiquement les données entre le système
Agresso et l'API N2F. Il gère la création, mise à jour et suppression d'entités
de manière cohérente et traçable.

### 🎯 Fonctionnalités principales

- ✅ **Synchronisation multi-scopes** : Users, Projects, Plates, Subposts
- ✅ **Gestion d'erreur robuste** : Exceptions personnalisées avec contexte riche
- ✅ **Architecture modulaire** : Classes abstraites pour extensibilité
- ✅ **Logging détaillé** : Export des logs d'API avec métriques
- ✅ **Configuration flexible** : Support dev/prod avec fichiers YAML
- ✅ **Cache intelligent** : Optimisation des performances API
- ✅ **Métriques avancées** : Monitoring des performances et statistiques
- ✅ **Retry automatique** : Gestion intelligente des erreurs réseau

## 🚀 Installation et configuration

### Prérequis

- Python 3.13+
- Accès aux bases de données Agresso
- Credentials N2F API

### Installation

#### Option 1 : Installation automatique (Recommandée)

```bash
# Cloner le repository
git clone <repository-url>
cd n2f

# Lancer le script de setup automatique
setup.bat                    # Windows
# ou
./setup.sh                   # Linux/Mac (à créer)
```

#### Option 2 : Installation manuelle

```bash
# Cloner le repository
git clone <repository-url>
cd n2f

# Créer un environnement virtuel
python -m venv env
source env/bin/activate  # Linux/Mac
# ou
env\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Configuration

#### Configuration du PYTHONPATH

Le projet nécessite l'accès au module `Iris` qui se trouve dans `D:\Users\kinnar\source\repos\common\Python\Packages`.

**Option 1 : Script automatique (Recommandée)**
```bash
# Windows (CMD)
set_env.bat

# Windows (PowerShell)
.\set_env.ps1
```

**Option 2 : Configuration manuelle**
```bash
# Windows (CMD)
set PYTHONPATH=python;D:\Users\kinnar\source\repos\common\Python\Packages

# Windows (PowerShell)
$env:PYTHONPATH="python;D:\Users\kinnar\source\repos\common\Python\Packages"
```

#### Fichiers de configuration

1. **Copier les fichiers de configuration :**

```bash
cp dev.yaml.example dev.yaml
cp prod.yaml.example prod.yaml
```

2. **Configurer les paramètres :**

```yaml
# dev.yaml
database:
  server: "your-agresso-server"
  database: "your-database"
  username: "your-username"
  password: "your-password"

api:
  base_url: "https://api.n2f.com"
  username: "your-n2f-username"
  password: "your-n2f-password"
  sandbox: true
```

## 🎯 Utilisation

### Synchronisation complète

```bash
# Synchroniser tous les scopes
python python/sync-agresso-n2f.py --all

# Synchroniser des scopes spécifiques
python python/sync-agresso-n2f.py --scopes users projects

# Synchroniser en mode production
python python/sync-agresso-n2f.py --config prod.yaml --scopes users
```

### Options disponibles

```bash
python python/sync-agresso-n2f.py --help

Options:
  --config FILE          Fichier de configuration (dev.yaml par défaut)
  --scopes SCOPE1,SCOPE2 Scopes à synchroniser
  --all                  Synchroniser tous les scopes
  --clear-cache          Vider le cache avant synchronisation
  --invalidate-cache     Invalider le cache
  --verbose              Mode verbeux
```

### Exemples d'utilisation

```bash
# Synchronisation rapide des utilisateurs
python python/sync-agresso-n2f.py --scopes users

# Synchronisation complète avec cache vidé
python python/sync-agresso-n2f.py --all --clear-cache

# Synchronisation en production
python python/sync-agresso-n2f.py --config prod.yaml --scopes users,projects
```

### Scripts batch (Windows)

Le projet inclut des scripts batch pour faciliter l'utilisation :

#### **setup.bat** - Installation automatique

```bash
# Crée l'environnement virtuel et installe les requirements
setup.bat
```

#### **sync_n2f.bat** - Synchronisation avec gestion automatique

```bash
# Lance la synchronisation avec vérification automatique des requirements
sync_n2f.bat

# Avec options
sync_n2f.bat --scopes users,projects
sync_n2f.bat --all --clear-cache
```

**Avantages des scripts batch :**

- ✅ **Vérification automatique** de l'environnement virtuel
- ✅ **Installation automatique** des requirements si manquants
- ✅ **Gestion des erreurs** avec messages clairs
- ✅ **Logs automatiques** avec horodatage
- ✅ **Ouverture automatique** des logs en cas d'erreur

## 🏗️ Architecture

### Structure du projet

```text
n2f/
├── python/
│   ├── core/                   # Composants principaux
│   │   ├── config.py           # Configuration centralisée
│   │   ├── exceptions.py       # Hiérarchie d'exceptions
│   │   ├── orchestrator.py     # Orchestrator principal
│   │   ├── cache.py            # Système de cache
│   │   ├── metrics.py          # Métriques et monitoring
│   │   └── retry.py            # Système de retry
│   ├── business/
│   │   └── process/            # Logique métier
│   │       ├── base_synchronizer.py
│   │       ├── user_synchronizer.py
│   │       └── axe_synchronizer.py
│   ├── n2f/                    # Client API N2F
│   └── agresso/                # Accès base Agresso
├── tests/                      # Tests unitaires
├── scripts/                    # Scripts utilitaires
├── docs/                       # Documentation
├── dev.yaml                    # Configuration développement
├── prod.yaml                   # Configuration production
└── requirements.txt            # Dépendances Python
```

### Composants principaux

#### **EntitySynchronizer** (Classe abstraite)

Classe de base pour toutes les synchronisations d'entités :

```python
class EntitySynchronizer(ABC):
    def create_entities(self, df_agresso, df_n2f) -> Tuple[pd.DataFrame, str]
    def update_entities(self, df_agresso, df_n2f) -> Tuple[pd.DataFrame, str]
    def delete_entities(self, df_agresso, df_n2f) -> Tuple[pd.DataFrame, str]

    @abstractmethod
    def build_payload(self, entity) -> Dict[str, Any]
    @abstractmethod
    def get_entity_id(self, entity) -> str
```

#### **SyncOrchestrator**

Orchestrateur principal gérant l'exécution des synchronisations :

```python
class SyncOrchestrator:
    def __init__(self, config: SyncConfig)
    def run(self, scopes: List[str], clear_cache: bool = False) -> SyncResult
```

#### **AdvancedCache**

Système de cache intelligent avec persistance :

```python
class AdvancedCache:
    def get(self, key: str) -> Optional[Any]
    def set(self, key: str, value: Any, ttl: int = None) -> None
    def invalidate(self, pattern: str) -> None
```

## 📊 Monitoring et métriques

### Métriques collectées

- **Durée des opérations** : Temps d'exécution par scope
- **Taux de succès** : Pourcentage d'opérations réussies
- **Appels API** : Nombre et durée des appels à l'API N2F
- **Cache hits/misses** : Efficacité du cache
- **Utilisation mémoire** : Consommation RAM par scope

### Export des métriques

```bash
# Les métriques sont automatiquement exportées
# Format : metrics_YYYYMMDD_HHMMSS.json
```

### Exemple de métriques

```json
{
  "timestamp": "2025-08-28T15:30:00",
  "duration": 45.2,
  "scopes": {
    "users": {
      "duration": 12.5,
      "success_rate": 100.0,
      "records_processed": 150,
      "api_calls": 25,
      "cache_hits": 18
    }
  }
}
```

## 🧪 Tests

### Exécution des tests

```bash
# Tous les tests
python tests/run_tests.py

# Tests spécifiques
python tests/run_tests.py test_exceptions
python tests/run_tests.py test_synchronizers

# Lister les tests disponibles
python tests/run_tests.py --list
```

### Couverture des tests

- ✅ **Tests d'exceptions** : Hiérarchie complète
- 🔄 **Tests de synchronisation** : En cours
- 🔄 **Tests de configuration** : En cours
- ⏳ **Tests d'intégration** : À implémenter

## 🔧 Développement

### Ajouter un nouveau scope

1. **Créer le synchronizer :**

```python
# python/business/process/new_entity_synchronizer.py
class NewEntitySynchronizer(EntitySynchronizer):
    def build_payload(self, entity):
        return {"name": entity["name"], "type": "new_entity"}

    def get_entity_id(self, entity):
        return entity["id"]
```

1. **Enregistrer le scope :**

```python
# python/business/process/new_entity.py
def synchronize_new_entities(context, sql_filename):
    synchronizer = NewEntitySynchronizer(context.n2f_client, context.sandbox, "new_entities")
    return synchronizer.synchronize(context, sql_filename)

# Auto-découverte automatique
```

### Scripts utilitaires

```bash
# Vérification Markdown
python scripts/check_markdown.py

# Correction automatique Markdown
python scripts/fix_markdown.py
```

## 📝 Logs et debugging

### Niveaux de log

- **INFO** : Opérations normales
- **WARNING** : Problèmes non critiques
- **ERROR** : Erreurs de synchronisation
- **DEBUG** : Informations détaillées

### Fichiers de log

- `logs/sync_YYYYMMDD_HHMMSS.log` : Logs de synchronisation
- `logs/api_logs_YYYYMMDD_HHMMSS.log.csv` : Logs détaillés API

### Mode debug

```bash
python python/sync-agresso-n2f.py --verbose --scopes users
```

## 🤝 Contribution

### Standards de code

- **PEP 8** : Style de code Python
- **Type hints** : Annotations de types obligatoires
- **Docstrings** : Documentation des fonctions
- **Tests unitaires** : Couverture minimale 80%

### Workflow Git

1. Créer une branche feature : `git checkout -b feature/nouvelle-fonctionnalite`
2. Développer et tester
3. Vérifier les fichiers Markdown : `python scripts/check_markdown.py`
4. Créer une pull request

## 📄 Licence

Ce projet est propriétaire et confidentiel.

---

*Dernière mise à jour : 28 août 2025*
*Version : 1.0*
