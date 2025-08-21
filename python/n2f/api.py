import time
import requests
import pandas as pd
from datetime import datetime

from functools import wraps

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
    Retourne un tuple (token, validity).
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


def get_entity(entity: str, base_url: str, client_id: str, client_secret: str, start: int = 0, limit: int = 200, simulate: bool = False) -> pd.DataFrame:
    """
    Récupère n'importe quelles entités depuis l'API N2F (paginé).

    Args:
        entity (str): Type d'entité à récupérer (ex: "users", "companies").
        base_url (str): URL de base de l'API N2F.
        access_token (str): Jeton d'accès Bearer pour l'API N2F.
        start (int): Index de départ pour la pagination.
        limit (int): Nombre maximum d'utilisateurs à récupérer (max 200).

    Returns:
        pd.DataFrame: DataFrame contenant les utilisateurs récupérés.

    Raises:
        Exception: En cas d'erreur HTTP ou de parsing.
    """

    if simulate:
        return pd.DataFrame()

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

    data = response.json()
    users = data["response"]["data"]
    df = pd.DataFrame(users)
    return df


def get_users(base_url: str, client_id: str, client_secret: str, start: int = 0, limit: int = 200, simulate: bool = False) -> pd.DataFrame:
    """
    Récupère les utilisateurs depuis l'API N2F (paginé).

    Args:
        base_url (str): URL de base de l'API N2F.
        access_token (str): Jeton d'accès Bearer pour l'API N2F.
        start (int): Index de départ pour la pagination.
        limit (int): Nombre maximum d'utilisateurs à récupérer (max 200).

    Returns:
        pd.DataFrame: DataFrame contenant les utilisateurs récupérés.

    Raises:
        Exception: En cas d'erreur HTTP ou de parsing.
    """

    return get_entity("users", base_url, client_id, client_secret, start, limit, simulate)


def get_companies(base_url: str, client_id: str, client_secret: str, start: int = 0, limit: int = 200, simulate: bool = False) -> pd.DataFrame:
    """
    Récupère les entreprises depuis l'API N2F (paginé).

    Args:
        base_url (str): URL de base de l'API N2F.
        access_token (str): Jeton d'accès Bearer pour l'API N2F.
        start (int): Index de départ pour la pagination.
        limit (int): Nombre maximum d'utilisateurs à récupérer (max 200).

    Returns:
        pd.DataFrame: DataFrame contenant les utilisateurs récupérés.

    Raises:
        Exception: En cas d'erreur HTTP ou de parsing.
    """

    return get_entity("companies", base_url, client_id, client_secret, start, limit, simulate)


def delete_user(base_url: str, client_id: str, client_secret: str, mail: str, simulate: bool = False) -> bool:
    """
    Supprime un utilisateur N2F via l'API (DELETE /v2/users/{mail}).
    Retourne True si la suppression a réussi, False sinon.
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


def upsert_user(base_url: str, client_id: str, client_secret: str, payload: dict, simulate: bool = False) -> bool:
    """
    Crée ou met à jour un utilisateur N2F via l'API (POST /v2/users).
    Retourne True si l'opération a réussi (code 200 ou 201), False sinon.
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
    """
    return upsert_user(base_url, client_id, client_secret, payload, simulate)


def update_user(base_url: str, client_id: str, client_secret: str, payload: dict, simulate: bool = False) -> bool:
    """
    Met à jour un utilisateur N2F via l'API.
    """
    return upsert_user(base_url, client_id, client_secret, payload, simulate)
