from typing import Dict, List, Any
from n2f.api.base import retreive

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

    response = retreive("companies", base_url, client_id, client_secret, start, limit, simulate)
    data = response["response"]
    return data["data"] if "data" in data else []
