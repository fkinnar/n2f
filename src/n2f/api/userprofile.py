"""
User profile API functions for N2F operations.
"""

from typing import Dict, List, Any
from n2f.api.base import retreive


def get_userprofiles(
    base_url: str, client_id: str, client_secret: str, simulate: bool = False
) -> List[Dict[str, Any]]:
    """
    Récupère les profils d'utilisateurs depuis l'API N2F.

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        simulate (bool): Si True, simule la récupération sans l'exécuter.

    Returns:
        List[Dict[str, Any]]: Liste de dictionnaires représentant les profils récupérés.

    Raises:
        Exception: En cas d'erreur HTTP ou de parsing.
    """

    response = retreive(
        "userprofiles", base_url, client_id, client_secret, simulate=simulate
    )
    data = response[0]["response"] if response and len(response) > 0 else []
    return data  # pas de data dans response ici !
