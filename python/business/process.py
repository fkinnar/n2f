import pandas as pd

from n2f.process import (
    get_projects as get_n2f_projects,
    get_customaxes_values as get_n2f_customaxes_values,
    get_customaxes as get_n2f_customaxes,
    get_roles as get_n2f_roles,
    get_userprofiles as get_n2f_userprofiles,
    get_companies as get_n2f_companies,
    get_users as get_n2f_users,
    create_users, delete_users, update_users
)
from agresso.process import select_users
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
        select_users(
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

    # Chargement des axes personnalisés N2F pour toutes les entreprises
    customaxes_list = []
    for company_id in df_n2f_companies["uuid"]:
        df_axes = get_n2f_customaxes(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            company_id=company_id,
            simulate=simulate
        )
        if not df_axes.empty:
            df_axes["company_id"] = company_id  # Pour garder la référence à la société
            customaxes_list.append(df_axes)

    if customaxes_list:
        df_n2f_customaxes = pd.concat(customaxes_list, ignore_index=True)
    else:
        df_n2f_customaxes = pd.DataFrame()

    print(f"Nombre d'axes personnalisés N2F chargés : {len(df_n2f_customaxes)}")

    # Chargement des valeurs des axes personnalisés N2F pour tous les axes de toutes les sociétés
    customaxes_values_list = []
    for _, row in df_n2f_customaxes.iterrows():
        company_id = row["company_id"]
        axe_id = row["uuid"]
        df_values = get_n2f_customaxes_values(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            company_id=company_id,
            axe_id=axe_id,
            simulate=simulate
        )
        if not df_values.empty:
            df_values["company_id"] = company_id
            df_values["axe_id"] = axe_id
            customaxes_values_list.append(df_values)

    if customaxes_values_list:
        df_n2f_customaxes_values = pd.concat(customaxes_values_list, ignore_index=True)
    else:
        df_n2f_customaxes_values = pd.DataFrame()

    print(f"Nombre de valeurs d'axes personnalisés N2F chargées : {len(df_n2f_customaxes_values)}")

    # Chargement des projets N2F pour toutes les entreprises
    projects_list = []
    for company_id in df_n2f_companies["uuid"]:
        df_projects = get_n2f_projects(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            company_id=company_id,
            simulate=simulate
        )
        if not df_projects.empty:
            df_projects["company_id"] = company_id  # Pour garder la référence à la société
            projects_list.append(df_projects)

    if projects_list:
        df_n2f_projects = pd.concat(projects_list, ignore_index=True)
    else:
        df_n2f_projects = pd.DataFrame()

    print(f"Nombre de projets N2F chargés : {len(df_n2f_projects)}")

    # Chargement des utilisateurs N2F et normalisation des données
    profile_mapping: dict[str, str] = build_n2f_mapping(df_n2f_userprofiles)
    # role_mapping: dict[str, str] = build_n2f_mapping(df_n2f_roles)
    role_mapping: dict[str, str] = {
        "gebruiker": "Utilisateur",
        "utilisateur": "Utilisateur"
    }
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


def reporting(
    result_df      : pd.DataFrame,
    empty_message  : str,
    update_message : str,
    status_col     : str
) -> None:
    """
    Génère un rapport à partir du DataFrame de résultats.
    Affiche le nombre de succès et d'échecs si une colonne de statut est fournie.
    """
    if result_df.empty:
        print(empty_message)
    else:
        print(update_message + " :")
        if status_col and status_col in result_df.columns:
            nb_success = result_df[status_col].sum()
            nb_total = len(result_df)
            nb_failed = nb_total - nb_success
            print(f"  Succès : {nb_success} / {nb_total}")
            print(f"  Échecs : {nb_failed} / {nb_total}")
        else:
            print(f"  Total : {len(result_df)}")