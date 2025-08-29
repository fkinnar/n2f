"""
Module de configuration centralisée pour la synchronisation N2F.

Ce module définit les structures de données pour la configuration
et fournit des utilitaires pour charger et valider la configuration.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Callable, Optional, List
from pathlib import Path
import yaml
from .registry import get_registry
# Les imports des fonctions de synchronisation sont déplacés dans les méthodes pour éviter les imports circulaires


@dataclass
class DatabaseConfig:
    """Configuration de la base de données Agresso."""
    prod: bool = True
    sql_path: str = "sql"
    sql_filename_users: str = "get-agresso-n2f-users.dev.sql"
    sql_filename_customaxes: str = "get-agresso-n2f-customaxes.dev.sql"


@dataclass
class ApiConfig:
    """Configuration de l'API N2F."""
    base_urls: str = "https://sandbox.n2f.com/services/api/v2/"
    simulate: bool = False
    sandbox: bool = True


@dataclass
class CacheConfig:
    """Configuration du cache."""
    enabled: bool = True
    cache_dir: str = "cache"
    max_size_mb: int = 100
    default_ttl: int = 3600  # 1 heure par défaut
    persist_cache: bool = True


@dataclass
class ScopeConfig:
    """Configuration d'un scope de synchronisation."""
    sync_function: Callable
    sql_filename: str
    entity_type: str
    display_name: str
    description: str = ""
    enabled: bool = True
    sql_column_filter: str = ""  # Filtre pour la colonne SQL


@dataclass
class SyncConfig:
    """Configuration complète de la synchronisation."""
    database: DatabaseConfig
    api: ApiConfig
    cache: CacheConfig = field(default_factory=CacheConfig)
    scopes: Dict[str, ScopeConfig] = field(default_factory=dict)

    def __post_init__(self):
        """Initialise les scopes par défaut après la création de l'objet."""
        if not self.scopes:
            self._init_default_scopes()

    def _init_default_scopes(self):
        """Initialise les scopes par défaut en utilisant le Registry."""
        registry = get_registry()

        # Enregistrement manuel des scopes par défaut
        self._register_default_scopes_if_needed(registry)

        # Récupération des scopes depuis le registry
        self.scopes = registry.get_all_scope_configs()

    def _register_default_scopes_if_needed(self, registry):
        """Enregistre les scopes par défaut s'ils ne sont pas encore découverts."""
        # Import des fonctions de synchronisation ici pour éviter les imports circulaires
        from business.process import (
            synchronize_users,
            synchronize_projects,
            synchronize_plates,
            synchronize_subposts
        )

        default_scopes = {
            "users": {
                "function": synchronize_users,
                "sql_filename": self.database.sql_filename_users,
                "entity_type": "user",
                "display_name": "Utilisateurs",
                "description": "Synchronisation des utilisateurs Agresso vers N2F"
            },
            "projects": {
                "function": synchronize_projects,
                "sql_filename": self.database.sql_filename_customaxes,
                "entity_type": "project",
                "display_name": "Projets",
                "description": "Synchronisation des projets (axes personnalisés)",
                "sql_column_filter": "projects"
            },
            "plates": {
                "function": synchronize_plates,
                "sql_filename": self.database.sql_filename_customaxes,
                "entity_type": "plate",
                "display_name": "Plaques",
                "description": "Synchronisation des plaques (axes personnalisés)",
                "sql_column_filter": "plates"
            },
            "subposts": {
                "function": synchronize_subposts,
                "sql_filename": self.database.sql_filename_customaxes,
                "entity_type": "subpost",
                "display_name": "Sous-posts",
                "description": "Synchronisation des sous-posts (axes personnalisés)",
                "sql_column_filter": "subposts"
            }
        }

        for scope_name, scope_data in default_scopes.items():
            if not registry.is_registered(scope_name):
                registry.register(
                    scope_name=scope_name,
                    sync_function=scope_data["function"],
                    sql_filename=scope_data["sql_filename"],
                    entity_type=scope_data["entity_type"],
                    display_name=scope_data["display_name"],
                    description=scope_data["description"],
                    sql_column_filter=scope_data.get("sql_column_filter", "")
                )

    def get_scope(self, scope_name: str) -> Optional[ScopeConfig]:
        """Récupère la configuration d'un scope."""
        return self.scopes.get(scope_name)

    def get_enabled_scopes(self) -> List[str]:
        """Récupère la liste des scopes activés."""
        return [name for name, config in self.scopes.items() if config.enabled]

    def validate(self) -> List[str]:
        """Valide la configuration et retourne une liste d'erreurs."""
        errors = []

        # Validation de la base de données
        if not self.database.sql_path:
            errors.append("sql_path ne peut pas être vide")

        # Validation de l'API
        if not self.api.base_urls:
            errors.append("base_urls ne peut pas être vide")

        # Validation des scopes
        for scope_name, scope_config in self.scopes.items():
            if not scope_config.sql_filename:
                errors.append(f"sql_filename manquant pour le scope '{scope_name}'")
            if not scope_config.entity_type:
                errors.append(f"entity_type manquant pour le scope '{scope_name}'")

        return errors


class ConfigLoader:
    """Chargeur de configuration depuis les fichiers YAML."""

    def __init__(self, config_path: Path):
        self.config_path = config_path

    def load(self) -> SyncConfig:
        """Charge la configuration depuis le fichier YAML."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Fichier de configuration non trouvé : {self.config_path}")

        with self.config_path.open('r', encoding='utf-8') as config_file:
            config_data = yaml.safe_load(config_file)

        # Création des objets de configuration
        database_config = DatabaseConfig(
            prod=config_data.get("agresso", {}).get("prod", True),
            sql_path=config_data.get("agresso", {}).get("sql-path", "sql"),
            sql_filename_users=config_data.get("agresso", {}).get("sql-filename-users", "get-agresso-n2f-users.dev.sql"),
            sql_filename_customaxes=config_data.get("agresso", {}).get("sql-filename-customaxes", "get-agresso-n2f-customaxes.dev.sql")
        )

        api_config = ApiConfig(
            base_urls=config_data.get("n2f", {}).get("base_urls", "https://sandbox.n2f.com/services/api/v2/"),
            simulate=config_data.get("n2f", {}).get("simulate", False),
            sandbox=config_data.get("n2f", {}).get("sandbox", True)
        )

        cache_config = CacheConfig(
            enabled=config_data.get("cache", {}).get("enabled", True),
            cache_dir=config_data.get("cache", {}).get("cache_dir", "cache"),
            max_size_mb=config_data.get("cache", {}).get("max_size_mb", 100),
            default_ttl=config_data.get("cache", {}).get("default_ttl", 3600),
            persist_cache=config_data.get("cache", {}).get("persist_cache", True)
        )

        sync_config = SyncConfig(
            database=database_config,
            api=api_config,
            cache=cache_config
        )

        # Validation de la configuration
        errors = sync_config.validate()
        if errors:
            raise ValueError(f"Configuration invalide : {'; '.join(errors)}")

        return sync_config


def create_default_config() -> Dict[str, Any]:
    """Crée une configuration par défaut."""
    return {
        "agresso": {
            "prod": True,
            "sql-path": "sql",
            "sql-filename-users": "get-agresso-n2f-users.dev.sql",
            "sql-filename-customaxes": "get-agresso-n2f-customaxes.dev.sql"
        },
        "n2f": {
            "base_urls": "https://sandbox.n2f.com/services/api/v2/",
            "simulate": False,
            "sandbox": True
        }
    }
