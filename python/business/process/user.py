import pandas as pd

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
    do_create     : bool,
    do_update     : bool,
    do_delete     : bool,
    base_dir      : str,
    db_user       : str,
    db_password   : str,
    sql_path      : str,
    sql_filename  : str,
    base_url      : str,
    client_id     : str,
    client_secret : str,
    prod          : bool,
    simulate      : bool,
    sandbox       : bool
) -> None:
    """
    Effectue la synchronisation des utilisateurs Agresso <-> N2F selon les options passées.
    """

    # Chargement des utilisateurs Agresso et normalisation des données
    df_agresso_users: pd.DataFrame = normalize_agresso_users(
        select(
        base_dir     = base_dir,
        db_user      = db_user,
        db_password  = db_password,
        sql_path     = sql_path,
        sql_filename = sql_filename,
        prod         = prod
    ))
    print(f"Nombre d'utilisateurs Agresso chargés : {len(df_agresso_users)}")

    # Chargement des rôles N2F
    df_n2f_roles: pd.DataFrame = get_n2f_roles(
        base_url,
        client_id,
        client_secret,
        simulate
    )
    print(f"Nombre de rôles N2F chargés : {len(df_n2f_roles)}")

    # Chargement des profils N2F
    df_n2f_userprofiles: pd.DataFrame = get_n2f_userprofiles(
        base_url,
        client_id,
        client_secret,
        simulate
    )
    print(f"Nombre de profils N2F chargés : {len(df_n2f_userprofiles)}")

    # Chargement des entreprises N2F
    df_n2f_companies: pd.DataFrame = get_n2f_companies(
        base_url      = base_url,
        client_id     = client_id,
        client_secret = client_secret,
        simulate      = simulate
    )
    print(f"Nombre d'entreprises N2F chargées : {len(df_n2f_companies)}")

    # Chargement des utilisateurs N2F et normalisation des données
    profile_mapping: dict[str, str] = build_n2f_mapping(df_n2f_userprofiles)
    role_mapping: dict[str, str] = build_n2f_mapping(df_n2f_roles)
    df_n2f_users: pd.DataFrame = normalize_n2f_users(
        get_n2f_users(
            base_url      = base_url,
            client_id     = client_id,
            client_secret = client_secret,
            simulate      = simulate
        ),
        profile_mapping, role_mapping
    )
    print(f"Nombre d'utilisateurs N2F chargés : {len(df_n2f_users)}")

    if do_create:
        # Création des utilisateurs N2F
        created, status_col = create_users(
            df_agresso_users = df_agresso_users,
            df_n2f_users     = df_n2f_users,
            df_n2f_companies = df_n2f_companies,
            base_url         = base_url,
            client_id        = client_id,
            client_secret    = client_secret,
            simulate         = simulate,
            sandbox          = sandbox
        )
        reporting(
            created,
            "Aucun utilisateur ajouté",
            "Utilisateurs ajoutés",
            status_col
        )

    if do_update:
        # Mise à jour des utilisateurs N2F
        updated, status_col = update_users(
            df_agresso_users = df_agresso_users,
            df_n2f_users     = df_n2f_users,
            df_n2f_companies = df_n2f_companies,
            base_url         = base_url,
            client_id        = client_id,
            client_secret    = client_secret,
            simulate         = simulate,
            sandbox          = sandbox
        )
        reporting(
            updated,
            "Aucun utilisateur modifié",
            "Utilisateurs modifiés",
            status_col
        )

    if do_delete:
        # Suppression des utilisateurs N2F
        deleted, status_col = delete_users(
            df_agresso_users = df_agresso_users,
            df_n2f_users     = df_n2f_users,
            base_url         = base_url,
            client_id        = client_id,
            client_secret    = client_secret,
            simulate         = simulate
        )
        reporting(
            deleted,
            "Aucun utilisateur supprimé",
            "Utilisateurs supprimés",
            status_col
        )
