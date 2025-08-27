import pandas as pd

from business.process.helper import reporting
from n2f.process import (
    get_projects as get_n2f_projects,
    get_customaxes_values as get_n2f_customaxes_values,
    get_customaxes as get_n2f_customaxes,
    get_companies as get_n2f_companies,
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
    Effectue la synchronisation des utilisateurs Agresso <-> N2F selon les options passées.
    """

    # Chargement des customaxes Agresso
    df_agresso_customaxes: pd.DataFrame = select(
        base_dir     = base_dir,
        db_user      = db_user,
        db_password  = db_password,
        sql_path     = sql_path,
        sql_filename = sql_filename,
        prod         = prod
    )
    print(f"Nombre de customaxes Agresso chargés : {len(df_agresso_customaxes)}")

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

    if do_create:
        # Création des utilisateurs N2F
        pass

    if do_update:
        # Mise à jour des utilisateurs N2F
        pass

    if do_delete:
        # Suppression des utilisateurs N2F
        pass