import pandas as pd
from typing import List, Dict, Any, Tuple

from n2f.api.customaxe import get_customaxes_values
from n2f.api.base import upsert, delete
from n2f.payload import create_project_upsert_payload
from helper.cache import get_from_cache, set_in_cache
from n2f.process.users import lookup_company_id

from business.process.helper import has_payload_changes


def get_axes(
    axe_id: str,
    base_url: str,
    client_id: str,
    client_secret: str,
    company_id: str,
    simulate: bool = False,
    cache: bool = True
) -> pd.DataFrame:
    """
    Récupère les valeurs d'un axe personnalisé d'une société depuis l'API N2F (toutes les pages) et retourne un DataFrame unique.
    La pagination est gérée automatiquement.

    Args:
        axe_id (str): Identifiant de l'axe ('projects', 'plates', 'subposts', etc.)
        base_url (str): URL de base de l'API N2F
        client_id (str): ID du client pour l'API N2F
        client_secret (str): Secret du client pour l'API N2F
        company_id (str): ID de la société
        simulate (bool): Si True, simule les appels sans les exécuter
        cache (bool): Si True, utilise le cache pour éviter les appels redondants

    Returns:
        pd.DataFrame: DataFrame contenant les valeurs de l'axe
    """
    if cache:
        cached = get_from_cache(f"get_axes_{axe_id}", base_url, client_id, company_id, simulate)
        if cached is not None:
            return cached

    all_values: List[pd.DataFrame] = []
    start = 0
    limit = 200

    while True:
        values_page = get_customaxes_values(
            base_url,
            client_id,
            client_secret,
            company_id,
            axe_id,
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
        set_in_cache(result, f"get_axes_{axe_id}", base_url, client_id, company_id, simulate)
    return result.copy(deep=True)


def build_axe_payload(
    project: pd.Series,
    sandbox: bool
) -> Dict[str, Any]:
    """
    Construit le payload JSON pour l'upsert (création ou mise à jour) d'un axe N2F.
    Retourne un dictionnaire prêt à être envoyé à l'API N2F.
    """
    payload = create_project_upsert_payload(project.to_dict(), sandbox)
    return payload


def create_axes(
    axe_id: str,
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
    Crée les valeurs d'un axe personnalisé dans N2F via l'API N2F pour une société donnée.
    Retourne un DataFrame avec une colonne 'created' (booléen) indiquant le succès ou l'échec.

    Args:
        axe_id (str): Identifiant de l'axe ('projects', 'plates', 'subposts', etc.)
        df_agresso_projects (pd.DataFrame): Données Agresso à synchroniser
        df_n2f_projects (pd.DataFrame): Données N2F existantes
        base_url (str): URL de base de l'API N2F
        client_id (str): ID du client pour l'API N2F
        client_secret (str): Secret du client pour l'API N2F
        df_n2f_companies (pd.DataFrame): DataFrame des entreprises N2F
        status_col (str): Nom de la colonne de statut
        simulate (bool): Si True, simule les appels sans les exécuter
        sandbox (bool): Si True, utilise le mode sandbox

    Returns:
        Tuple[pd.DataFrame, str]: DataFrame avec les résultats et nom de la colonne de statut
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
            payload = build_axe_payload(project, sandbox)
            endpoint = f"/companies/{company_id}/axes/{axe_id}"
            status = upsert(
                base_url,
                endpoint,
                client_id,
                client_secret,
                payload,
                simulate
            )
            created_list.append(status)
        else:
            created_list.append(False)
    projects_to_create[status_col] = created_list

    return projects_to_create, status_col


def update_axes(
    axe_id: str,
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
    Met à jour les valeurs d'un axe personnalisé dans N2F via l'API N2F pour une société donnée.
    Retourne un DataFrame avec une colonne 'updated' (booléen) indiquant le succès ou l'échec.

    Args:
        axe_id (str): Identifiant de l'axe ('projects', 'plates', 'subposts', etc.)
        df_agresso_projects (pd.DataFrame): Données Agresso à synchroniser
        df_n2f_projects (pd.DataFrame): Données N2F existantes
        base_url (str): URL de base de l'API N2F
        client_id (str): ID du client pour l'API N2F
        client_secret (str): Secret du client pour l'API N2F
        df_n2f_companies (pd.DataFrame): DataFrame des entreprises N2F
        status_col (str): Nom de la colonne de statut
        simulate (bool): Si True, simule les appels sans les exécuter
        sandbox (bool): Si True, utilise le mode sandbox

    Returns:
        Tuple[pd.DataFrame, str]: DataFrame avec les résultats et nom de la colonne de statut
    """
    if df_agresso_projects.empty or df_n2f_projects.empty:
        return pd.DataFrame(), status_col

    # Index N2F by code for fast lookup
    n2f_by_code = df_n2f_projects.set_index("code").to_dict(orient="index")

    axes_to_update: List[Dict] = []
    updated_list: List[bool] = []

    for _, project in df_agresso_projects[df_agresso_projects["code"].isin(df_n2f_projects["code"])].iterrows():
        payload = build_axe_payload(project, sandbox)
        code = project["code"]
        n2f_project = n2f_by_code.get(code, {})

        # Compare payload fields with N2F project fields
        if not has_payload_changes(payload, n2f_project):
            continue

        company_code = project.get("client")
        company_id = lookup_company_id(company_code, df_n2f_companies, sandbox)
        # On ne met à jour que si company_id est trouvé
        if company_id != "":
            endpoint = f"/companies/{company_id}/axes/{axe_id}"
            status = upsert(
                base_url,
                endpoint,
                client_id,
                client_secret,
                payload,
                simulate
            )
            updated_list.append(status)
            axes_to_update.append(project.to_dict())
        else:
            updated_list.append(False)
            axes_to_update.append(project.to_dict())

    if axes_to_update:
        df_result = pd.DataFrame(axes_to_update)
        df_result[status_col] = updated_list
        return df_result, status_col
    else:
        return pd.DataFrame(), status_col


def delete_axes(
    axe_id: str,
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
    Supprime les valeurs d'un axe personnalisé dans N2F via l'API N2F pour une société donnée.
    Retourne un DataFrame avec une colonne 'deleted' (booléen) indiquant le succès ou l'échec.

    Args:
        axe_id (str): Identifiant de l'axe ('projects', 'plates', 'subposts', etc.)
        df_agresso_projects (pd.DataFrame): Données Agresso à synchroniser
        df_n2f_projects (pd.DataFrame): Données N2F existantes
        base_url (str): URL de base de l'API N2F
        client_id (str): ID du client pour l'API N2F
        client_secret (str): Secret du client pour l'API N2F
        df_n2f_companies (pd.DataFrame): DataFrame des entreprises N2F
        status_col (str): Nom de la colonne de statut
        simulate (bool): Si True, simule les appels sans les exécuter
        sandbox (bool): Si True, utilise le mode sandbox

    Returns:
        Tuple[pd.DataFrame, str]: DataFrame avec les résultats et nom de la colonne de statut
    """
    # If N2F is empty, nothing to delete
    if df_n2f_projects.empty:
        return pd.DataFrame(), status_col

    if df_agresso_projects.empty:
        axes_to_delete = df_n2f_projects.copy()
    else:
        axes_to_delete = df_n2f_projects[~df_n2f_projects["code"].isin(df_agresso_projects["code"])].copy()

    if axes_to_delete.empty:
        return pd.DataFrame(), status_col

    deleted_list: List[bool] = []
    for _, project in axes_to_delete.iterrows():
        code = project["code"]
        # Pour la suppression, on a besoin du company_id du projet N2F
        # On peut le récupérer via le code du projet dans Agresso ou utiliser une valeur par défaut
        company_code = project.get("client", "")
        company_id = lookup_company_id(company_code, df_n2f_companies, sandbox)
        # On ne supprime que si company_id est trouvé
        if company_id != "":
            endpoint = f"/companies/{company_id}/axes/{axe_id}/"
            deleted = delete(
                base_url,
                endpoint,
                client_id,
                client_secret,
                code,
                simulate
            )
            deleted_list.append(deleted)
        else:
            deleted_list.append(False)
    axes_to_delete[status_col] = deleted_list

    return axes_to_delete, status_col
