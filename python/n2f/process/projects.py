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
from n2f.process.users import lookup_company_id

from business.process.helper import has_payload_changes


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
    df_agresso_projects: pd.DataFrame,
    df_n2f_projects: pd.DataFrame,
    base_url: str,
    client_id: str,
    client_secret: str,
    df_n2f_companies: pd.DataFrame,
    status_col: str = "created",
    simulate: bool = False,
    sandbox: bool = False
) -> Tuple[pd.DataFrame, str]:
    """
    Crée les projets dans N2F via l'API N2F pour une société donnée.
    Retourne un DataFrame avec une colonne 'created' (booléen) indiquant le succès ou l'échec.
    """
    if df_agresso_projects.empty:
        return pd.DataFrame(), status_col

    if df_n2f_projects.empty:
        projects_to_create = df_agresso_projects.copy()
    else:
        projects_to_create = df_agresso_projects[~df_agresso_projects["code"].isin(df_n2f_projects["code"])].copy()

    if projects_to_create.empty:
        return pd.DataFrame(), status_col

    created_list: List[bool] = []
    for _, project in projects_to_create.iterrows():
        company_code = project.get("client")
        company_id = lookup_company_id(company_code, df_n2f_companies, sandbox)

        # On ne crée que si company_id est trouvé
        if company_id != "":
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
        else:
            created_list.append(False)
    projects_to_create[status_col] = created_list

    return projects_to_create, status_col


def update_projects(
    df_agresso_projects: pd.DataFrame,
    df_n2f_projects: pd.DataFrame,
    base_url: str,
    client_id: str,
    client_secret: str,
    df_n2f_companies: pd.DataFrame,
    status_col: str = "updated",
    simulate: bool = False,
    sandbox: bool = False
) -> Tuple[pd.DataFrame, str]:
    """
    Met à jour les projets dans N2F via l'API N2F pour une société donnée.
    Retourne un DataFrame avec une colonne 'updated' (booléen) indiquant le succès ou l'échec.
    """
    if df_agresso_projects.empty or df_n2f_projects.empty:
        return pd.DataFrame(), status_col

    # Index N2F by code for fast lookup
    n2f_by_code = df_n2f_projects.set_index("code").to_dict(orient="index")

    projects_to_update: List[Dict] = []
    updated_list: List[bool] = []

    for _, project in df_agresso_projects[df_agresso_projects["code"].isin(df_n2f_projects["code"])].iterrows():
        payload = build_project_payload(project, sandbox)
        code = project["code"]
        n2f_project = n2f_by_code.get(code, {})

        # Compare payload fields with N2F project fields
        if not has_payload_changes(payload, n2f_project):
            continue

        company_code = project.get("client")
        company_id = lookup_company_id(company_code, df_n2f_companies, sandbox)
        # On ne met à jour que si company_id est trouvé
        if company_id != "":
            status = update_project_api(
                base_url,
                client_id,
                client_secret,
                company_id,
                payload,
                simulate
            )
            updated_list.append(status)
            projects_to_update.append(project.to_dict())
        else:
            updated_list.append(False)
            projects_to_update.append(project.to_dict())

    if projects_to_update:
        df_result = pd.DataFrame(projects_to_update)
        df_result[status_col] = updated_list
        return df_result, status_col
    else:
        return pd.DataFrame(), status_col


def delete_projects(
    df_agresso_projects: pd.DataFrame,
    df_n2f_projects: pd.DataFrame,
    base_url: str,
    client_id: str,
    client_secret: str,
    df_n2f_companies: pd.DataFrame,
    status_col: str = "deleted",
    simulate: bool = False,
    sandbox: bool = False
) -> Tuple[pd.DataFrame, str]:
    """
    Supprime les projets dans N2F via l'API N2F pour une société donnée.
    Retourne un DataFrame avec une colonne 'deleted' (booléen) indiquant le succès ou l'échec.
    """
    # If N2F is empty, nothing to delete
    if df_n2f_projects.empty:
        return pd.DataFrame(), status_col

    if df_agresso_projects.empty:
        projects_to_delete = df_n2f_projects.copy()
    else:
        projects_to_delete = df_n2f_projects[~df_n2f_projects["code"].isin(df_agresso_projects["code"])].copy()

    if projects_to_delete.empty:
        return pd.DataFrame(), status_col

    deleted_list: List[bool] = []
    for _, project in projects_to_delete.iterrows():
        code = project["code"]
        # Pour la suppression, on a besoin du company_id du projet N2F
        # On peut le récupérer via le code du projet dans Agresso ou utiliser une valeur par défaut
        company_code = project.get("client", "")
        company_id = lookup_company_id(company_code, df_n2f_companies, sandbox)
        # On ne supprime que si company_id est trouvé
        if company_id != "":
            deleted = delete_project_api(
                base_url,
                client_id,
                client_secret,
                company_id,
                code,
                simulate
            )
            deleted_list.append(deleted)
        else:
            deleted_list.append(False)
    projects_to_delete[status_col] = deleted_list

    return projects_to_delete, status_col
