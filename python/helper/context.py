import argparse
from pathlib import Path
from typing import Any
from dataclasses import dataclass


@dataclass
class SyncContext:
    """Objet contenant tout le contexte d'exécution pour la synchronisation."""
    args: argparse.Namespace
    config: dict[str, Any]
    base_dir: Path
    db_user: str | None
    db_password: str | None
    client_id: str | None
    client_secret: str | None
