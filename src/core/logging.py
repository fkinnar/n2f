"""
Module de configuration centralisée du logging pour la synchronisation N2F.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure le logging pour l'application.

    Cette fonction initialise un logger racine avec deux handlers :
    - Un StreamHandler pour afficher les logs dans la console.
    - Un RotatingFileHandler pour écrire les logs dans un fichier
      avec rotation automatique.

    Args:
        log_level (str): Le niveau de log à utiliser (par ex. "DEBUG", "INFO").
    """
    # Créer le dossier logs s'il n'existe pas
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / "sync.log"

    # Définir le format des logs
    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configurer le logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()  # Supprimer les handlers existants

    # Handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    # Handler pour le fichier avec rotation
    # 5 Mo par fichier, conserve les 5 derniers fichiers
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    logging.info("*** DÉBUT DE SESSION DE SYNCHRONISATION ***")
    logging.info("Le système de logging a été initialisé.")
    logging.info("Niveau de log : %s", log_level)
    logging.info("Fichier de log : %s", log_file.absolute())
