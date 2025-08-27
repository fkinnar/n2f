import pandas as pd

from business.process.helper import reporting
from business.process.axe_types import AxeType, get_axe_mapping
from n2f.process import (
    get_axes as get_n2f_projects,
    get_companies as get_n2f_companies,
    create_axes as create_n2f_axes,
    delete_axes as delete_n2f_axes,
    update_axes as update_n2f_axes
)
from agresso.process import select


def synchronize(
    axe_type      : AxeType,
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
    Effectue la synchronisation des axes Agresso <-> N2F selon les options passées.
    """
    # Chargement des axes Agresso
    df_agresso_axes: pd.DataFrame = select(
        base_dir     = base_dir,
        db_user      = db_user,
        db_password  = db_password,
        sql_path     = sql_path,
        sql_filename = sql_filename,
        prod         = prod
    )

    # Chargement des entreprises N2F
    df_n2f_companies: pd.DataFrame = get_n2f_companies(
        base_url      = base_url,
        client_id     = client_id,
        client_secret = client_secret,
        simulate      = simulate
    )
    print(f"Nombre d'entreprises N2F chargées : {len(df_n2f_companies)}")

    # Récupération du mapping pour le type d'axe
    # Pour les projets, on utilise le mapping statique
    # Pour les plaques et subposts, on récupère dynamiquement depuis l'API
    company_id_for_mapping = df_n2f_companies["uuid"].iloc[0] if not df_n2f_companies.empty else ""
    sql_column, n2f_code = get_axe_mapping(
        axe_type=axe_type,
        base_url=base_url,
        client_id=client_id,
        client_secret=client_secret,
        company_id=company_id_for_mapping,
        simulate=simulate
    )

    if not df_agresso_axes.empty:
        df_agresso_axes = df_agresso_axes[
            df_agresso_axes["typ"].astype(str).str.upper() == sql_column
        ].copy()

    print(f"Nombre de {sql_column} Agresso chargés : {len(df_agresso_axes)}")

    # Chargement des axes N2F pour toutes les entreprises
    axes_list = []
    for company_id in df_n2f_companies["uuid"]:
        df_axes = get_n2f_projects(
            axe_id=n2f_code,
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            company_id=company_id,
            simulate=simulate
        )
        if not df_axes.empty:
            df_axes["company_id"] = company_id  # Pour garder la référence à la société
            axes_list.append(df_axes)

    if axes_list:
        df_n2f_axes = pd.concat(axes_list, ignore_index=True)
    else:
        df_n2f_axes = pd.DataFrame()

    print(f"Nombre de {sql_column} N2F chargés : {len(df_n2f_axes)}")

    if do_create:
        # Création des axes N2F (par société)
        created_df, status_col = create_n2f_axes(
            axe_id=n2f_code,
            df_agresso_projects = df_agresso_axes,
            df_n2f_projects     = df_n2f_axes,
            base_url            = base_url,
            client_id           = client_id,
            client_secret       = client_secret,
            df_n2f_companies    = df_n2f_companies,
            simulate            = simulate,
            sandbox             = sandbox
        )
        reporting(
            created_df,
            f"Aucun {sql_column} ajouté",
            f"{sql_column} ajoutés",
            status_col
        )

    if do_update:
        # Mise à jour des axes N2F
        updated_df, status_col = update_n2f_axes(
            axe_id=n2f_code,
            df_agresso_projects = df_agresso_axes,
            df_n2f_projects     = df_n2f_axes,
            base_url            = base_url,
            client_id           = client_id,
            client_secret       = client_secret,
            df_n2f_companies    = df_n2f_companies,
            simulate            = simulate,
            sandbox             = sandbox
        )
        reporting(
            updated_df,
            f"Aucun {sql_column} mis à jour",
            f"{sql_column} mis à jour",
            status_col
        )

    if do_delete:
        # Suppression des axes N2F
        deleted_df, status_col = delete_n2f_axes(
            axe_id=n2f_code,
            df_agresso_projects = df_agresso_axes,
            df_n2f_projects     = df_n2f_axes,
            base_url            = base_url,
            client_id           = client_id,
            client_secret       = client_secret,
            df_n2f_companies    = df_n2f_companies,
            simulate            = simulate,
            sandbox             = sandbox
        )
        reporting(
            deleted_df,
            f"Aucun {sql_column} supprimé",
            f"{sql_column} supprimés",
            status_col
        )


def synchronize_projects(
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
    Effectue la synchronisation des projets Agresso <-> N2F.
    """
    synchronize(
        axe_type=AxeType.PROJECTS,
        do_create=do_create,
        do_update=do_update,
        do_delete=do_delete,
        base_dir=base_dir,
        db_user=db_user,
        db_password=db_password,
        sql_path=sql_path,
        sql_filename=sql_filename,
        base_url=base_url,
        client_id=client_id,
        client_secret=client_secret,
        prod=prod,
        simulate=simulate,
        sandbox=sandbox
    )


def synchronize_plates(
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
    Effectue la synchronisation des plaques Agresso <-> N2F.
    """
    synchronize(
        axe_type=AxeType.PLATES,
        do_create=do_create,
        do_update=do_update,
        do_delete=do_delete,
        base_dir=base_dir,
        db_user=db_user,
        db_password=db_password,
        sql_path=sql_path,
        sql_filename=sql_filename,
        base_url=base_url,
        client_id=client_id,
        client_secret=client_secret,
        prod=prod,
        simulate=simulate,
        sandbox=sandbox
    )


def synchronize_subposts(
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
    Effectue la synchronisation des subposts Agresso <-> N2F.
    """
    synchronize(
        axe_type=AxeType.SUBPOSTS,
        do_create=do_create,
        do_update=do_update,
        do_delete=do_delete,
        base_dir=base_dir,
        db_user=db_user,
        db_password=db_password,
        sql_path=sql_path,
        sql_filename=sql_filename,
        base_url=base_url,
        client_id=client_id,
        client_secret=client_secret,
        prod=prod,
        simulate=simulate,
        sandbox=sandbox
    )