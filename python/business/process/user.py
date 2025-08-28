import pandas as pd

from helper.context import SyncContext
from business.process.helper import reporting
from n2f.process import (
    get_roles as get_n2f_roles,
    get_userprofiles as get_n2f_userprofiles,
    get_companies as get_n2f_companies,
    get_users as get_n2f_users,
    create_users, delete_users, update_users
)
from agresso.process import select
from business.normalize import normalize_agresso_users, normalize_n2f_users, build_mapping as build_n2f_mapping


def synchronize(
    context: SyncContext,
    sql_filename: str
) -> None:
    """
    Effectue la synchronisation des utilisateurs Agresso <-> N2F selon les options passées.
    """

    # Chargement des utilisateurs Agresso et normalisation des données
    df_agresso_users: pd.DataFrame = normalize_agresso_users(
        select(
        base_dir     = context.base_dir,
        db_user      = context.db_user,
        db_password  = context.db_password,
        sql_path     = context.config["agresso"]["sql-path"],
        sql_filename = sql_filename,
        prod         = context.config["agresso"]["prod"]
    ))
    print(f"Nombre d'utilisateurs Agresso chargés : {len(df_agresso_users)}")

    # Chargement des rôles N2F
    df_n2f_roles: pd.DataFrame = get_n2f_roles(
        context.config["n2f"]["base_urls"],
        context.client_id,
        context.client_secret,
        context.config["n2f"]["simulate"]
    )
    print(f"Nombre de rôles N2F chargés : {len(df_n2f_roles)}")

    # Chargement des profils N2F
    df_n2f_userprofiles: pd.DataFrame = get_n2f_userprofiles(
        context.config["n2f"]["base_urls"],
        context.client_id,
        context.client_secret,
        context.config["n2f"]["simulate"]
    )
    print(f"Nombre de profils N2F chargés : {len(df_n2f_userprofiles)}")

    # Chargement des entreprises N2F
    df_n2f_companies: pd.DataFrame = get_n2f_companies(
        base_url      = context.config["n2f"]["base_urls"],
        client_id     = context.client_id,
        client_secret = context.client_secret,
        simulate      = context.config["n2f"]["simulate"]
    )
    print(f"Nombre d'entreprises N2F chargées : {len(df_n2f_companies)}")

    # Chargement des utilisateurs N2F et normalisation des données
    profile_mapping: dict[str, str] = build_n2f_mapping(df_n2f_userprofiles)
    role_mapping: dict[str, str] = build_n2f_mapping(df_n2f_roles)
    df_n2f_users: pd.DataFrame = normalize_n2f_users(
        get_n2f_users(
            base_url      = context.config["n2f"]["base_urls"],
            client_id     = context.client_id,
            client_secret = context.client_secret,
            simulate      = context.config["n2f"]["simulate"]
        ),
        profile_mapping, role_mapping
    )
    print(f"Nombre d'utilisateurs N2F chargés : {len(df_n2f_users)}")

    if context.args.create:
        # Création des utilisateurs N2F
        created, status_col = create_users(
            df_agresso_users = df_agresso_users,
            df_n2f_users     = df_n2f_users,
            df_n2f_companies = df_n2f_companies,
            base_url         = context.config["n2f"]["base_urls"],
            client_id        = context.client_id,
            client_secret    = context.client_secret,
            simulate         = context.config["n2f"]["simulate"],
            sandbox          = context.config["n2f"]["sandbox"]
        )
        reporting(
            created,
            "Aucun utilisateur ajouté",
            "Utilisateurs ajoutés",
            status_col
        )

    if context.args.update:
        # Mise à jour des utilisateurs N2F
        updated, status_col = update_users(
            df_agresso_users = df_agresso_users,
            df_n2f_users     = df_n2f_users,
            df_n2f_companies = df_n2f_companies,
            base_url         = context.config["n2f"]["base_urls"],
            client_id        = context.client_id,
            client_secret    = context.client_secret,
            simulate         = context.config["n2f"]["simulate"],
            sandbox          = context.config["n2f"]["sandbox"]
        )
        reporting(
            updated,
            "Aucun utilisateur modifié",
            "Utilisateurs modifiés",
            status_col
        )

    if context.args.delete:
        # Suppression des utilisateurs N2F
        deleted, status_col = delete_users(
            df_agresso_users = df_agresso_users,
            df_n2f_users     = df_n2f_users,
            base_url         = context.config["n2f"]["base_urls"],
            client_id        = context.client_id,
            client_secret    = context.client_secret,
            simulate         = context.config["n2f"]["simulate"]
        )
        reporting(
            deleted,
            "Aucun utilisateur supprimé",
            "Utilisateurs supprimés",
            status_col
        )
