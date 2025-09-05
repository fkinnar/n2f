"""
Project API functions for N2F operations.
"""

from typing import Any, List, Dict
from n2f.api.base import upsert, delete
from n2f.api.customaxe import get_customaxes_values


def get_projects(
    base_url: str,
    client_id: str,
    client_secret: str,
    company_id: str,
    start: int,
    limit: int,
    simulate: bool = False,
) -> List[Dict[str, Any]]:
    """
    Récupère une page de projets d'une société depuis l'API N2F.

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        company_id (str): UUID de la société.
        start (int): Index de départ pour la pagination.
        limit (int): Nombre maximum de projets à récupérer (max 200).
        simulate (bool): Si True, simule la récupération sans l'exécuter.

    Returns:
        List[Dict[str, Any]]: Liste de dictionnaires représentant les projets.

    Raises:
        Exception: En cas d'erreur HTTP ou de parsing.
    """
    return get_customaxes_values(
        base_url,
        client_id,
        client_secret,
        company_id,
        "projects",
        start,
        limit,
        simulate,
    )


def create_project(
    base_url: str,
    client_id: str,
    client_secret: str,
    company_id: str,
    payload: Dict[str, Any],
    simulate: bool = False,
) -> bool:
    """
    Crée un projet N2F via l'API.

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        company_id (str): UUID de la société.
        payload (Dict[str, Any]): Données du projet à envoyer à l'API.
        simulate (bool): Si True, simule l'appel sans l'exécuter.

    Returns:
        bool: True si l'opération a réussi (code 200 ou 201), False sinon.
    """
    endpoint = f"/companies/{company_id}/axes/projects"
    return upsert(base_url, endpoint, client_id, client_secret, payload, simulate)


def update_project(
    base_url: str,
    client_id: str,
    client_secret: str,
    company_id: str,
    payload: Dict[str, Any],
    simulate: bool = False,
) -> bool:
    """
    Met à jour un projet N2F via l'API.

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        company_id (str): UUID de la société.
        payload (Dict[str, Any]): Données du projet à envoyer à l'API.
        simulate (bool): Si True, simule l'appel sans l'exécuter.

    Returns:
        bool: True si l'opération a réussi (code 200 ou 201), False sinon.
    """
    endpoint = f"/companies/{company_id}/axes/projects"
    return upsert(base_url, endpoint, client_id, client_secret, payload, simulate)


def delete_project(
    base_url: str,
    client_id: str,
    client_secret: str,
    company_id: str,
    code: str,
    simulate: bool = False,
) -> bool:
    """
    Supprime un projet N2F via l'API.

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        company_id (str): UUID de la société.
        code (str): Code du projet à supprimer.
        simulate (bool): Si True, simule la suppression sans l'exécuter.

    Returns:
        bool: True si la suppression a réussi (code 200-299), False sinon.
    """
    endpoint = f"/companies/{company_id}/axes/projects/"
    return delete(base_url, endpoint, client_id, client_secret, code, simulate)
