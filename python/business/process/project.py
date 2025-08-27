import pandas as pd

from business.process.helper import reporting
from n2f.process import (
    get_projects as get_n2f_projects,
    get_companies as get_n2f_companies,
    create_projects, delete_projects, update_projects
)
from agresso.process import select


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
    Effectue la synchronisation des projets Agresso <-> N2F selon les options passées.
    """
    # Chargement des projets Agresso
    df_agresso_projects: pd.DataFrame = select(
        base_dir     = base_dir,
        db_user      = db_user,
        db_password  = db_password,
        sql_path     = sql_path,
        sql_filename = sql_filename,
        prod         = prod
    )
    if not df_agresso_projects.empty:
        df_agresso_projects = df_agresso_projects[
            df_agresso_projects["typ"].astype(str).str.upper() == "PROJECT"
        ].copy()
    print(f"Nombre de projets Agresso chargés : {len(df_agresso_projects)}")

    # Chargement des entreprises N2F
    df_n2f_companies: pd.DataFrame = get_n2f_companies(
        base_url      = base_url,
        client_id     = client_id,
        client_secret = client_secret,
        simulate      = simulate
    )
    print(f"Nombre d'entreprises N2F chargées : {len(df_n2f_companies)}")

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

    if do_create:
        # Création des projets N2F (par société)
        created_df, status_col = create_projects(
            df_agresso_projects = df_agresso_projects,
            df_n2f_projects     = df_n2f_projects,
            base_url            = base_url,
            client_id           = client_id,
            client_secret       = client_secret,
            df_n2f_companies    = df_n2f_companies,
            simulate            = simulate,
            sandbox             = sandbox
        )
        reporting(
            created_df,
            "Aucun projet ajouté",
            "Projets ajoutés",
            status_col
        )

    if do_update:
        # Mise à jour des projets N2F
        updated_df, status_col = update_projects(
            df_agresso_projects = df_agresso_projects,
            df_n2f_projects     = df_n2f_projects,
            base_url            = base_url,
            client_id           = client_id,
            client_secret       = client_secret,
            df_n2f_companies    = df_n2f_companies,
            simulate            = simulate,
            sandbox             = sandbox
        )
        reporting(
            updated_df,
            "Aucun projet mis à jour",
            "Projets mis à jour",
            status_col
        )

    if do_delete:
        # Suppression des projets N2F
        deleted_df, status_col = delete_projects(
            df_agresso_projects = df_agresso_projects,
            df_n2f_projects     = df_n2f_projects,
            base_url            = base_url,
            client_id           = client_id,
            client_secret       = client_secret,
            df_n2f_companies    = df_n2f_companies,
            simulate            = simulate,
            sandbox             = sandbox
        )
        reporting(
            deleted_df,
            "Aucun projet supprimé",
            "Projets supprimés",
            status_col
        )