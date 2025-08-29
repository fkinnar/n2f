# 📚 API Reference - N2F Synchronization Tool

Documentation technique complète des APIs et composants du projet de synchronisation N2F.

## 🏗️ Architecture Overview

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Agresso DB    │    │  N2F Sync Tool  │    │   N2F API       │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ SQL Queries │◄┼────┼►│ EntitySync  │◄┼────┼►│ REST API    │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │ ┌─────────────┐ │    │                 │
│                 │    │ │ N2F Client  │◄┼────┼─────────────────┤
│                 │    │ └─────────────┘ │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘

```

## 🔧 Core Components

### 1. EntitySynchronizer (Abstract Base Class)

Classe abstraite définissant le contrat pour toutes les synchronisations d'entités.

#### Signature

```python
class EntitySynchronizer(ABC):
    def __init__(self, n2f_client: N2fApiClient, sandbox: bool, scope: str)

    # Méthodes concrètes (implémentées dans la classe de base)

    def create_entities(self, df_agresso: pd.DataFrame, df_n2f: pd.DataFrame,
                       df_n2f_companies: pd.DataFrame = None) -> Tuple[pd.DataFrame, str]
    def update_entities(self, df_agresso: pd.DataFrame, df_n2f: pd.DataFrame,
                       df_n2f_companies: pd.DataFrame = None) -> Tuple[pd.DataFrame, str]
    def delete_entities(self, df_agresso: pd.DataFrame, df_n2f: pd.DataFrame,
                       df_n2f_companies: pd.DataFrame = None) -> Tuple[pd.DataFrame, str]

    # Méthodes abstraites (à implémenter dans les classes concrètes)

    @abstractmethod
    def build_payload(self, entity: pd.Series, df_agresso: pd.DataFrame,
                     df_n2f: pd.DataFrame, df_n2f_companies: pd.DataFrame = None) -> Dict[str, Any]

    @abstractmethod
    def get_entity_id(self, entity: pd.Series) -> str

    @abstractmethod
    def get_agresso_id_column(self) -> str

    @abstractmethod
    def get_n2f_id_column(self) -> str

    @abstractmethod
    def _perform_create_operation(self, entity: pd.Series, payload: Dict,
                                df_n2f_companies: pd.DataFrame = None) -> ApiResult

    @abstractmethod
    def _perform_update_operation(self, entity: pd.Series, payload: Dict,
                                n2f_entity: Dict, df_n2f_companies: pd.DataFrame = None) -> ApiResult

    @abstractmethod
    def _perform_delete_operation(self, entity: pd.Series,
                                df_n2f_companies: pd.DataFrame = None) -> ApiResult

```

#### Exemple d'implémentation

```python
class UserSynchronizer(EntitySynchronizer):
    def __init__(self, n2f_client, sandbox: bool):
        super().__init__(n2f_client, sandbox, "users")

    def build_payload(self, entity: pd.Series, df_agresso: pd.DataFrame,
                     df_n2f: pd.DataFrame, df_n2f_companies: pd.DataFrame = None) -> Dict[str, Any]:
        return build_user_payload(entity, df_agresso, df_n2f, self.n2f_client, df_n2f_companies, self.sandbox)

    def get_entity_id(self, entity: pd.Series) -> str:
        return entity["AdresseEmail"]

    def get_agresso_id_column(self) -> str:
        return "AdresseEmail"

    def get_n2f_id_column(self) -> str:
        return "mail"

    def _perform_create_operation(self, entity: pd.Series, payload: Dict,
                                df_n2f_companies: pd.DataFrame = None) -> ApiResult:
        return self.n2f_client.create_user(payload)

    def _perform_update_operation(self, entity: pd.Series, payload: Dict,
                                n2f_entity: Dict, df_n2f_companies: pd.DataFrame = None) -> ApiResult:
        return self.n2f_client.update_user(payload)

    def _perform_delete_operation(self, entity: pd.Series,
                                df_n2f_companies: pd.DataFrame = None) -> ApiResult:
        return self.n2f_client.delete_user(self.get_entity_id(entity))

```

### 2. N2fApiClient

Client API pour interagir avec l'API N2F.

#### Méthodes principales

```python
class N2fApiClient:
    def __init__(self, context: SyncContext)

    # Récupération de données

    def get_companies(self, use_cache: bool = True) -> pd.DataFrame
    def get_roles(self, use_cache: bool = True) -> pd.DataFrame
    def get_users(self, use_cache: bool = True) -> pd.DataFrame
    def get_user_profiles(self, use_cache: bool = True) -> pd.DataFrame
    def get_custom_axes(self, company_id: str, use_cache: bool = True) -> pd.DataFrame

    # Opérations CRUD

    def create_user(self, payload: dict) -> ApiResult
    def update_user(self, payload: dict) -> ApiResult
    def delete_user(self, user_email: str) -> ApiResult

    # Opérations sur les axes

    def upsert_axe_value(self, company_id: str, axe_id: str, payload: dict,
                        action_type: str, scope: str) -> ApiResult

```

#### Exemple d'utilisation

```python

# Initialisation

context = SyncContext(...)
client = N2fApiClient(context)

# Récupération de données

companies = client.get_companies(use_cache=True)
users = client.get_users(use_cache=True)

# Création d'un utilisateur

user_payload = {
    "mail": "john.doe@example.com",
    "firstname": "John",
    "lastname": "Doe"
}
result = client.create_user(user_payload)

if result.success:
    print(f"User created: {result.message}")
else:
    print(f"Error: {result.message}")

```

### 3. ApiResult

Classe pour encapsuler les résultats d'API avec métadonnées.

#### Structure

```python
class ApiResult:
    def __init__(self, success: bool, message: str, status_code: int = None,
                 duration_ms: float = None, error_details: str = None,
                 action_type: str = None, object_type: str = None,
                 object_id: str = None, scope: str = None)

    # Propriétés

    success: bool
    message: str
    status_code: Optional[int]
    duration_ms: Optional[float]
    error_details: Optional[str]
    action_type: Optional[str]
    object_type: Optional[str]
    object_id: Optional[str]
    scope: Optional[str]

    # Méthodes de factory

    @classmethod
    def success_result(cls, message: str, status_code: int = None,
                      duration_ms: float = None, **kwargs) -> 'ApiResult'

    @classmethod
    def error_result(cls, message: str, status_code: int = None,
                    duration_ms: float = None, error_details: str = None, **kwargs) -> 'ApiResult'

    @classmethod
    def simulate_result(cls, action_type: str, object_type: str = None,
                       object_id: str = None, scope: str = None) -> 'ApiResult'

```

#### Exemple d'utilisation

```python

# Succès

result = ApiResult.success_result(
    message="User created successfully",
    status_code=201,
    duration_ms=150.5,
    action_type="create",
    object_type="user",
    object_id="john@example.com",
    scope="users"
)

# Erreur

result = ApiResult.error_result(
    message="User not found",
    status_code=404,
    duration_ms=45.2,
    error_details="User with email john@example.com does not exist",
    action_type="update",
    object_type="user",
    object_id="john@example.com",
    scope="users"
)

# Simulation

result = ApiResult.simulate_result(
    action_type="create",
    object_type="user",
    object_id="john@example.com",
    scope="users"
)

```

## 🚨 Exception Hierarchy

### SyncException (Base)

Exception de base pour toutes les erreurs de synchronisation.

```python
class SyncException(Exception):
    def __init__(self, message: str, details: str = None, context: Dict[str, Any] = None)

    # Propriétés

    message: str
    details: Optional[str]
    context: Dict[str, Any]

    # Méthodes

    def to_dict(self) -> Dict[str, Any]

```

### Exceptions spécialisées

```python

# Erreurs d'API

class ApiException(SyncException):
    def __init__(self, message: str, status_code: int = None,
                 response_text: str = None, endpoint: str = None, **kwargs)

    # Propriétés additionnelles

    status_code: Optional[int]
    response_text: Optional[str]
    endpoint: Optional[str]

# Erreurs de validation

class ValidationException(SyncException):
    def __init__(self, message: str, field: str = None,
                 value: Any = None, expected_format: str = None, **kwargs)

    # Propriétés additionnelles

    field: Optional[str]
    value: Optional[Any]
    expected_format: Optional[str]

# Erreurs de configuration

class ConfigurationException(SyncException):
    def __init__(self, message: str, config_key: str = None,
                 config_file: str = None, **kwargs)

    # Propriétés additionnelles

    config_key: Optional[str]
    config_file: Optional[str]

# Erreurs de base de données

class DatabaseException(SyncException):
    def __init__(self, message: str, sql_query: str = None,
                 table: str = None, **kwargs)

    # Propriétés additionnelles

    sql_query: Optional[str]
    table: Optional[str]

# Erreurs d'authentification

class AuthenticationException(SyncException):
    def __init__(self, message: str, service: str = None,
                 credentials_type: str = None, **kwargs)

    # Propriétés additionnelles

    service: Optional[str]
    credentials_type: Optional[str]

# Erreurs réseau

class NetworkException(SyncException):
    def __init__(self, message: str, url: str = None,
                 timeout: float = None, retry_count: int = None, **kwargs)

    # Propriétés additionnelles

    url: Optional[str]
    timeout: Optional[float]
    retry_count: Optional[int]

```

### Exemple d'utilisation

```python
from core.exceptions import ApiException, ValidationException

# Gestion d'erreur d'API

try:
    result = client.create_user(payload)
except ApiException as e:
    print(f"API Error: {e.message}")
    print(f"Status: {e.status_code}")
    print(f"Endpoint: {e.endpoint}")
    print(f"Response: {e.response_text}")

# Gestion d'erreur de validation

try:
    validate_email(email)
except ValidationException as e:
    print(f"Validation Error: {e.message}")
    print(f"Field: {e.field}")
    print(f"Value: {e.value}")
    print(f"Expected Format: {e.expected_format}")

# Gestion hiérarchique

try:
    # Opération qui peut lever différentes exceptions

    pass
except ApiException as e:
    # Gestion spécifique des erreurs d'API

    handle_api_error(e)
except SyncException as e:
    # Gestion générique des erreurs de synchronisation

    handle_sync_error(e)
except Exception as e:
    # Gestion des erreurs inattendues

    handle_unexpected_error(e)

```

## 🔧 Utility Functions

### Fonctions de comparaison

```python
def has_payload_changes(payload: Dict[str, Any], n2f_entity: Dict[str, Any],
                       entity_type: str = None) -> bool:
    """
    Compare les champs du payload avec les données N2F pour détecter les changements.

    Args:
        payload: Dictionnaire contenant les données à envoyer à l'API
        n2f_entity: Dictionnaire contenant les données actuelles de N2F
        entity_type: Type d'entité ('axe' ou 'user') pour adapter la logique

    Returns:
        bool: True si des changements sont détectés, False sinon
    """

```

### Fonctions de logging

```python
def log_error(scope: str, action: str, entity_id: str, error: Exception,
              context: str = "") -> None:
    """
    Enregistre une erreur avec son contexte pour faciliter le debugging.

    Args:
        scope: Périmètre de synchronisation (USERS, PROJECTS, PLATES, SUBPOSTS)
        action: Action effectuée (CREATE, UPDATE, DELETE)
        entity_id: Identifiant de l'entité
        error: Exception levée
        context: Contexte supplémentaire optionnel
    """

def reporting(result_df: pd.DataFrame, empty_message: str, update_message: str,
              status_col: str) -> None:
    """
    Génère un rapport détaillé à partir d'un DataFrame de résultats.

    Args:
        result_df: DataFrame contenant les résultats des opérations
        empty_message: Message à afficher si le DataFrame est vide
        update_message: Message de base pour les opérations avec résultats
        status_col: Nom de la colonne contenant le statut
    """

```

### Fonctions de cache

```python
def get_from_cache(key: str, *args) -> Optional[Any]:
    """
    Récupère une valeur du cache.

    Args:
        key: Clé de cache
        *args: Arguments pour générer la clé de cache

    Returns:
        Valeur mise en cache ou None si non trouvée
    """

def set_in_cache(value: Any, key: str, *args) -> None:
    """
    Stocke une valeur dans le cache.

    Args:
        value: Valeur à stocker
        key: Clé de cache
        *args: Arguments pour générer la clé de cache
    """

```

## 🎯 Décorateurs

### Gestion automatique d'exceptions

```python
from core.exceptions import wrap_api_call, handle_sync_exceptions

@wrap_api_call
def api_function():
    """
    Fonction wrapper avec gestion automatique des erreurs d'API.
    Convertit automatiquement les exceptions génériques en ApiException.
    """
    pass

@handle_sync_exceptions
def sync_function():
    """
    Fonction wrapper avec gestion automatique des erreurs de synchronisation.
    Convertit automatiquement les exceptions génériques en SyncException.
    """
    pass

```

## 📊 Data Models

### SyncContext

Contexte de synchronisation contenant la configuration et les credentials.

```python
class SyncContext:
    def __init__(self, args: argparse.Namespace, config: dict, base_dir: Path,
                 db_user: str, db_password: str, client_id: str, client_secret: str)

    # Propriétés

    args: argparse.Namespace
    config: dict
    base_dir: Path
    db_user: str
    db_password: str
    client_id: str
    client_secret: str

```

### Configuration YAML

Structure typique d'un fichier de configuration :

```yaml
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

## 🔄 Workflow de synchronisation

### 1. Initialisation

```python

# Chargement de la configuration

context = SyncContext(...)
client = N2fApiClient(context)

# Création du synchroniseur

synchronizer = UserSynchronizer(client, sandbox=True)

```

### 2. Récupération des données

```python

# Données Agresso (via SQL)

df_agresso = load_agresso_data(sql_filename)

# Données N2F (via API)

df_n2f = client.get_users(use_cache=True)
df_n2f_companies = client.get_companies(use_cache=True)

```

### 3. Synchronisation

```python

# Création des entités manquantes

create_results, create_summary = synchronizer.create_entities(
    df_agresso, df_n2f, df_n2f_companies
)

# Mise à jour des entités existantes

update_results, update_summary = synchronizer.update_entities(
    df_agresso, df_n2f, df_n2f_companies
)

# Suppression des entités obsolètes

delete_results, delete_summary = synchronizer.delete_entities(
    df_agresso, df_n2f, df_n2f_companies
)

```

### 4. Export des logs

```python

# Combinaison des résultats

all_results = [create_results, update_results, delete_results]
combined_df = pd.concat(all_results, ignore_index=True)

# Export des logs

log_filename = export_api_logs(combined_df)

```

## 🧪 Testing

### Tests unitaires

```python
import unittest
from unittest.mock import Mock, patch

class TestUserSynchronizer(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.synchronizer = UserSynchronizer(self.client, sandbox=True)

    def test_build_payload(self):
        # Test de construction du payload

        entity = pd.Series({
            "AdresseEmail": "test@example.com",
            "Nom": "Test User"
        })
        payload = self.synchronizer.build_payload(entity, pd.DataFrame(), pd.DataFrame())
        self.assertEqual(payload["mail"], "test@example.com")

    def test_get_entity_id(self):
        # Test d'extraction de l'ID

        entity = pd.Series({"AdresseEmail": "test@example.com"})
        entity_id = self.synchronizer.get_entity_id(entity)
        self.assertEqual(entity_id, "test@example.com")

```

### Tests d'intégration

```python
class TestN2fApiClient(unittest.TestCase):
    def setUp(self):
        self.context = create_test_context()
        self.client = N2fApiClient(self.context)

    @patch('n2f.client.requests.get')
    def test_get_users(self, mock_get):
        # Mock de la réponse API

        mock_get.return_value.json.return_value = {
            "response": {"data": [{"mail": "test@example.com"}]}
        }
        mock_get.return_value.status_code = 200

        users = self.client.get_users()
        self.assertFalse(users.empty)
        self.assertEqual(users.iloc[0]["mail"], "test@example.com")

```

## 📈 Performance et optimisation

### Cache

- **TTL** : 5 minutes par défaut

- **Clés** : Basées sur les paramètres de la requête

- **Nettoyage** : Automatique lors du dépassement de la taille limite

### Pagination

- **Taille de page** : 200 éléments par défaut

- **Récupération automatique** : Toutes les pages récupérées automatiquement

- **Optimisation mémoire** : Traitement par chunks

### Gestion d'erreur

- **Retry automatique** : 3 tentatives avec backoff exponentiel

- **Fallback** : Mode simulation en cas d'échec critique

- **Logging détaillé** : Toutes les erreurs tracées avec contexte

---

**Version :** 1.0
**Dernière mise à jour :** 28 août 2025
**Statut :** ✅ Production Ready
