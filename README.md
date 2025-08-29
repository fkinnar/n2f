# 🔄 N2F Synchronization Tool

Outil de synchronisation entre Agresso et N2F pour la gestion des utilisateurs, projets, plaques et sous-posts.

## 📋 Vue d'ensemble

Ce projet permet de synchroniser automatiquement les données entre le système Agresso et l'API N2F. Il gère la création, mise à jour et suppression d'entités de manière cohérente et traçable.

### 🎯 Fonctionnalités principales

- ✅ **Synchronisation multi-scopes** : Users, Projects, Plates, Subposts

- ✅ **Gestion d'erreur robuste** : Exceptions personnalisées avec contexte riche

- ✅ **Architecture modulaire** : Classes abstraites pour extensibilité

- ✅ **Logging détaillé** : Export des logs d'API avec métriques

- ✅ **Configuration flexible** : Support dev/prod avec fichiers YAML

- ✅ **Cache intelligent** : Optimisation des performances API

## 🚀 Installation et configuration

### Prérequis

- Python 3.13+

- Accès aux bases de données Agresso

- Credentials N2F API

### Installation

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

1. **Variables d'environnement** (`.env`) :

```env
AGRESSO_DB_USER=your_db_user
AGRESSO_DB_PASSWORD=your_db_password
N2F_CLIENT_ID=your_client_id
N2F_CLIENT_SECRET=your_client_secret

```

1. **Fichiers de configuration** :
   - `dev.yaml` : Configuration de développement
   - `prod.yaml` : Configuration de production

## 📖 Utilisation

### Commandes de base

```bash

# Synchronisation complète (create + update)

python python/sync-agresso-n2f.py

# Synchronisation spécifique

python python/sync-agresso-n2f.py --scope users projects

# Actions spécifiques

python python/sync-agresso-n2f.py --create --update --delete

# Configuration spécifique

python python/sync-agresso-n2f.py --config prod

```

### Options disponibles

| Option | Description | Défaut |
|--------|-------------|---------|
| `--create` | Créer les éléments manquants | ✅ (si aucune action spécifiée) |
| `--update` | Mettre à jour les éléments existants | ✅ (si aucune action spécifiée) |
| `--delete` | Supprimer les éléments obsolètes | ❌ |
| `--config` | Fichier de configuration | `dev` |
| `--scope` | Périmètres à synchroniser | `all` |

### Exemples d'utilisation

```bash

# Synchronisation des utilisateurs uniquement

python python/sync-agresso-n2f.py --scope users

# Création uniquement (pas de mise à jour)

python python/sync-agresso-n2f.py --create

# Synchronisation complète en production

python python/sync-agresso-n2f.py --config prod --scope all

# Test en mode simulation

# (modifier simulate: true dans la config)

python python/sync-agresso-n2f.py --config dev

```

## 🏗️ Architecture

### Structure du projet

```text
n2f/
├── python/
│   ├── sync-agresso-n2f.py      # Point d'entrée principal

│   ├── business/
│   │   └── process/
│   │       ├── base_synchronizer.py    # Classe abstraite

│   │       ├── user_synchronizer.py    # Synchronisation users

│   │       ├── axe_synchronizer.py     # Synchronisation axes

│   │       └── helper.py               # Utilitaires

│   ├── n2f/
│   │   ├── client.py            # Client API N2F

│   │   ├── api_result.py        # Résultats d'API

│   │   └── process/             # Logique métier N2F

│   ├── core/
│   │   ├── exceptions.py        # Exceptions personnalisées

│   │   └── exception_examples.py # Exemples d'utilisation

│   └── helper/
│       ├── context.py           # Contexte de synchronisation

│       └── cache.py             # Gestionnaire de cache

├── sql/                         # Requêtes SQL Agresso

├── config/                      # Fichiers de configuration

└── logs/                        # Logs de synchronisation

```

### Composants principaux

#### 1. EntitySynchronizer (Classe abstraite)

Classe de base pour toutes les synchronisations d'entités :

```python
from business.process.base_synchronizer import EntitySynchronizer

class UserSynchronizer(EntitySynchronizer):
    def build_payload(self, entity, df_agresso, df_n2f, df_n2f_companies=None):
        # Logique spécifique aux utilisateurs

        pass

    def get_entity_id(self, entity):
        return entity["AdresseEmail"]

```

#### 2. Gestion d'erreur personnalisée

Hiérarchie d'exceptions pour une gestion d'erreur structurée :

```python
from core.exceptions import ApiException, ValidationException

try:
    # Opération API

    result = client.create_user(payload)
except ApiException as e:
    print(f"Erreur API: {e.message}")
    print(f"Status: {e.status_code}")
    print(f"Endpoint: {e.endpoint}")

```

#### 3. Client API N2F

Client robuste avec gestion du cache et des tokens :

```python
from n2f.client import N2fApiClient

client = N2fApiClient(context)
companies = client.get_companies(use_cache=True)
users = client.get_users(use_cache=True)

```

## 🔧 Configuration

### Fichier de configuration YAML

```yaml

# dev.yaml

agresso:
  sql-filename-users: "get-agresso-n2f-users.dev.sql"
  sql-filename-customaxes: "get-agresso-n2f-customaxes.dev.sql"

n2f:
  base_urls: "https://api-dev.n2f.com"
  simulate: false

database:
  host: "localhost"
  port: 1433
  database: "AGRESSO_DEV"

```

### Variables d'environnement

| Variable | Description | Requis |
|----------|-------------|---------|
| `AGRESSO_DB_USER` | Utilisateur base Agresso | ✅ |
| `AGRESSO_DB_PASSWORD` | Mot de passe base Agresso | ✅ |
| `N2F_CLIENT_ID` | Client ID API N2F | ✅ |
| `N2F_CLIENT_SECRET` | Client Secret API N2F | ✅ |

## 📊 Monitoring et logs

### Logs de synchronisation

Les logs sont automatiquement exportés dans le dossier `logs/` :

- **Format** : `api_logs_YYYYMMDD_HHMMSS.log.csv`

- **Contenu** : Détails de chaque opération API

- **Métriques** : Taux de succès, temps de réponse, erreurs

### Exemple de sortie

```text
--- Starting synchronization for scope : users ---

✅ CREATE - john.doe@example.com - User created successfully

❌ UPDATE - jane.smith@example.com - User not found

--- End of synchronization for scope : users ---

--- API Logs Export ---

API logs exported to : logs/api_logs_20250828_105300.log.csv

API Operations Summary :
  - Success : 45/50
  - Errors : 5/50

```

## 🧪 Tests et développement

### Exécuter les exemples

```bash

# Tester les exceptions personnalisées

python python/core/exception_examples.py

# Tester les synchroniseurs

python python/business/process/sync_example.py

```

### Mode simulation

Pour tester sans affecter les données réelles :

```yaml

# dev.yaml

n2f:
  simulate: true  # Mode simulation activé

```

## 🚨 Gestion d'erreur

### Types d'exceptions

| Exception | Usage | Exemple |
|-----------|-------|---------|
| `ApiException` | Erreurs d'API | Status 404, 500, timeout |
| `ValidationException` | Données invalides | Email mal formaté |
| `ConfigurationException` | Configuration manquante | Variables d'env manquantes |
| `DatabaseException` | Erreurs base de données | Table inexistante |
| `AuthenticationException` | Erreurs d'auth | Token expiré |
| `NetworkException` | Erreurs réseau | Connexion perdue |

### Gestion automatique

Les décorateurs permettent une gestion automatique :

```python
from core.exceptions import wrap_api_call, handle_sync_exceptions

@wrap_api_call
def api_function():
    # Gestion automatique des erreurs d'API

    pass

@handle_sync_exceptions
def sync_function():
    # Gestion automatique des erreurs de synchronisation

    pass

```

## 🔄 Workflow de développement

### Branches

- `main` : Version stable

- `feature-refactor` : Développement en cours

- `dev` : Tests et intégration

### Ajouter un nouveau scope

1. **Créer le synchroniseur** :

```python

# python/business/process/new_entity_synchronizer.py

class NewEntitySynchronizer(EntitySynchronizer):
    # Implémenter les méthodes abstraites

    pass

```

1. **Ajouter la fonction de synchronisation** :

```python

# python/business/process/__init__.py

def synchronize_new_entity(context, sql_filename):
    # Logique de synchronisation

    pass

```

1. **Mettre à jour le mapping** :

```python

# python/sync-agresso-n2f.py

scope_map["new_entity"] = (synchronize_new_entity, sql_filename)

```

## 📈 Métriques et performance

### Optimisations implémentées

- ✅ **Cache intelligent** : Réduction des appels API redondants

- ✅ **Pagination optimisée** : Gestion efficace des gros volumes

- ✅ **Gestion d'erreur robuste** : Retry automatique et fallback

- ✅ **Logging structuré** : Traçabilité complète des opérations

### Monitoring recommandé

- Taux de succès des opérations

- Temps de réponse des APIs

- Volume de données synchronisées

- Erreurs par type et scope

## 🤝 Contribution

### Standards de code

- **Docstrings** : Toutes les fonctions documentées

- **Type hints** : Typage Python complet

- **Exceptions** : Utilisation des exceptions personnalisées

- **Tests** : Couverture de tests pour les nouvelles fonctionnalités

### Processus de contribution

1. Créer une branche feature
2. Implémenter les changements
3. Ajouter/améliorer la documentation
4. Tester avec les données de test
5. Créer une pull request

## 📞 Support

Pour toute question ou problème :

1. Consulter les logs dans `logs/`
2. Vérifier la configuration
3. Tester en mode simulation
4. Consulter la documentation des exceptions

---

**Version :** 1.0
**Dernière mise à jour :** 28 août 2025
**Statut :** ✅ Production Ready
