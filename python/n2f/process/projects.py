import pandas as pd
from typing import List, Dict, Any, Tuple

from n2f.api.project import (
    get_projects as get_projects_api,
    create_project as create_project_api,
    update_project as update_project_api,
    delete_project as delete_project_api
)
from n2f.payload import create_project_upsert_payload
from helper.cache import get_from_cache, set_in_cache


def get_projects(
    base_url: str,
    client_id: str,
    client_secret: str,
    company_id: str,
    simulate: bool = False,
    cache: bool = True
) -> pd.DataFrame:
    """
    Récupère les projets d'une société depuis l'API N2F (axe 'projects', toutes les pages) et retourne un DataFrame unique.
    La pagination est gérée automatiquement.
    """
    if cache:
        cached = get_from_cache("get_projects", base_url, client_id, company_id, simulate)
        if cached is not None:
            return cached

    all_values: List[pd.DataFrame] = []
    start = 0
    limit = 200

    while True:
        values_page = get_projects_api(
            base_url,
            client_id,
            client_secret,
            company_id,
            start,
            limit,
            simulate
        )
        if not values_page:
            break
        df_page = pd.DataFrame(values_page)
        if df_page.empty:
            break
        all_values.append(df_page)
        if len(df_page) < limit:
            break
        start += limit

    if all_values:
        result = pd.concat(all_values, ignore_index=True)
    else:
        result = pd.DataFrame()

    if cache:
        set_in_cache(result, "get_projects", base_url, client_id, company_id, simulate)
    return result.copy(deep=True)


def build_project_payload(
    project: pd.Series,
    sandbox: bool
) -> Dict[str, Any]:
    """
    Construit le payload JSON pour l'upsert (création ou mise à jour) d'un projet N2F.
    Retourne un dictionnaire prêt à être envoyé à l'API N2F.
    """
    payload = create_project_upsert_payload(project.to_dict(), sandbox)
    return payload


def create_projects(
    df_projects: pd.DataFrame,
    base_url: str,
    client_id: str,
    client_secret: str,
    company_id: str,
    status_col: str = "created",
    simulate: bool = False,
    sandbox: bool = False
) -> Tuple[pd.DataFrame, str]:
    """
    Crée les projets dans N2F via l'API N2F pour une société donnée.
    Retourne un DataFrame avec une colonne 'created' (booléen) indiquant le succès ou l'échec.
    """
    if df_projects.empty:
        return pd.DataFrame(), status_col

    created_list: List[bool] = []
    for _, project in df_projects.iterrows():
        payload = build_project_payload(project, sandbox)
        status = create_project_api(
            base_url,
            client_id,
            client_secret,
            company_id,
            payload,
            simulate
        )
        created_list.append(status)
    df_projects[status_col] = created_list

    return df_projects, status_col


def update_projects(
    df_projects: pd.DataFrame,
    base_url: str,
    client_id: str,
    client_secret: str,
    company_id: str,
    status_col: str = "updated",
    simulate: bool = False,
    sandbox: bool = False
) -> Tuple[pd.DataFrame, str]:
    """
    Met à jour les projets dans N2F via l'API N2F pour une société donnée.
    Retourne un DataFrame avec une colonne 'updated' (booléen) indiquant le succès ou l'échec.
    """
    if df_projects.empty:
        return pd.DataFrame(), status_col

    updated_list: List[bool] = []
    for _, project in df_projects.iterrows():
        payload = build_project_payload(project, sandbox)
        status = update_project_api(
            base_url,
            client_id,
            client_secret,
            company_id,
            payload,
            simulate
        )
        updated_list.append(status)
    df_projects[status_col] = updated_list

    return df_projects, status_col


def delete_projects(
    df_projects: pd.DataFrame,
    base_url: str,
    client_id: str,
    client_secret: str,
    company_id: str,
    status_col: str = "deleted",
    simulate: bool = False
) -> Tuple[pd.DataFrame, str]:
    """
    Supprime les projets dans N2F via l'API N2F pour une société donnée.
    Retourne un DataFrame avec une colonne 'deleted' (booléen) indiquant le succès ou l'échec.
    """
    if df_projects.empty:
        return pd.DataFrame(), status_col

    deleted_list: List[bool] = []
    for _, project in df_projects.iterrows():
        code = project["code"]
        deleted = delete_project_api(
            base_url,
            client_id,
            client_secret,
            company_id,
            code,
            simulate
        )
        deleted_list.append(deleted)
    df_projects[status_col] = deleted_list

    return df_projects, status_col
