# ðŸ”„ N2F Synchronization Tool

Outil de synchronisation entre Agresso et N2F pour la gestion des utilisateurs, projets,
plaques et sous-posts.

## ðŸ“‹ Vue d'ensemble

Ce projet permet de synchroniser automatiquement les donnÃ©es entre le systÃ¨me Agresso
et l'API N2F. Il gÃ¨re la crÃ©ation, mise Ã  jour et suppression d'entitÃ©s de maniÃ¨re
cohÃ©rente et traÃ§able.

### ðŸŽ¯ FonctionnalitÃ©s principales

- âœ… **Synchronisation multi-scopes** : Users, Projects, Plates, Subposts
- âœ… **Gestion d'erreur robuste** : Exceptions personnalisÃ©es avec contexte riche
- âœ… **Architecture modulaire** : Classes abstraites pour extensibilitÃ©
- âœ… **Logging dÃ©taillÃ©** : Export des logs d'API avec mÃ©triques
- âœ… **Configuration flexible** : Support dev/prod avec fichiers YAML
- âœ… **Cache intelligent** : Optimisation des performances API
- âœ… **MÃ©triques avancÃ©es** : Monitoring des performances et statistiques
- âœ… **Retry automatique** : Gestion intelligente des erreurs rÃ©seau

## ðŸš€ Installation et configuration

### PrÃ©requis

- Python 3.13+
- AccÃ¨s aux bases de donnÃ©es Agresso
- Credentials N2F API

### Installation

#### Option 1 : Installation automatique (RecommandÃ©e)

```bash
# Cloner le repository
git clone <repository-url>
cd n2f

# Lancer le script de setup automatique
setup.bat                    # Windows
# ou
./setup.sh                   # Linux/Mac (Ã  crÃ©er)
```

#### Option 2 : Installation manuelle

```bash
# Cloner le repository
git clone <repository-url>
cd n2f

# CrÃ©er un environnement virtuel
python -m venv env
source env/bin/activate  # Linux/Mac
# ou
env\Scripts\activate     # Windows

# Installer les dÃ©pendances
pip install -r requirements.txt
```

### Configuration

#### Configuration du PYTHONPATH

Le projet nÃ©cessite l'accÃ¨s au module `Iris` qui se trouve dans
`D:\Users\kinnar\source\repos\common\Python\Packages`.

##### Option 1 : Script automatique (RecommandÃ©e)

```bash
# Windows (CMD)
set_env.bat

# Windows (PowerShell)
.\set_env.ps1
```

##### Option 2 : Configuration manuelle

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

1. **Configurer les paramÃ¨tres :**

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

## ðŸŽ¯ Utilisation

### Synchronisation complÃ¨te

```bash
# Synchroniser tous les scopes
python python/sync-agresso-n2f.py --all

# Synchroniser des scopes spÃ©cifiques
python python/sync-agresso-n2f.py --scopes users projects

# Synchroniser en mode production
python python/sync-agresso-n2f.py --config prod.yaml --scopes users
```

### Options disponibles

```bash
python python/sync-agresso-n2f.py --help

Options:
  --config FILE          Fichier de configuration (dev.yaml par dÃ©faut)
  --scopes SCOPE1,SCOPE2 Scopes Ã  synchroniser
  --all                  Synchroniser tous les scopes
  --clear-cache          Vider le cache avant synchronisation
  --invalidate-cache     Invalider le cache
  --verbose              Mode verbeux
```

### Exemples d'utilisation

```bash
# Synchronisation rapide des utilisateurs
python python/sync-agresso-n2f.py --scopes users

# Synchronisation complÃ¨te avec cache vidÃ©
python python/sync-agresso-n2f.py --all --clear-cache

# Synchronisation en production
python python/sync-agresso-n2f.py --config prod.yaml --scopes users,projects
```

### Scripts batch (Windows)

Le projet inclut des scripts batch pour faciliter l'utilisation :

#### **setup.bat** - Installation automatique

```bash
# CrÃ©e l\'environnement virtuel et installe les requirements
setup.bat
```

#### **sync_n2f.bat** - Synchronisation avec gestion automatique

```bash
# Lance la synchronisation avec vÃ©rification automatique des requirements
sync_n2f.bat

# Avec options
sync_n2f.bat --scopes users,projects
sync_n2f.bat --all --clear-cache
```

**Avantages des scripts batch :**

- âœ… **VÃ©rification automatique** de l'environnement virtuel
- âœ… **Installation automatique** des requirements si manquants
- âœ… **Gestion des erreurs** avec messages clairs
- âœ… **Logs automatiques** avec horodatage
- âœ… **Ouverture automatique** des logs en cas d'erreur

## ðŸ—ï¸ Architecture

### Structure du projet

```text
n2f/
â”œâ”€â”€ python/
â”‚   â”œâ”€â”€ core/                   # Composants principaux
â”‚   â”‚   â”œâ”€â”€ config.py           # Configuration centralisÃ©e
â”‚   â”‚   â”œâ”€â”€ exceptions.py       # HiÃ©rarchie d\'exceptions
â”‚   â”‚   â”œâ”€â”€ orchestrator.py     # Orchestrator principal
â”‚   â”‚   â”œâ”€â”€ cache.py            # SystÃ¨me de cache
â”‚   â”‚   â”œâ”€â”€ metrics.py          # MÃ©triques et monitoring
â”‚   â”‚   â””â”€â”€ retry.py            # SystÃ¨me de retry
â”‚   â”œâ”€â”€ business/
â”‚   â”‚   â””â”€â”€ process/            # Logique mÃ©tier
â”‚   â”‚       â”œâ”€â”€ base_synchronizer.py
â”‚   â”‚       â”œâ”€â”€ user_synchronizer.py
â”‚   â”‚       â””â”€â”€ axe_synchronizer.py
â”‚   â”œâ”€â”€ n2f/                    # Client API N2F
â”‚   â””â”€â”€ agresso/                # AccÃ¨s base Agresso
â”œâ”€â”€ tests/                      # Tests unitaires
â”œâ”€â”€ scripts/                    # Scripts utilitaires
â”œâ”€â”€ docs/                       # Documentation
â”œâ”€â”€ dev.yaml                    # Configuration dÃ©veloppement
â”œâ”€â”€ prod.yaml                   # Configuration production
â””â”€â”€ requirements.txt            # DÃ©pendances Python
```

### Composants principaux

#### **EntitySynchronizer** (Classe abstraite)

Classe de base pour toutes les synchronisations d'entitÃ©s :

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

Orchestrateur principal gÃ©rant l'exÃ©cution des synchronisations :

```python
class SyncOrchestrator:
    def __init__(self, config: SyncConfig)
    def run(self, scopes: List[str], clear_cache: bool = False) -> SyncResult
```

#### **AdvancedCache**

SystÃ¨me de cache intelligent avec persistance :

```python
class AdvancedCache:
    def get(self, key: str) -> Optional[Any]
    def set(self, key: str, value: Any, ttl: int = None) -> None
    def invalidate(self, pattern: str) -> None
```

## ðŸ“Š Monitoring et mÃ©triques

### MÃ©triques collectÃ©es

- **DurÃ©e des opÃ©rations** : Temps d'exÃ©cution par scope
- **Taux de succÃ¨s** : Pourcentage d'opÃ©rations rÃ©ussies
- **Appels API** : Nombre et durÃ©e des appels Ã  l'API N2F
- **Cache hits/misses** : EfficacitÃ© du cache
- **Utilisation mÃ©moire** : Consommation RAM par scope

### Export des mÃ©triques

```bash
# Les mÃ©triques sont automatiquement exportÃ©es
# Format : metrics_YYYYMMDD_HHMMSS.json
```

### Exemple de mÃ©triques

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

## ðŸ§ª Tests

### ExÃ©cution des tests

```bash
# Tous les tests
python tests/run_tests.py

# Tests spÃ©cifiques
python tests/run_tests.py test_exceptions
python tests/run_tests.py test_synchronizers

# Lister les tests disponibles
python tests/run_tests.py --list
```

### Couverture des tests

- âœ… **Tests d'exceptions** : HiÃ©rarchie complÃ¨te
- ðŸ”„ **Tests de synchronisation** : En cours
- ðŸ”„ **Tests de configuration** : En cours
- â³ **Tests d'intÃ©gration** : Ã€ implÃ©menter

## ðŸ”§ DÃ©veloppement

### Ajouter un nouveau scope

1. **CrÃ©er le synchronizer :**

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

# Auto-dÃ©couverte automatique
```

### Scripts utilitaires

```bash
# VÃ©rification Markdown
python scripts/check_markdown.py

# Correction automatique Markdown
python scripts/fix_markdown.py
```

## ðŸ“ Logs et debugging

### Niveaux de log

- **INFO** : OpÃ©rations normales
- **WARNING** : ProblÃ¨mes non critiques
- **ERROR** : Erreurs de synchronisation
- **DEBUG** : Informations dÃ©taillÃ©es

### Fichiers de log

- `logs/sync_YYYYMMDD_HHMMSS.log` : Logs de synchronisation
- `logs/api_logs_YYYYMMDD_HHMMSS.log.csv` : Logs dÃ©taillÃ©s API

### Mode debug

```bash
python python/sync-agresso-n2f.py --verbose --scopes users
```

## ðŸ¤ Contribution

### Standards de code

- **PEP 8** : Style de code Python
- **Type hints** : Annotations de types obligatoires
- **Docstrings** : Documentation des fonctions
- **Tests unitaires** : Couverture minimale 80%

### Workflow Git

1. CrÃ©er une branche feature : `git checkout -b feature/nouvelle-fonctionnalite`
1. DÃ©velopper et tester
1. VÃ©rifier les fichiers Markdown : `python scripts/check_markdown.py`
1. CrÃ©er une pull request

## ðŸ“„ Licence

Ce projet est propriÃ©taire et confidentiel.

______________________________________________________________________

*DerniÃ¨re mise Ã  jour : 28 aoÃ»t 2025* *Version : 1.0*

## Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality:

- **Black**: Automatic code formatting
- **Trailing whitespace**: Removes trailing spaces
- **End of file**: Ensures files end with newline
- **YAML validation**: Checks YAML syntax
- **Large files**: Prevents large files from being committed
- **Merge conflicts**: Detects unresolved merge conflicts

For detailed configuration and usage, see [PRE_COMMIT_HOOKS.md](PRE_COMMIT_HOOKS.md).

Test line for pre-commit hooks.

## Development Setup

### Installing Development Dependencies

```bash
# Install all development dependencies
python -m pip install -e ".[dev]"

# Or use the requirements file
python -m pip install -r requirements-dev.txt
```

**Note**: After installing dev dependencies, run `pre-commit install` to set up Git
hooks.

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality:

- **Black**: Automatic code formatting
- **Trailing whitespace**: Removes trailing spaces
- **End of file**: Ensures files end with newline
- **YAML validation**: Checks YAML syntax
- **Large files**: Prevents large files from being committed
- **Merge conflicts**: Detects unresolved merge conflicts

For detailed configuration and usage, see [PRE_COMMIT_HOOKS.md](PRE_COMMIT_HOOKS.md).
