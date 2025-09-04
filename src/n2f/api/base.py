from typing import Dict, List, Any
from n2f.api.token import get_access_token
import n2f


def retreive(
    entity: str,
    base_url: str,
    client_id: str,
    client_secret: str,
    start: int = 0,
    limit: int = 200,
    simulate: bool = False,
) -> List[Dict[str, Any]]:
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
        List[Dict[str,
     Any]]: Réponse brute de l'API (incluant la clé "response" avec les données).

    Raises:
        Exception: En cas d'erreur HTTP ou de parsing.
    """

    if simulate:
        return []

    access_token, _ = get_access_token(
        base_url, client_id, client_secret, simulate=simulate
    )
    url = base_url + f"/{entity}"
    req_params = {"start": start, "limit": limit}
    headers = {"Authorization": f"Bearer {access_token}"}

    response = n2f.get_session_get().get(url, headers=headers, params=req_params)
    response.raise_for_status()  # Laisse planter en cas d'erreur HTTP

    return response.json()


def upsert(
    base_url: str,
    endpoint: str,
    client_id: str,
    client_secret: str,
    payload: Dict[str, Any],
    simulate: bool = False,
) -> bool:
    """
    Crée ou met à jour un objet N2F via l'API (POST sur l'endpoint donné).

    Args:
        base_url (str): URL de base de l'API N2F.
        endpoint (str): Point de terminaison de l'API (ex: "/users").
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        payload (Dict[str, Any]): Données à envoyer à l'API.
        simulate (bool): Si True, simule l'appel sans l'exécuter.

    Returns:
        bool: True si l'opération a réussi (code 200 ou 201), False sinon.
    """

    if simulate:
        return False

    access_token, _ = get_access_token(
        base_url, client_id, client_secret, simulate=simulate
    )
    url = base_url + endpoint
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = n2f.get_session_write().post(url, headers=headers, json=payload)
    return response.status_code >= 200 and response.status_code < 300


def delete(
    base_url: str,
    endpoint: str,
    client_id: str,
    client_secret: str,
    id: str,
    simulate: bool = False,
) -> bool:
    """
    Supprime un objet N2F via l'API (DELETE sur l'endpoint donné avec identifiant).

    Args:
        base_url (str): URL de base de l'API N2F.
        endpoint (str): Point de terminaison de l'API (ex: "/users").
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        id (str): Identifiant de l'objet à supprimer (ex: adresse e -
    mail pour un utilisateur).
        simulate (bool): Si True, simule la suppression sans l'exécuter.

    Returns:
        bool: True si la suppression a réussi (code 200 - 299), False sinon.
    """

    if simulate:
        return False

    access_token, _ = get_access_token(
        base_url, client_id, client_secret, simulate=simulate
    )
    url = base_url + f"/{endpoint}/{id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = n2f.get_session_write().delete(url, headers=headers)
    return response.status_code >= 200 and response.status_code < 300
