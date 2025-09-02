"""
Module Registry pour la gestion dynamique des scopes de synchronisation.

Ce module implémente le Pattern Registry pour permettre l'enregistrement
et la découverte automatique des scopes sans modification du code existant.
"""

from typing import Dict, Optional, Callable, List, Any
from dataclasses import dataclass
from pathlib import Path
import importlib
import inspect
import pkgutil


@dataclass
class RegistryEntry:
    """Entrée dans le registry pour un scope."""
    sync_function: Callable
    sql_filename: str
    entity_type: str
    display_name: str
    description: str = ""
    enabled: bool = True
    module_path: str = ""
    sql_column_filter: str = ""  # Filtre pour la colonne SQL (ex: "projects", "plates", "subposts")

    def to_scope_config(self):
        """Convertit l'entrée en ScopeConfig."""
        # Import déplacé ici pour éviter les imports circulaires
        from .config import ScopeConfig
        return ScopeConfig(
            sync_function=self.sync_function,
            sql_filename=self.sql_filename,
            entity_type=self.entity_type,
            display_name=self.display_name,
            description=self.description,
            enabled=self.enabled,
            sql_column_filter=self.sql_column_filter
        )


class SyncRegistry:
    """
    Registry pour la gestion dynamique des scopes de synchronisation.

    Permet l'enregistrement et la découverte automatique des scopes
    sans modification du code existant.
    """

    def __init__(self):
        self._registry: Dict[str, RegistryEntry] = {}
        self._discovered_modules: set = set()

    def register(self,
                scope_name: str,
                sync_function: Callable,
                sql_filename: str,
                entity_type: str,
                display_name: str,
                description: str = "",
                enabled: bool = True,
                module_path: str = "",
                sql_column_filter: str = "") -> None:
        """
        Enregistre un nouveau scope dans le registry.

        Args:
            scope_name: Nom unique du scope (ex: "users", "projects")
            sync_function: Fonction de synchronisation
            sql_filename: Nom du fichier SQL pour ce scope
            entity_type: Type d'entité (ex: "user", "project")
            display_name: Nom d'affichage pour l'utilisateur
            description: Description du scope
            enabled: Si le scope est activé
            module_path: Chemin du module (pour auto-découverte)
        """
        if scope_name in self._registry:
            raise ValueError(f"Scope '{scope_name}' already registered")

        self._registry[scope_name] = RegistryEntry(
            sync_function=sync_function,
            sql_filename=sql_filename,
            entity_type=entity_type,
            display_name=display_name,
            description=description,
            enabled=enabled,
            module_path=module_path,
            sql_column_filter=sql_column_filter
        )

    def get(self, scope_name: str):
        """
        Récupère la configuration d'un scope.

        Args:
            scope_name: Nom du scope à récupérer

        Returns:
            ScopeConfig si trouvé, None sinon
        """
        entry = self._registry.get(scope_name)
        return entry.to_scope_config() if entry else None

    def get_all_scopes(self) -> List[str]:
        """Récupère la liste de tous les scopes enregistrés."""
        return list(self._registry.keys())

    def get_enabled_scopes(self) -> List[str]:
        """Récupère la liste des scopes activés."""
        return [name for name, entry in self._registry.items() if entry.enabled]

    def get_all_scope_configs(self) -> Dict[str, Any]:
        """Récupère toutes les configurations de scopes."""
        return {name: entry.to_scope_config() for name, entry in self._registry.items()}

    def is_registered(self, scope_name: str) -> bool:
        """Vérifie si un scope est enregistré."""
        return scope_name in self._registry

    def unregister(self, scope_name: str) -> bool:
        """
        Désenregistre un scope.

        Args:
            scope_name: Nom du scope à désenregistrer

        Returns:
            True si le scope était enregistré et a été supprimé
        """
        if scope_name in self._registry:
            del self._registry[scope_name]
            return True
        return False

    def auto_discover_scopes(self, modules_path: str = "business.process") -> None:
        """
        Découvre automatiquement les scopes dans les modules.

        Args:
            modules_path: Chemin des modules à scanner
        """
        try:
            # Import du module principal
            module = importlib.import_module(modules_path)
            self._scan_module_for_scopes(module, modules_path)

            # Import des sous-modules pour découvrir les nouveaux scopes
            for finder, name, ispkg in pkgutil.iter_modules(module.__path__):
                if not ispkg:  # Seulement les modules, pas les packages
                    submodule_path = f"{modules_path}.{name}"
                    try:
                        submodule = importlib.import_module(submodule_path)
                        self._scan_module_for_scopes(submodule, submodule_path)
                    except ImportError as e:
                        print(f"Warning: Could not import {submodule_path} for auto-discovery: {e}")

        except ImportError as e:
            print(f"Warning: Could not import {modules_path} for auto-discovery: {e}")

    def _scan_module_for_scopes(self, module: Any, module_path: str) -> None:
        """Scanne un module pour trouver les fonctions de synchronisation."""
        if module_path in self._discovered_modules:
            return

        self._discovered_modules.add(module_path)

        for name, obj in inspect.getmembers(module):
            if self._is_sync_function(obj):
                scope_name = self._extract_scope_name(name)
                if scope_name and not self.is_registered(scope_name):
                    # Enregistrement automatique avec valeurs par défaut
                    # Ne pas écraser les configurations existantes
                    self.register(
                        scope_name=scope_name,
                        sync_function=obj,
                        sql_filename=f"get-agresso-n2f-{scope_name}.dev.sql",
                        entity_type=scope_name.rstrip('s'),  # "users" -> "user"
                        display_name=scope_name.title(),  # "users" -> "Users"
                        description=f"Auto-discovered scope: {scope_name}",
                        enabled=True,
                        module_path=module_path
                    )
                # Ne pas mettre à jour les scopes existants pour éviter d'écraser les configurations

    def _is_sync_function(self, obj: Any) -> bool:
        """Vérifie si un objet est une fonction de synchronisation."""
        return (inspect.isfunction(obj) and
                obj.__name__.startswith('synchronize_') and
                obj.__name__ != 'synchronize')  # Exclure la fonction générique

    def _extract_scope_name(self, function_name: str) -> Optional[str]:
        """Extrait le nom du scope depuis le nom de la fonction."""
        if function_name.startswith('synchronize_'):
            return function_name[12:]  # "synchronize_users" -> "users"
        return None

    def load_from_config(self, config_data: Dict[str, Any]) -> None:
        """
        Charge les scopes depuis une configuration.

        Args:
            config_data: Données de configuration contenant les scopes
        """
        scopes_config = config_data.get("scopes", {})

        for scope_name, scope_data in scopes_config.items():
            if isinstance(scope_data, dict) and "sync_function" in scope_data:
                # Configuration complète fournie
                self.register(
                    scope_name=scope_name,
                    sync_function=scope_data["sync_function"],
                    sql_filename=scope_data.get("sql_filename", f"get-agresso-n2f-{scope_name}.dev.sql"),
                    entity_type=scope_data.get("entity_type", scope_name.rstrip('s')),
                    display_name=scope_data.get("display_name", scope_name.title()),
                    description=scope_data.get("description", ""),
                    enabled=scope_data.get("enabled", True)
                )

    def validate(self) -> List[str]:
        """
        Valide le registry et retourne une liste d'erreurs.

        Returns:
            Liste des erreurs de validation
        """
        errors = []

        for scope_name, entry in self._registry.items():
            if not entry.sql_filename:
                errors.append(f"sql_filename manquant pour le scope '{scope_name}'")
            if not entry.entity_type:
                errors.append(f"entity_type manquant pour le scope '{scope_name}'")
            if not entry.display_name:
                errors.append(f"display_name manquant pour le scope '{scope_name}'")

        return errors


# Instance globale du registry
_global_registry = SyncRegistry()


def get_registry() -> SyncRegistry:
    """Récupère l'instance globale du registry."""
    return _global_registry


def register_scope(scope_name: str,
                  sync_function: Callable,
                  sql_filename: str,
                  entity_type: str,
                  display_name: str,
                  description: str = "",
                  enabled: bool = True,
                  sql_column_filter: str = "") -> None:
    """
    Fonction utilitaire pour enregistrer un scope dans le registry global.

    Args:
        scope_name: Nom unique du scope
        sync_function: Fonction de synchronisation
        sql_filename: Nom du fichier SQL
        entity_type: Type d'entité
        display_name: Nom d'affichage
        description: Description du scope
        enabled: Si le scope est activé
    """
    _global_registry.register(
        scope_name=scope_name,
        sync_function=sync_function,
        sql_filename=sql_filename,
        entity_type=entity_type,
        display_name=display_name,
        description=description,
        enabled=enabled,
        sql_column_filter=sql_column_filter
    )
