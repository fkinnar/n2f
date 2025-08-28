import pandas as pd
from typing import Optional, Set, Dict, Any, List, Tuple

from n2f.client import N2fApiClient
from n2f.payload import create_user_upsert_payload
# Import déplacé dans la fonction pour éviter l'import circulaire
from n2f.api_result import ApiResult
from n2f.process.helper import add_api_logging_columns

# Note: get_users is now in the client, but we keep the process file for business logic

def lookup_company_id(company_code: str, df_n2f_companies: pd.DataFrame, sandbox: bool = False) -> str:
    """Recherche l'UUID d'une entreprise à partir de son code."""
    if df_n2f_companies.empty:
        return ""
    match = df_n2f_companies.loc[df_n2f_companies["code"] == company_code, "uuid"]
    if not match.empty:
        return match.iloc[0]
    if sandbox and not df_n2f_companies.empty and "uuid" in df_n2f_companies.columns:
        return df_n2f_companies["uuid"].iloc[0]
    return ""

def build_user_payload(
    user: pd.Series,
    df_agresso_users: pd.DataFrame,
    df_n2f_users: pd.DataFrame,
    n2f_client: N2fApiClient,
    df_n2f_companies: pd.DataFrame,
    sandbox: bool,
    manager_email: str = None
) -> Dict[str, Any]:
    """Construit le payload JSON pour l'upsert d'un utilisateur."""
    company_id = lookup_company_id(user["Entreprise"], df_n2f_companies)
    payload = create_user_upsert_payload(user.to_dict(), company_id, sandbox)
    if manager_email is None:
        payload["managerMail"] = ensure_manager_exists(
            user["Manager"], df_agresso_users, df_n2f_users, n2f_client, df_n2f_companies, sandbox
        )
    else:
        payload["managerMail"] = manager_email
    return payload

def ensure_manager_exists(
    manager_email: str,
    df_agresso_users: pd.DataFrame,
    df_n2f_users: pd.DataFrame,
    n2f_client: N2fApiClient,
    df_n2f_companies: pd.DataFrame,
    sandbox: bool,
    _visited: Optional[Set[str]] = None
) -> str:
    """Vérifie récursivement si le manager existe dans N2F, sinon le crée."""
    if not manager_email or pd.isna(manager_email):
        return ""

    if _visited is None:
        _visited = set()

    if manager_email in _visited:
        return ""
    _visited.add(manager_email)

    if manager_email in df_n2f_users["mail"].values:
        return manager_email

    if manager_email in df_agresso_users["AdresseEmail"].values:
        user = df_agresso_users[df_agresso_users["AdresseEmail"] == manager_email].iloc[0]

        manager_of_manager_mail = ensure_manager_exists(
            user["Manager"], df_agresso_users, df_n2f_users,
            n2f_client, df_n2f_companies, sandbox, _visited
        )

        payload = build_user_payload(
            user, df_agresso_users, df_n2f_users, n2f_client, df_n2f_companies, sandbox, manager_of_manager_mail
        )
        status = n2f_client.create_user(payload)

        df_n2f_users.loc[len(df_n2f_users)] = {"mail": manager_email}
        return manager_email if status else ""

    return ""

def create_users(
    df_agresso_users: pd.DataFrame,
    df_n2f_users: pd.DataFrame,
    df_n2f_companies: pd.DataFrame,
    n2f_client: N2fApiClient,
    sandbox: bool,
    status_col: str = "created",
) -> Tuple[pd.DataFrame, str]:
    """Crée les utilisateurs manquants."""
    if df_agresso_users.empty:
        return pd.DataFrame(), status_col

    users_to_create = df_agresso_users[~df_agresso_users["AdresseEmail"].isin(df_n2f_users["mail"])].copy() if not df_n2f_users.empty else df_agresso_users.copy()

    api_results: List[ApiResult] = []
    for _, user in users_to_create.iterrows():
        payload = build_user_payload(user, df_agresso_users, df_n2f_users, n2f_client, df_n2f_companies, sandbox)
        api_result = n2f_client.create_user(payload)
        api_results.append(api_result)

    # Ajouter les colonnes de logging
    users_to_create[status_col] = [result.success for result in api_results]
    users_to_create = add_api_logging_columns(users_to_create, api_results)

    return users_to_create, status_col

def update_users(
    df_agresso_users: pd.DataFrame,
    df_n2f_users: pd.DataFrame,
    df_n2f_companies: pd.DataFrame,
    n2f_client: N2fApiClient,
    sandbox: bool,
    status_col: str = "updated",
) -> Tuple[pd.DataFrame, str]:
    """Met à jour les utilisateurs existants si nécessaire."""
    if df_agresso_users.empty or df_n2f_users.empty:
        return pd.DataFrame(), status_col

    users_to_update: List[Dict] = []
    api_results: List[ApiResult] = []
    n2f_by_mail = df_n2f_users.set_index("mail").to_dict(orient="index")

    for _, user in df_agresso_users[df_agresso_users["AdresseEmail"].isin(df_n2f_users["mail"])].iterrows():
        payload = build_user_payload(user, df_agresso_users, df_n2f_users, n2f_client, df_n2f_companies, sandbox)
        n2f_user = n2f_by_mail.get(user["AdresseEmail"], {})
        # Ajouter l'email car set_index("mail") le retire des valeurs
        if n2f_user:
            n2f_user["mail"] = user["AdresseEmail"]

        from business.process.helper import has_payload_changes
        if not has_payload_changes(payload, n2f_user, 'user'):
            continue

        api_result = n2f_client.update_user(payload)
        api_results.append(api_result)
        users_to_update.append(user.to_dict())

    if users_to_update:
        df_result = pd.DataFrame(users_to_update)
        df_result[status_col] = [result.success for result in api_results]
        df_result = add_api_logging_columns(df_result, api_results)

        return df_result, status_col
    return pd.DataFrame(), status_col

def delete_users(
    df_agresso_users: pd.DataFrame,
    df_n2f_users: pd.DataFrame,
    n2f_client: N2fApiClient,
    status_col: str = "deleted",
) -> Tuple[pd.DataFrame, str]:
    """Supprime les utilisateurs obsolètes."""
    if df_n2f_users.empty:
        return pd.DataFrame(), status_col

    users_to_delete = df_n2f_users[~df_n2f_users["mail"].isin(df_agresso_users["AdresseEmail"])].copy() if not df_agresso_users.empty else df_n2f_users.copy()

    if not users_to_delete.empty:
        api_results: List[ApiResult] = [n2f_client.delete_user(mail) for mail in users_to_delete["mail"]]
        users_to_delete[status_col] = [result.success for result in api_results]
        users_to_delete = add_api_logging_columns(users_to_delete, api_results)

    return users_to_delete, status_col