"""
Context management for synchronization operations.
"""

import argparse
from pathlib import Path
from typing import Any, Union, Dict
from dataclasses import dataclass


@dataclass
class SyncContext:
    """Objet contenant tout le contexte d'exécution pour la synchronisation."""

    args: argparse.Namespace
    config: Union[
        Dict[str, Any], Any
    ]  # Supporte l'ancien format dict et le nouveau SyncConfig
    base_dir: Path
    db_user: Union[str, None]
    db_password: Union[str, None]
    client_id: Union[str, None]
    client_secret: Union[str, None]

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur de configuration de manière compatible avec l'ancien et le
        nouveau format.
        """
        # Import local pour éviter l'import circulaire
        from core import SyncConfig

        if isinstance(self.config, SyncConfig):
            # Nouveau format : SyncConfig
            if key == "agresso":
                return self.config.database
            elif key == "n2f":
                return self.config.api
            else:
                return getattr(self.config, key, default)
        else:
            # Ancien format : dict
            return self.config.get(key, default)
