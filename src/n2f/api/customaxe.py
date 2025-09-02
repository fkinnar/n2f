from typing import Any, List, Dict
from n2f.api.token import get_access_token
import n2f


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

    values = data["response"]["data"] if "data" in data["response"] else []
    return values


