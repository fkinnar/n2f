import pandas as pd
from typing import List, Dict, Any, Tuple

from n2f.client import N2fApiClient
from n2f.payload import create_project_upsert_payload

# Import déplacé dans les fonctions pour éviter l'import circulaire
# Import déplacé dans la fonction pour éviter l'import circulaire
from n2f.api_result import ApiResult
from core.logging import add_api_logging_columns
from business.process.helper import has_payload_changes, log_error
from core.exceptions import SyncException


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
    scope: str = "projects",
) -> Tuple[pd.DataFrame, str]:
    """
    Crée les valeurs d'un axe via le client N2F.
    """
    if df_agresso_projects.empty:
        return pd.DataFrame(), status_col

    projects_to_create = (
        df_agresso_projects[
            ~df_agresso_projects["code"].isin(df_n2f_projects["code"])
        ].copy()
        if not df_n2f_projects.empty
        else df_agresso_projects.copy()
    )

    if projects_to_create.empty:
        return pd.DataFrame(), status_col

    api_results: List[ApiResult] = []
    for _, project in projects_to_create.iterrows():
        try:
            # Import déplacé ici pour éviter les imports circulaires
            from n2f.process.user import lookup_company_id

            company_code = project.get("client")
            company_id = lookup_company_id(company_code, df_n2f_companies, sandbox)
            if company_id:
                payload = build_axe_payload(project, sandbox)
                api_result = n2f_client.upsert_axe_value(
                    company_id, axe_id, payload, "create", scope
                )
                api_results.append(api_result)
            else:
                error_msg = f"Company not found: {company_code}"
                log_error(
                    scope.upper(),
                    "CREATE",
                    project.get("code", "unknown"),
                    Exception(error_msg),
                )
                api_results.append(
                    ApiResult.error_result(
                        "Company not found",
                        error_details=f"Company code: {company_code}",
                        action_type="create",
                        object_type="axe",
                        object_id=project.get("code", "unknown"),
                        scope=scope,
                    )
                )
        except SyncException as e:
            # Log l'erreur mais continue le processus
            log_error(
                scope.upper(),
                "CREATE",
                project.get("code", "unknown"),
                e,
                f"Company: {project.get('client', 'unknown')}",
            )
            # Créer un ApiResult d'erreur pour maintenir la cohérence
            api_results.append(
                ApiResult.error_result(
                    str(e),
                    error_details=str(e),
                    action_type="create",
                    object_type="axe",
                    object_id=project.get("code", "unknown"),
                    scope=scope,
                )
            )

    projects_to_create[status_col] = [result.success for result in api_results]
    projects_to_create = add_api_logging_columns(projects_to_create, api_results)

    return projects_to_create, status_col


def update_axes(
    n2f_client: N2fApiClient,
    axe_id: str,
    df_agresso_projects: pd.DataFrame,
    df_n2f_projects: pd.DataFrame,
    df_n2f_companies: pd.DataFrame,
    sandbox: bool,
    status_col: str = "updated",
    scope: str = "projects",
) -> Tuple[pd.DataFrame, str]:
    """Met à jour les valeurs d'un axe via le client N2F."""
    if df_agresso_projects.empty or df_n2f_projects.empty:
        return pd.DataFrame(), status_col

    n2f_by_code = df_n2f_projects.set_index("code").to_dict(orient="index")
    axes_to_update: List[Dict[str, Any]] = []
    api_results: List[ApiResult] = []

    for _, project in df_agresso_projects[
        df_agresso_projects["code"].isin(df_n2f_projects["code"])
    ].iterrows():
        payload = build_axe_payload(project, sandbox)
        n2f_project = n2f_by_code.get(project["code"], {})

        if not has_payload_changes(payload, n2f_project, "axe"):
            continue

        axes_to_update.append(project.to_dict())
        try:
            # Import déplacé ici pour éviter les imports circulaires
            from n2f.process.user import lookup_company_id

            company_code = project.get("client")
            company_id = lookup_company_id(company_code, df_n2f_companies, sandbox)
            if company_id:
                api_result = n2f_client.upsert_axe_value(
                    company_id, axe_id, payload, "update", scope
                )
                api_results.append(api_result)
            else:
                error_msg = f"Company not found: {company_code}"
                log_error(
                    scope.upper(),
                    "UPDATE",
                    project.get("code", "unknown"),
                    Exception(error_msg),
                )
                api_results.append(
                    ApiResult.error_result(
                        "Company not found",
                        error_details=f"Company code: {company_code}",
                        action_type="update",
                        object_type="axe",
                        object_id=project.get("code", "unknown"),
                        scope=scope,
                    )
                )
        except SyncException as e:
            # Log l'erreur mais continue le processus
            log_error(
                scope.upper(),
                "UPDATE",
                project.get("code", "unknown"),
                e,
                f"Company: {project.get('client', 'unknown')}",
            )
            # Créer un ApiResult d'erreur pour maintenir la cohérence
            api_results.append(
                ApiResult.error_result(
                    str(e),
                    error_details=str(e),
                    action_type="update",
                    object_type="axe",
                    object_id=project.get("code", "unknown"),
                    scope=scope,
                )
            )

    if axes_to_update:
        df_result = pd.DataFrame(axes_to_update)
        df_result[status_col] = [result.success for result in api_results]
        df_result = add_api_logging_columns(df_result, api_results)

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
    scope: str = "projects",
) -> Tuple[pd.DataFrame, str]:
    """Supprime les valeurs d'un axe via le client N2F."""
    if df_n2f_projects.empty:
        return pd.DataFrame(), status_col

    axes_to_delete = (
        df_n2f_projects[
            ~df_n2f_projects["code"].isin(df_agresso_projects["code"])
        ].copy()
        if not df_agresso_projects.empty
        else df_n2f_projects.copy()
    )

    if axes_to_delete.empty:
        return pd.DataFrame(), status_col

    api_results: List[ApiResult] = []
    for _, project in axes_to_delete.iterrows():
        try:
            company_id = project.get(
                "company_id"
            )  # Assumes company_id was added during get_axes
            if company_id:
                api_result = n2f_client.delete_axe_value(
                    company_id, axe_id, project["code"], scope
                )
                api_results.append(api_result)
            else:
                error_msg = "Company ID not found: company_id field missing"
                log_error(
                    scope.upper(),
                    "DELETE",
                    project.get("code", "unknown"),
                    Exception(error_msg),
                )
                api_results.append(
                    ApiResult.error_result(
                        "Company ID not found",
                        error_details="company_id field missing",
                        action_type="delete",
                        object_type="axe",
                        object_id=project.get("code", "unknown"),
                        scope=scope,
                    )
                )
        except SyncException as e:
            # Log l'erreur mais continue le processus
            log_error(
                scope.upper(),
                "DELETE",
                project.get("code", "unknown"),
                e,
                f"Company ID: {project.get('company_id', 'missing')}",
            )
            # Créer un ApiResult d'erreur pour maintenir la cohérence
            api_results.append(
                ApiResult.error_result(
                    str(e),
                    error_details=str(e),
                    action_type="delete",
                    object_type="axe",
                    object_id=project.get("code", "unknown"),
                    scope=scope,
                )
            )

    axes_to_delete[status_col] = [result.success for result in api_results]
    axes_to_delete = add_api_logging_columns(axes_to_delete, api_results)

    return axes_to_delete, status_col
