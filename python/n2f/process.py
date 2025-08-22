import pandas as pd
from typing import Optional, Set, Dict, Any, List, Tuple

from n2f.api import get_companies as get_companies_api, get_users as get_users_api, delete_user as delete_user_api, create_user as create_user_api, update_user as update_user_api
from n2f.payload import create_upsert_payload


def get_users(
        base_url: str,
        client_id: str,
        client_secret: str,
        simulate: bool = False
    ) -> pd.DataFrame:
    """
    Récupère tous les utilisateurs depuis l'API N2F (toutes les pages) et retourne un DataFrame unique.
    Respecte le quota d'appels à l'API (en secondes entre chaque appel).
    La pagination est gérée automatiquement.
    """

    all_users = []
    start = 0
    limit = 200

    while True:
        users_page = get_users_api(
            base_url,
            client_id,
            client_secret,
            start,
            limit,
            simulate
        )
        if not users_page:
            break
        df_page = pd.DataFrame(users_page)
        if df_page.empty:
            break
        all_users.append(df_page)
        if len(df_page) < limit:
            break
        start += limit

    if all_users:
        return pd.concat(all_users, ignore_index=True)
    else:
        return pd.DataFrame()


def get_companies(
        base_url: str,
        client_id: str,
        client_secret: str,
        simulate: bool = False
    ) -> pd.DataFrame:
    """
    Récupère toutes les entreprises depuis l'API N2F (toutes les pages) et retourne un DataFrame unique.
    Respecte le quota d'appels à l'API (en secondes entre chaque appel).
    La pagination est gérée automatiquement.
    """

    all_companies = []
    start = 0
    limit = 200

    while True:
        companies_page = get_companies_api(
            base_url,
            client_id,
            client_secret,
            start,
            limit,
            simulate
        )
        if not companies_page:
            break
        df_page = pd.DataFrame(companies_page)
        if df_page.empty:
            break
        all_companies.append(df_page)
        if len(df_page) < limit:
            break
        start += limit

    if all_companies:
        return pd.concat(all_companies, ignore_index=True)
    else:
        return pd.DataFrame()


def ensure_manager_exists(
    manager_email: str,
    df_agresso_users: pd.DataFrame,
    df_n2f_users: pd.DataFrame,
    base_url: str,
    client_id: str,
    client_secret: str,
    df_n2f_companies: pd.DataFrame,
    simulate: bool,
    sandbox: bool,
    _visited: Optional[Set[str]] = None
) -> str:
    """Vérifie récursivement si le manager existe dans N2F, sinon le crée (ainsi que ses managers).
    Retourne l'email du manager si trouvé/créé, sinon une chaîne vide.
    Le paramètre _visited permet d'éviter les boucles dans la hiérarchie.
    """

    if not manager_email or pd.isna(manager_email):
        return ""

    if _visited is None:
        _visited = set()

    if manager_email in _visited:
        # Boucle détectée dans la hiérarchie
        return ""
    _visited.add(manager_email)

    if manager_email in df_n2f_users["mail"].values:
        return manager_email

    if manager_email in df_agresso_users["AdresseEmail"].values:
        # On récupère la ligne du manager
        user = df_agresso_users[df_agresso_users["AdresseEmail"] == manager_email].iloc[0]

        # On s'assure que le manager de ce manager existe aussi
        manager_of_manager = user["Manager"]
        manager_of_manager_mail = ensure_manager_exists(
            manager_of_manager, df_agresso_users, df_n2f_users,
            base_url, client_id, client_secret, df_n2f_companies, simulate, sandbox, _visited
        )

        # On crée le manager avec le bon managerMail
        payload = build_user_payload(
            user,
            df_agresso_users,
            df_n2f_users,
            df_n2f_companies,
            base_url,
            client_id,
            client_secret,
            simulate,
            sandbox,
            manager_of_manager_mail
        )
        status = create_user_api(
            base_url,
            client_id,
            client_secret,
            payload,
            simulate
        )

        # On ajoute à df_n2f pour éviter de le refaire
        df_n2f_users.loc[len(df_n2f_users)] = {"mail": manager_email}

        return manager_email if status else ""

    # Manager inconnu, on met ""
    return ""


def lookup_company_id(company_code: str, df_n2f_companies: pd.DataFrame) -> str:
    """
    Recherche l'UUID d'une entreprise à partir de son code dans le DataFrame des entreprises N2F.

    Args:
        company_code (str): Code de l'entreprise à rechercher.
        df_n2f_companies (pd.DataFrame): DataFrame contenant les entreprises N2F.

    Returns:
        str: UUID de l'entreprise si trouvé, sinon une chaîne vide.
    """
    if df_n2f_companies.empty:
        return ""

    match = df_n2f_companies.loc[df_n2f_companies["code"] == company_code, "uuid"]
    return match.iloc[0] if not match.empty else ""


def build_user_payload(
    user: pd.Series,
    df_agresso_users: pd.DataFrame,
    df_n2f_users: pd.DataFrame,
    df_n2f_companies: pd.DataFrame,
    base_url: str,
    client_id: str,
    client_secret: str,
    simulate: bool,
    sandbox: bool,
    manager_email: str = None
) -> Dict[str, Any]:
    """
    Construit le payload JSON pour l'upsert (création ou mise à jour) d'un utilisateur N2F,
    en s'assurant que le manager existe (création récursive si besoin).
    Retourne un dictionnaire prêt à être envoyé à l'API N2F.
    """
    company_id = lookup_company_id(user["Entreprise"], df_n2f_companies)
    payload = create_upsert_payload(user.to_dict(), company_id, sandbox)
    if manager_email is None:
        payload["managerMail"] = ensure_manager_exists(
            user["Manager"],
            df_agresso_users,
            df_n2f_users,
            base_url,
            client_id,
            client_secret,
            df_n2f_companies,
            simulate,
            sandbox
        )
    else:
        payload["managerMail"] = manager_email

    return payload


def create_users(
    df_agresso_users: pd.DataFrame,
    df_n2f_users: pd.DataFrame,
    df_n2f_companies: pd.DataFrame,
    base_url: str,
    client_id: str,
    client_secret: str,
    status_col: str = "created",
    simulate: bool = False,
    sandbox: bool = False
) -> Tuple[pd.DataFrame, str]:
    """
    Crée les utilisateurs présents dans Agresso mais absents de N2F via l'API N2F.
    Retourne un DataFrame avec une colonne 'created' (booléen) indiquant le succès ou l'échec.
    """

    if df_agresso_users.empty:
        return pd.DataFrame(), status_col
    if df_n2f_users.empty:
        users_to_create = df_agresso_users.copy()
    else:
        users_to_create = df_agresso_users[~df_agresso_users["AdresseEmail"].isin(df_n2f_users["mail"])].copy()

    if not users_to_create.empty:
        created_list: List[bool] = []
        for _, user in users_to_create.iterrows():
            payload = build_user_payload(
                user,
                df_agresso_users,
                df_n2f_users,
                df_n2f_companies,
                base_url,
                client_id,
                client_secret,
                simulate,
                sandbox
            )

            status = create_user_api(
                base_url,
                client_id,
                client_secret,
                payload,
                simulate
            )
            created_list.append(status)
        users_to_create[status_col] = created_list

    return users_to_create, status_col

def update_users(
    df_agresso_users: pd.DataFrame,
    df_n2f_users: pd.DataFrame,
    df_n2f_companies: pd.DataFrame,
    base_url: str,
    client_id: str,
    client_secret: str,
    status_col: str = "updated",
    simulate: bool = False,
    sandbox: bool = False
) -> Tuple[pd.DataFrame, str]:
    """
    Met à jour les utilisateurs présents dans les deux sources via l'API N2F,
    uniquement si les données diffèrent.
    Retourne un DataFrame avec une colonne 'updated' (booléen) indiquant le succès ou l'échec.
    """

    if df_agresso_users.empty or df_n2f_users.empty:
        return pd.DataFrame(), status_col

    users_to_update: List[Dict] = []
    updated_list: List[bool] = []

    # On indexe df_n2f par mail pour accès rapide
    n2f_by_mail = df_n2f_users.set_index("mail").to_dict(orient="index")

    for _, user in df_agresso_users[df_agresso_users["AdresseEmail"].isin(df_n2f_users["mail"])].iterrows():
        payload = build_user_payload(
            user,
            df_agresso_users,
            df_n2f_users,
            df_n2f_companies,
            base_url,
            client_id,
            client_secret,
            simulate,
            sandbox
        )

        mail = user["AdresseEmail"]
        n2f_user = n2f_by_mail.get(mail, {})

        # On compare les champs du payload avec ceux de N2F
        diff = False
        for key, value in payload.items():
            if key in n2f_user and n2f_user[key] != value:
                diff = True
                break
        if diff:
            status = update_user_api(
                base_url,
                client_id,
                client_secret,
                payload,
                simulate
            )
            updated_list.append(status)
            users_to_update.append(user.to_dict())
        # Sinon, on ne fait rien (pas de mise à jour)

    if users_to_update:
        df_result = pd.DataFrame(users_to_update)
        df_result[status_col] = updated_list
        return df_result, status_col
    else:
        return pd.DataFrame(), status_col

def delete_users(
    df_agresso_users: pd.DataFrame,
    df_n2f_users: pd.DataFrame,
    base_url: str,
    client_id: str,
    client_secret: str,
    status_col: str = "deleted",
    simulate: bool = False
) -> Tuple[pd.DataFrame, str]:
    """
    Supprime les utilisateurs présents dans N2F mais absents d'Agresso via l'API N2F.
    Retourne un tuple (DataFrame, nom_colonne_statut).
    """

    # Si N2F est vide, il n'y a rien à supprimer
    if df_n2f_users.empty:
        return pd.DataFrame(), status_col

    if df_agresso_users.empty:
        # Si Agresso est vide, tous les utilisateurs de N2F sont à supprimer
        users_to_delete = df_n2f_users.copy()
    else:
        # On supprime ceux qui ne sont pas dans Agresso
        users_to_delete = df_n2f_users[~df_n2f_users["mail"].isin(df_agresso_users["AdresseEmail"])].copy()

    if not users_to_delete.empty:
        # Suppression des utilisateurs via l'API N2F
        deleted_list: List[bool] = []
        for mail in users_to_delete["mail"]:
            deleted = delete_user_api(
                base_url,
                client_id,
                client_secret,
                mail,
                simulate
            )
            deleted_list.append(deleted)

        # Initialisation de la colonne de statut
        users_to_delete[status_col] = deleted_list

    return users_to_delete, status_col