"""
Module de traitement des processus métier.

Ce module contient les classes et fonctions pour la synchronisation
des entités métier (utilisateurs, axes, projets) avec l'API N2F.
"""

# Import des nouvelles classes de synchronisation
from .user_synchronizer import UserSynchronizer
from .axe_synchronizer import AxeSynchronizer
from .base_synchronizer import EntitySynchronizer

# Import des fonctions de compatibilité
from .user import synchronize as synchronize_users
from .axe import synchronize_projects, synchronize_plates, synchronize_subposts

# Import des fonctions utilitaires
from .helper import reporting

__all__ = [
    "UserSynchronizer",
    "AxeSynchronizer",
    "EntitySynchronizer",
    "synchronize_users",
    "synchronize_projects",
    "synchronize_plates",
    "synchronize_subposts",
    "reporting",
]
