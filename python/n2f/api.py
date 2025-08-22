import time
from datetime import datetime
from functools import wraps
from typing import Any, Dict, List

import n2f


def cache_token(timeout_seconds: int = n2f.TIMEOUT_TOKEN, safety_margin: int = n2f.SAFETY_MARGIN):
    def decorator(func):
        cache = {}
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            if (
                "token" in cache and
                "expires_at" in cache and
                cache["expires_at"] - safety_margin > now
            ):
                return cache["token"], cache["expires_at"]
            token, validity = func(*args, **kwargs)
            # validity est une date ISO, ex: '2025-08-20T09:54:35.8185075Z'
            expires_at = datetime.fromisoformat(validity.replace("Z", "+00:00")).timestamp()
            cache["token"] = token
            cache["expires_at"] = expires_at

            return token, expires_at

        return wrapper

    return decorator


@cache_token(timeout_seconds=3600)
def get_access_token(base_url: str, client_id: str, client_secret: str, simulate: bool = False) -> tuple[str, str]:
    """
    Récupère un token d'accès N2F via l'API d'authentification.

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        simulate (bool): Si True, simule la récupération sans l'exécuter.

    Returns:
        tuple[str, str]: Un tuple contenant le token d'accès et sa validité.

    Laisse lever une exception en cas d'erreur HTTP ou de parsing.
    """

    if simulate:
        return "", ""

    url = base_url + "/auth"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = n2f.get_session_write().post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    token = data["response"]["token"]
    validity = data["response"]["validity"]
    return token, validity


def get_entity(entity: str, base_url: str, client_id: str, client_secret: str, start: int = 0, limit: int = 200, simulate: bool = False) -> List[Dict[str, Any]]:
    """
    Récupère une page d'entités depuis l'API N2F (paginé).

    Args:
        entity (str): Type d'entité à récupérer (ex: "users", "companies").
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        start (int): Index de départ pour la pagination.
        limit (int): Nombre maximum d'entités à récupérer (max 200).
        simulate (bool): Si True, simule la récupération sans l'exécuter.

    Returns:
        dict: Réponse brute de l'API (incluant la clé "response" avec les données).

    Raises:
        Exception: En cas d'erreur HTTP ou de parsing.
    """

    if simulate:
        return []

    access_token, _ = get_access_token(base_url, client_id, client_secret, simulate=simulate)
    url = base_url + f"/{entity}"
    req_params = {
        "start": start,
        "limit": limit
    }
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = n2f.get_session_get().get(url, headers=headers, params=req_params)
    response.raise_for_status()  # Laisse planter en cas d'erreur HTTP

    return response.json()


def get_users(base_url: str, client_id: str, client_secret: str, start: int = 0, limit: int = 200, simulate: bool = False) -> List[Dict[str, Any]]:
    """
    Récupère une page d'utilisateurs depuis l'API N2F (paginé).

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        start (int): Index de départ pour la pagination.
        limit (int): Nombre maximum d'utilisateurs à récupérer (max 200).
        simulate (bool): Si True, simule la récupération sans l'exécuter.

    Returns:
        list[dict[str, Any]]: Liste de dictionnaires représentant les utilisateurs récupérés.

    Raises:
        Exception: En cas d'erreur HTTP ou de parsing.
    """

    response = get_entity("users", base_url, client_id, client_secret, start, limit, simulate)
    return response["response"]["data"]


def get_companies(base_url: str, client_id: str, client_secret: str, start: int = 0, limit: int = 200, simulate: bool = False) -> List[Dict[str, Any]]:
    """
    Récupère une page d'entreprises depuis l'API N2F (paginé).

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        start (int): Index de départ pour la pagination.
        limit (int): Nombre maximum d'entreprises à récupérer (max 200).
        simulate (bool): Si True, simule la récupération sans l'exécuter.

    Returns:
        list[dict[str, Any]]: Liste de dictionnaires représentant les entreprises récupérées.

    Raises:
        Exception: En cas d'erreur HTTP ou de parsing.
    """

    response = get_entity("companies", base_url, client_id, client_secret, start, limit, simulate)
    return response["response"]["data"]


def get_roles(base_url: str, client_id: str, client_secret: str, simulate: bool = False) -> List[Dict[str, Any]]:
    """
    Récupère les rôles depuis l'API N2F.

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        simulate (bool): Si True, simule la récupération sans l'exécuter.

    Returns:
        list[dict[str, Any]]: Liste de dictionnaires représentant les rôles récupérés.

    Raises:
        Exception: En cas d'erreur HTTP ou de parsing.
    """

    response = get_entity("roles", base_url, client_id, client_secret, simulate=simulate)
    return response["response"]


def get_userprofiles(base_url: str, client_id: str, client_secret: str, simulate: bool = False) -> List[Dict[str, Any]]:
    """
    Récupère les profils d'utilisateurs depuis l'API N2F.

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        simulate (bool): Si True, simule la récupération sans l'exécuter.

    Returns:
        list[dict[str, Any]]: Liste de dictionnaires représentant les profils récupérés.

    Raises:
        Exception: En cas d'erreur HTTP ou de parsing.
    """

    response = get_entity("userprofiles", base_url, client_id, client_secret, simulate=simulate)
    return response["response"]


def get_customaxes(
    base_url: str,
    client_id: str,
    client_secret: str,
    company_id: str,
    start: int,
    limit: int,
    simulate: bool = False
) -> List[Dict[str, Any]]:
    """
    Récupère une page d'axes personnalisés d'une société depuis l'API N2F.

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        company_id (str): UUID de la société.
        start (int): Index de départ pour la pagination.
        limit (int): Nombre maximum d'axes à récupérer (max 200).
        simulate (bool): Si True, simule la récupération sans l'exécuter.

    Returns:
        list[dict[str, Any]]: Liste de dictionnaires représentant les axes personnalisés.

    Raises:
        Exception: En cas d'erreur HTTP ou de parsing.
    """

    if simulate:
        return []

    access_token, _ = get_access_token(base_url, client_id, client_secret, simulate=simulate)
    url = f"{base_url}/companies/{company_id}/axes"
    params = {
        "start": start,
        "limit": limit
    }
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = n2f.get_session_get().get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    axes = data["response"]["data"]
    return axes


def get_customaxes_values(
    base_url: str,
    client_id: str,
    client_secret: str,
    company_id: str,
    axe_id: str,
    start: int,
    limit: int,
    simulate: bool = False
) -> List[Dict[str, Any]]:
    """
    Récupère une page de valeurs d'un axe personnalisé d'une société depuis l'API N2F.

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        company_id (str): UUID de la société.
        axe_id (str): UUID de l'axe personnalisé.
        start (int): Index de départ pour la pagination.
        limit (int): Nombre maximum de valeurs à récupérer (max 200).
        simulate (bool): Si True, simule la récupération sans l'exécuter.

    Returns:
        list[dict[str, Any]]: Liste de dictionnaires représentant les valeurs de l'axe personnalisé.

    Raises:
        Exception: En cas d'erreur HTTP ou de parsing.
    """

    if simulate:
        return []

    access_token, _ = get_access_token(base_url, client_id, client_secret, simulate=simulate)
    url = f"{base_url}/companies/{company_id}/axes/{axe_id}"
    params = {
        "start": start,
        "limit": limit
    }
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = n2f.get_session_get().get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    values = data["response"]["data"]
    return values


def upsert_user(base_url: str, client_id: str, client_secret: str, payload: dict, simulate: bool = False) -> bool:
    """
    Crée ou met à jour un utilisateur N2F via l'API (POST /v2/users).

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        payload (dict): Données utilisateur à envoyer à l'API.
        simulate (bool): Si True, simule l'appel sans exécuter.

    Returns:
        bool: True si l'opération a réussi (code 200 ou 201), False sinon.
    """

    if simulate:
        return False

    access_token, _ = get_access_token(base_url, client_id, client_secret, simulate=simulate)
    url = base_url + "/users"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = n2f.get_session_write().post(url, headers=headers, json=payload)
    return response.status_code >= 200 and response.status_code < 300


def create_user(base_url: str, client_id: str, client_secret: str, payload: dict, simulate: bool = False) -> bool:
    """
    Crée un utilisateur N2F via l'API.

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        payload (dict): Données utilisateur à envoyer à l'API.
        simulate (bool): Si True, simule l'appel sans exécuter.

    Returns:
        bool: True si l'opération a réussi (code 200 ou 201), False sinon.
    """
    return upsert_user(base_url, client_id, client_secret, payload, simulate)


def update_user(base_url: str, client_id: str, client_secret: str, payload: dict, simulate: bool = False) -> bool:
    """
    Met à jour un utilisateur N2F via l'API.

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        payload (dict): Données utilisateur à envoyer à l'API.
        simulate (bool): Si True, simule l'appel sans exécuter.

    Returns:
        bool: True si l'opération a réussi (code 200 ou 201), False sinon.
    """
    return upsert_user(base_url, client_id, client_secret, payload, simulate)


def delete_user(base_url: str, client_id: str, client_secret: str, mail: str, simulate: bool = False) -> bool:
    """
    Supprime un utilisateur N2F via l'API (DELETE /v2/users/{mail}).

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        mail (str): Adresse e-mail de l'utilisateur à supprimer.
        simulate (bool): Si True, simule la suppression sans l'exécuter.

    Returns:
        bool: True si la suppression a réussi, False sinon.
    """

    if simulate:
        return False

    access_token, _ = get_access_token(base_url, client_id, client_secret, simulate=simulate)
    url = base_url + f"/users/{mail}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = n2f.get_session_write().delete(url, headers=headers)
    return response.status_code >= 200 and response.status_code < 300