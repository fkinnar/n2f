"""
Exemple d'utilisation des nouvelles classes EntitySynchronizer.

Ce fichier montre comment utiliser UserSynchronizer et AxeSynchronizer
pour remplacer les fonctions existantes dans user.py et axe.py.
"""

import pandas as pd
from typing import Tuple, Any
from business.process.user_synchronizer import UserSynchronizer
from business.process.axe_synchronizer import AxeSynchronizer
from n2f.client import N2fApiClient


def sync_users_with_new_classes(
    n2f_client: N2fApiClient,
    df_agresso_users: pd.DataFrame,
    df_n2f_users: pd.DataFrame,
    df_n2f_companies: pd.DataFrame,
    sandbox: bool,
) -> Tuple[
    Tuple[pd.DataFrame, str], Tuple[pd.DataFrame, str], Tuple[pd.DataFrame, str]
]:
    """
    Exemple d'utilisation de UserSynchronizer pour remplacer les fonctions existantes.

    Args:
        n2f_client: Client API N2F
        df_agresso_users: DataFrame des utilisateurs Agresso
        df_n2f_users: DataFrame des utilisateurs N2F
        df_n2f_companies: DataFrame des entreprises N2F
        sandbox: Mode sandbox ou production

    Returns:
        Tuple[Tuple[pd.DataFrame, str], Tuple[pd.DataFrame, str], Tuple[pd.DataFrame, str]]:
        Résultats des opérations (create, update, delete)
    """
    # Créer le synchroniseur d'utilisateurs
    user_sync = UserSynchronizer(n2f_client, sandbox)

    # Effectuer les opérations de synchronisation
    created_users, created_col = user_sync.create_entities(
        df_agresso_users, df_n2f_users, df_n2f_companies, "created"
    )

    updated_users, updated_col = user_sync.update_entities(
        df_agresso_users, df_n2f_users, df_n2f_companies, "updated"
    )

    deleted_users, deleted_col = user_sync.delete_entities(
        df_agresso_users, df_n2f_users, df_n2f_companies, "deleted"
    )

    return (
        (created_users, created_col),
        (updated_users, updated_col),
        (deleted_users, deleted_col),
    )


def sync_axes_with_new_classes(
    n2f_client: N2fApiClient,
    axe_id: str,
    df_agresso_projects: pd.DataFrame,
    df_n2f_projects: pd.DataFrame,
    df_n2f_companies: pd.DataFrame,
    sandbox: bool,
    scope: str = "projects",
) -> Tuple[
    Tuple[pd.DataFrame, str], Tuple[pd.DataFrame, str], Tuple[pd.DataFrame, str]
]:
    """
    Exemple d'utilisation de AxeSynchronizer pour remplacer les fonctions existantes.

    Args:
        n2f_client: Client API N2F
        axe_id: Identifiant de l'axe à synchroniser
        df_agresso_projects: DataFrame des projets Agresso
        df_n2f_projects: DataFrame des projets N2F
        df_n2f_companies: DataFrame des entreprises N2F
        sandbox: Mode sandbox ou production
        scope: Scope de synchronisation

    Returns:
        Tuple[Tuple[pd.DataFrame, str], Tuple[pd.DataFrame, str], Tuple[pd.DataFrame, str]]:
        Résultats des opérations (create, update, delete)
    """
    # Créer le synchroniseur d'axes
    axe_sync = AxeSynchronizer(n2f_client, sandbox, axe_id, scope)

    # Effectuer les opérations de synchronisation
    created_axes, created_col = axe_sync.create_entities(
        df_agresso_projects, df_n2f_projects, df_n2f_companies, "created"
    )

    updated_axes, updated_col = axe_sync.update_entities(
        df_agresso_projects, df_n2f_projects, df_n2f_companies, "updated"
    )

    deleted_axes, deleted_col = axe_sync.delete_entities(
        df_agresso_projects, df_n2f_projects, df_n2f_companies, "deleted"
    )

    return (
        (created_axes, created_col),
        (updated_axes, updated_col),
        (deleted_axes, deleted_col),
    )


# Comparaison avec l'ancien code :
"""
ANCIEN CODE (user.py):
def create_users(df_agresso_users, df_n2f_users, df_n2f_companies, n2f_client, sandbox, status_col="created"):
    # 30+ lignes de code avec gestion d'erreur manuelle
    # Logique répétée pour chaque opération

def update_users(df_agresso_users, df_n2f_users, df_n2f_companies, n2f_client, sandbox, status_col="updated"):
    # 40+ lignes de code avec gestion d'erreur manuelle
    # Logique répétée pour chaque opération

def delete_users(df_agresso_users, df_n2f_users, n2f_client, status_col="deleted"):
    # 25+ lignes de code avec gestion d'erreur manuelle
    # Logique répétée pour chaque opération

NOUVEAU CODE:
user_sync = UserSynchronizer(n2f_client, sandbox)
created_users, created_col = user_sync.create_entities(df_agresso_users, df_n2f_users, df_n2f_companies)
updated_users, updated_col = user_sync.update_entities(df_agresso_users, df_n2f_users, df_n2f_companies)
deleted_users, deleted_col = user_sync.delete_entities(df_agresso_users, df_n2f_users, df_n2f_companies)

AVANTAGES:
✅ Code plus concis et lisible
✅ Gestion d'erreur centralisée et cohérente
✅ Pas de duplication de logique
✅ Facile d'ajouter de nouveaux types d'entités
✅ Tests plus faciles à écrire
"""
