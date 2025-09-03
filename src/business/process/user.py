import pandas as pd
from typing import Tuple, List

from core import SyncContext
from business.process.helper import reporting
from n2f.client import N2fApiClient
from agresso.process import select
from business.normalize import (
    normalize_agresso_users,
    normalize_n2f_users,
    build_mapping as build_n2f_mapping,
)
from .user_synchronizer import UserSynchronizer


def _load_agresso_users(context: SyncContext, sql_filename: str) -> pd.DataFrame:
    """Charge et normalise les utilisateurs depuis Agresso."""
    # Utilise la méthode get_config_value pour supporter l'ancien et le nouveau format
    agresso_config = context.get_config_value("agresso")
    sql_path = (
        agresso_config.sql_path
        if hasattr(agresso_config, "sql_path")
        else agresso_config["sql - path"]
    )
    prod = (
        agresso_config.prod
        if hasattr(agresso_config, "prod")
        else agresso_config["prod"]
    )

    df_agresso_users = normalize_agresso_users(
        select(
            base_dir=context.base_dir,
            db_user=context.db_user,
            db_password=context.db_password,
            sql_path=sql_path,
            sql_filename=sql_filename,
            prod=prod,
        )
    )
    print(f"Number of Agresso users loaded : {len(df_agresso_users)}")
    return df_agresso_users


def _load_n2f_data(n2f_client: N2fApiClient) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Charge toutes les données nécessaires depuis N2F (utilisateurs, rôles, profils, entreprises)."""
    df_roles = n2f_client.get_roles()
    print(f"Number of N2F roles loaded : {len(df_roles)}")

    df_userprofiles = n2f_client.get_userprofiles()
    print(f"Number of N2F profiles loaded : {len(df_userprofiles)}")

    df_companies = n2f_client.get_companies()
    print(f"Number of N2F companies loaded : {len(df_companies)}")

    profile_mapping = build_n2f_mapping(df_userprofiles)
    role_mapping = build_n2f_mapping(df_roles)
    df_users = normalize_n2f_users(
        n2f_client.get_users(), profile_mapping, role_mapping
    )
    print(f"Number of N2F users loaded : {len(df_users)}")

    return df_users, df_companies


def synchronize(
    context: SyncContext, sql_filename: str, sql_column_filter: str = ""
) -> List[pd.DataFrame]:
    """
    Orchestre la synchronisation des utilisateurs Agresso <-> N2F.

    Utilise la nouvelle classe UserSynchronizer pour une meilleure architecture.
    """
    # Initialisation des clients et chargement des données
    n2f_client = N2fApiClient(context)
    df_agresso_users = _load_agresso_users(context, sql_filename)
    df_n2f_users, df_n2f_companies = _load_n2f_data(n2f_client)

    # Création du synchroniseur
    n2f_config = context.get_config_value("n2f")
    sandbox = (
        n2f_config.sandbox if hasattr(n2f_config, "sandbox") else n2f_config["sandbox"]
    )
    synchronizer = UserSynchronizer(n2f_client, sandbox)
    results: List[pd.DataFrame] = []

    # Exécution des actions de synchronisation
    if context.args.create:
        created, status_col = synchronizer.create_entities(
            df_agresso_users, df_n2f_users, df_n2f_companies
        )
        reporting(created, "No user added", "Users added", status_col)
        if not created.empty:
            results.append(created)

    if context.args.update:
        updated, status_col = synchronizer.update_entities(
            df_agresso_users, df_n2f_users, df_n2f_companies
        )
        reporting(updated, "No user modified", "Users modified", status_col)
        if not updated.empty:
            results.append(updated)

    if context.args.delete:
        deleted, status_col = synchronizer.delete_entities(
            df_agresso_users, df_n2f_users, df_n2f_companies
        )
        reporting(deleted, "No user deleted", "Users deleted", status_col)
        if not deleted.empty:
            results.append(deleted)

    return results
