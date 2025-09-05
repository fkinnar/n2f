"""
User API functions for N2F operations.
"""

from typing import Dict, List, Any
from n2f.api.base import retreive, upsert, delete


def get_users(
    base_url: str,
    client_id: str,
    client_secret: str,
    start: int = 0,
    limit: int = 200,
    simulate: bool = False,
) -> List[Dict[str, Any]]:
    """
    Récupère une page d'utilisateurs depuis l'API N2F.

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        start (int): Index de départ pour la pagination.
        limit (int): Nombre maximum d'utilisateurs à récupérer (max 200).
        simulate (bool): Si True, simule la récupération sans l'exécuter.

    Returns:
        List[Dict[str, Any]]: Liste de dictionnaires représentant les utilisateurs.

    Raises:
        Exception: En cas d'erreur HTTP ou de parsing.
    """

    response = retreive(
        "users", base_url, client_id, client_secret, start, limit, simulate
    )
    data = response[0]["response"] if response and len(response) > 0 else {}
    return data.get("data", [])


def create_user(
    base_url: str,
    client_id: str,
    client_secret: str,
    payload: Dict[str, Any],
    simulate: bool = False,
) -> bool:
    """
    Crée un utilisateur N2F via l'API.

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        payload (Dict[str, Any]): Données utilisateur à envoyer à l'API.
        simulate (bool): Si True, simule l'appel sans exécuter.

    Returns:
        bool: True si l'opération a réussi (code 200 ou 201), False sinon.
    """
    return upsert(base_url, "/users", client_id, client_secret, payload, simulate)


def update_user(
    base_url: str,
    client_id: str,
    client_secret: str,
    payload: Dict[str, Any],
    simulate: bool = False,
) -> bool:
    """
    Met à jour un utilisateur N2F via l'API.

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        payload (Dict[str, Any]): Données utilisateur à envoyer à l'API.
        simulate (bool): Si True, simule l'appel sans exécuter.

    Returns:
        bool: True si l'opération a réussi (code 200 ou 201), False sinon.
    """
    return upsert(base_url, "/users", client_id, client_secret, payload, simulate)


def delete_user(
    base_url: str, client_id: str, client_secret: str, mail: str, simulate: bool = False
) -> bool:
    """
    Supprime un utilisateur N2F via l'API.

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        mail (str): Adresse e-mail de l'utilisateur à supprimer.
        simulate (bool): Si True, simule la suppression sans l'exécuter.

    Returns:
        bool: True si la suppression a réussi (code 200-299), False sinon.
    """
    return delete(base_url, "/users", client_id, client_secret, mail, simulate)
