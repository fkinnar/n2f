import pandas as pd

from helper.context import SyncContext
from n2f.client import N2fApiClient
from business.process.helper import reporting
from business.process.axe_types import AxeType, get_axe_mapping
from n2f.process.axe import (
    get_axes as get_n2f_projects,
    create_axes as create_n2f_axes,
    delete_axes as delete_n2f_axes,
    update_axes as update_n2f_axes
)
from agresso.process import select

from business.constants import AGRESSO_COL_AXE_TYPE, COL_UUID

def _load_agresso_axes(context: SyncContext, sql_filename: str, sql_column_filter: str) -> pd.DataFrame:
    """Charge et filtre les axes depuis Agresso."""
    df_agresso_axes = select(
        base_dir=context.base_dir,
        db_user=context.db_user,
        db_password=context.db_password,
        sql_path=context.config["agresso"]["sql-path"],
        sql_filename=sql_filename,
        prod=context.config["agresso"]["prod"]
    )
    if not df_agresso_axes.empty:
        df_agresso_axes = df_agresso_axes[
            df_agresso_axes[AGRESSO_COL_AXE_TYPE].astype(str).str.upper() == sql_column_filter
        ].copy()
    print(f"Number of {sql_column_filter} Agresso loaded : {len(df_agresso_axes)}")
    return df_agresso_axes

def _load_n2f_axes(n2f_client: N2fApiClient, df_n2f_companies: pd.DataFrame, n2f_code: str) -> pd.DataFrame:
    """Charge les valeurs d'axes N2F pour toutes les entreprises."""
    axes_list = []
    for company_id in df_n2f_companies["uuid"]:
        df_axes = get_n2f_projects(
            n2f_client=n2f_client,
            axe_id=n2f_code,
            company_id=company_id
        )
        if not df_axes.empty:
            df_axes["company_id"] = company_id
            axes_list.append(df_axes)
    df_n2f_axes = pd.concat(axes_list, ignore_index=True) if axes_list else pd.DataFrame()
    print(f"Number of N2F axe values loaded : {len(df_n2f_axes)}")
    return df_n2f_axes

def _get_scope_from_axe_type(axe_type: AxeType) -> str:
    """Détermine le scope à partir du type d'axe."""
    scope_map = {
        AxeType.PROJECTS: "projects",
        AxeType.PLATES: "plates",
        AxeType.SUBPOSTS: "subposts"
    }
    return scope_map.get(axe_type, "unknown")

def _perform_sync_actions(
    context: SyncContext,
    n2f_client: N2fApiClient,
    n2f_code: str,
    sql_column: str,
    df_agresso_axes: pd.DataFrame,
    df_n2f_axes: pd.DataFrame,
    df_n2f_companies: pd.DataFrame,
    scope: str
) -> list[pd.DataFrame]:
    """Exécute les actions de création, mise à jour et suppression pour les axes."""
    results = []

    if context.args.create:
        created_df, status_col = create_n2f_axes(
            n2f_client=n2f_client, axe_id=n2f_code, df_agresso_projects=df_agresso_axes,
            df_n2f_projects=df_n2f_axes, df_n2f_companies=df_n2f_companies,
            sandbox=context.config["n2f"]["sandbox"], scope=scope
        )
        reporting(created_df, f"No {sql_column} added", f"{sql_column} added", status_col)
        if not created_df.empty:
            results.append(created_df)

    if context.args.update:
        updated_df, status_col = update_n2f_axes(
            n2f_client=n2f_client, axe_id=n2f_code, df_agresso_projects=df_agresso_axes,
            df_n2f_projects=df_n2f_axes, df_n2f_companies=df_n2f_companies,
            sandbox=context.config["n2f"]["sandbox"], scope=scope
        )
        reporting(updated_df, f"No {sql_column} updated", f"{sql_column} updated", status_col)
        if not updated_df.empty:
            results.append(updated_df)

    if context.args.delete:
        deleted_df, status_col = delete_n2f_axes(
            n2f_client=n2f_client, axe_id=n2f_code, df_agresso_projects=df_agresso_axes,
            df_n2f_projects=df_n2f_axes, df_n2f_companies=df_n2f_companies,
            sandbox=context.config["n2f"]["sandbox"], scope=scope
        )
        reporting(deleted_df, f"Aucun {sql_column} supprimé", f"{sql_column} supprimés", status_col)
        if not deleted_df.empty:
            results.append(deleted_df)

    return results

def synchronize(
    context: SyncContext,
    axe_type: AxeType,
    sql_filename: str,
) -> list[pd.DataFrame]:
    """Orchestre la synchronisation des axes Agresso <-> N2F."""
    n2f_client = N2fApiClient(context)

    df_n2f_companies = n2f_client.get_companies()
    print(f"Number of N2F companies loaded : {len(df_n2f_companies)}")

    company_id_for_mapping = df_n2f_companies[COL_UUID].iloc[0] if not df_n2f_companies.empty else ""
    sql_column, n2f_code = get_axe_mapping(
        axe_type=axe_type, n2f_client=n2f_client, company_id=company_id_for_mapping
    )

    df_agresso_axes = _load_agresso_axes(context, sql_filename, sql_column)
    df_n2f_axes = _load_n2f_axes(n2f_client, df_n2f_companies, n2f_code)

    scope = _get_scope_from_axe_type(axe_type)
    results = _perform_sync_actions(
        context, n2f_client, n2f_code, sql_column, df_agresso_axes, df_n2f_axes, df_n2f_companies, scope
    )

    return results

def synchronize_projects(context: SyncContext, sql_filename: str) -> list[pd.DataFrame]:
    """Effectue la synchronisation des projets Agresso <-> N2F."""
    return synchronize(context=context, axe_type=AxeType.PROJECTS, sql_filename=sql_filename)

def synchronize_plates(context: SyncContext, sql_filename: str) -> list[pd.DataFrame]:
    """Effectue la synchronisation des plaques Agresso <-> N2F."""
    return synchronize(context=context, axe_type=AxeType.PLATES, sql_filename=sql_filename)

def synchronize_subposts(context: SyncContext, sql_filename: str) -> list[pd.DataFrame]:
    """Effectue la synchronisation des subposts Agresso <-> N2F."""
    return synchronize(context=context, axe_type=AxeType.SUBPOSTS, sql_filename=sql_filename)
