import time
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

            # Si on est en mode simulation, validity peut être vide
            if not validity:  # Si validity est vide ou None
                return token, validity

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
