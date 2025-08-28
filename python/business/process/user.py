import pandas as pd
from typing import Tuple

from helper.context import SyncContext
from business.process.helper import reporting
from n2f.client import N2fApiClient
from n2f.process import create_users, delete_users, update_users
from agresso.process import select
from business.normalize import normalize_agresso_users, normalize_n2f_users, build_mapping as build_n2f_mapping

def _load_agresso_users(context: SyncContext, sql_filename: str) -> pd.DataFrame:
    """Charge et normalise les utilisateurs depuis Agresso."""
    df_agresso_users = normalize_agresso_users(
        select(
            base_dir=context.base_dir,
            db_user=context.db_user,
            db_password=context.db_password,
            sql_path=context.config["agresso"]["sql-path"],
            sql_filename=sql_filename,
            prod=context.config["agresso"]["prod"]
        )
    )
    print(f"Number of Agresso users loaded : {len(df_agresso_users)}")
    return df_agresso_users

def _load_n2f_data(n2f_client: N2fApiClient) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
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
        n2f_client.get_users(),
        profile_mapping, role_mapping
    )
    print(f"Number of N2F users loaded : {len(df_users)}")

    return df_users, df_companies

def _perform_sync_actions(
    context: SyncContext,
    n2f_client: N2fApiClient,
    df_agresso_users: pd.DataFrame,
    df_n2f_users: pd.DataFrame,
    df_n2f_companies: pd.DataFrame
) -> list[pd.DataFrame]:
    """Exécute les actions de création, mise à jour et suppression."""
    results = []

    if context.args.create:
        created, status_col = create_users(
            df_agresso_users=df_agresso_users,
            df_n2f_users=df_n2f_users,
            df_n2f_companies=df_n2f_companies,
            n2f_client=n2f_client,
            sandbox=context.config["n2f"]["sandbox"]
        )
        reporting(created, "No user added", "Users added", status_col)
        if not created.empty:
            results.append(created)

    if context.args.update:
        updated, status_col = update_users(
            df_agresso_users=df_agresso_users,
            df_n2f_users=df_n2f_users,
            df_n2f_companies=df_n2f_companies,
            n2f_client=n2f_client,
            sandbox=context.config["n2f"]["sandbox"]
        )
        reporting(updated, "No user modified", "Users modified", status_col)
        if not updated.empty:
            results.append(updated)

    if context.args.delete:
        deleted, status_col = delete_users(
            df_agresso_users=df_agresso_users,
            df_n2f_users=df_n2f_users,
            n2f_client=n2f_client
        )
        reporting(deleted, "No user deleted", "Users deleted", status_col)
        if not deleted.empty:
            results.append(deleted)

    return results

def synchronize(
    context: SyncContext,
    sql_filename: str
) -> list[pd.DataFrame]:
    """
    Orchestre la synchronisation des utilisateurs Agresso <-> N2F.
    """
    # Initialisation des clients et chargement des données
    n2f_client = N2fApiClient(context)
    df_agresso_users = _load_agresso_users(context, sql_filename)
    df_n2f_users, df_n2f_companies = _load_n2f_data(n2f_client)

    # Exécution des actions de synchronisation
    results = _perform_sync_actions(
        context, n2f_client, df_agresso_users, df_n2f_users, df_n2f_companies
    )

    return results