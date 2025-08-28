import pandas as pd
from typing import List, Dict, Any, Tuple

from n2f.client import N2fApiClient
from n2f.payload import create_project_upsert_payload
from n2f.process.user import lookup_company_id
from business.process.helper import has_payload_changes

def get_axes(
    n2f_client: N2fApiClient,
    axe_id: str,
    company_id: str,
) -> pd.DataFrame:
    """Récupère les valeurs d'un axe via le client N2F."""
    return n2f_client.get_axe_values(company_id, axe_id)

def build_axe_payload(project: pd.Series, sandbox: bool) -> Dict[str, Any]:
    """Construit le payload pour l'upsert d'un axe."""
    return create_project_upsert_payload(project.to_dict(), sandbox)

def create_axes(
    n2f_client: N2fApiClient,
    axe_id: str,
    df_agresso_projects: pd.DataFrame,
    df_n2f_projects: pd.DataFrame,
    df_n2f_companies: pd.DataFrame,
    sandbox: bool,
    status_col: str = "created",
) -> Tuple[pd.DataFrame, str]:
    """Crée les valeurs d'un axe via le client N2F."""
    if df_agresso_projects.empty:
        return pd.DataFrame(), status_col

    projects_to_create = df_agresso_projects[~df_agresso_projects["code"].isin(df_n2f_projects["code"])].copy() if not df_n2f_projects.empty else df_agresso_projects.copy()

    if projects_to_create.empty:
        return pd.DataFrame(), status_col

    created_list: List[bool] = []
    for _, project in projects_to_create.iterrows():
        company_code = project.get("client")
        company_id = lookup_company_id(company_code, df_n2f_companies, sandbox)
        if company_id:
            payload = build_axe_payload(project, sandbox)
            status = n2f_client.upsert_axe_value(company_id, axe_id, payload)
            created_list.append(status)
        else:
            created_list.append(False)
    projects_to_create[status_col] = created_list
    return projects_to_create, status_col

def update_axes(
    n2f_client: N2fApiClient,
    axe_id: str,
    df_agresso_projects: pd.DataFrame,
    df_n2f_projects: pd.DataFrame,
    df_n2f_companies: pd.DataFrame,
    sandbox: bool,
    status_col: str = "updated",
) -> Tuple[pd.DataFrame, str]:
    """Met à jour les valeurs d'un axe via le client N2F."""
    if df_agresso_projects.empty or df_n2f_projects.empty:
        return pd.DataFrame(), status_col

    n2f_by_code = df_n2f_projects.set_index("code").to_dict(orient="index")
    axes_to_update: List[Dict] = []
    updated_list: List[bool] = []

    for _, project in df_agresso_projects[df_agresso_projects["code"].isin(df_n2f_projects["code"])].iterrows():
        payload = build_axe_payload(project, sandbox)
        if not has_payload_changes(payload, n2f_by_code.get(project["code"], {})):
            continue

        company_code = project.get("client")
        company_id = lookup_company_id(company_code, df_n2f_companies, sandbox)
        if company_id:
            status = n2f_client.upsert_axe_value(company_id, axe_id, payload)
            updated_list.append(status)
            axes_to_update.append(project.to_dict())
        else:
            updated_list.append(False)
            axes_to_update.append(project.to_dict())

    if axes_to_update:
        df_result = pd.DataFrame(axes_to_update)
        df_result[status_col] = updated_list
        return df_result, status_col
    return pd.DataFrame(), status_col

def delete_axes(
    n2f_client: N2fApiClient,
    axe_id: str,
    df_agresso_projects: pd.DataFrame,
    df_n2f_projects: pd.DataFrame,
    df_n2f_companies: pd.DataFrame,
    sandbox: bool,
    status_col: str = "deleted",
) -> Tuple[pd.DataFrame, str]:
    """Supprime les valeurs d'un axe via le client N2F."""
    if df_n2f_projects.empty:
        return pd.DataFrame(), status_col

    axes_to_delete = df_n2f_projects[~df_n2f_projects["code"].isin(df_agresso_projects["code"])].copy() if not df_agresso_projects.empty else df_n2f_projects.copy()

    if axes_to_delete.empty:
        return pd.DataFrame(), status_col

    deleted_list: List[bool] = []
    for _, project in axes_to_delete.iterrows():
        company_id = project.get("company_id") # Assumes company_id was added during get_axes
        if company_id:
            status = n2f_client.delete_axe_value(company_id, axe_id, project["code"])
            deleted_list.append(status)
        else:
            deleted_list.append(False)
    axes_to_delete[status_col] = deleted_list
    return axes_to_delete, status_col