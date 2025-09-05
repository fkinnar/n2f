"""
Token management functions for N2F API authentication.
"""

import time
from datetime import datetime
from functools import wraps
from typing import Callable, Any, Tuple, Union, Dict
import n2f


def cache_token(
    timeout_seconds: int = n2f.TIMEOUT_TOKEN, safety_margin: int = n2f.SAFETY_MARGIN
) -> Callable[
    [Callable[..., Tuple[str, Union[str, float]]]],
    Callable[..., Tuple[str, Union[str, float]]],
]:
    def decorator(
        func: Callable[..., Tuple[str, Union[str, float]]],
    ) -> Callable[..., Tuple[str, Union[str, float]]]:
        cache: Dict[str, Union[str, float]] = {}

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Tuple[str, Union[str, float]]:
            now = time.time()
            if (
                "token" in cache
                and "expires_at" in cache
                and isinstance(cache["token"], str)
                and isinstance(cache["expires_at"], (int, float))
                and cache["expires_at"] - safety_margin > now
            ):
                return cache["token"], cache["expires_at"]
            token, validity = func(*args, **kwargs)

            # Si on est en mode simulation, validity peut être vide
            if not validity:  # Si validity est vide ou None
                return token, validity

            # validity est une date ISO, ex: '2025-08-20T09:54:35.8185075Z'
            if isinstance(validity, str):
                expires_at = datetime.fromisoformat(
                    validity.replace("Z", "+00:00")
                ).timestamp()
            else:
                expires_at = validity
            cache["token"] = token
            cache["expires_at"] = expires_at

            return token, expires_at

        return wrapper

    return decorator


@cache_token(timeout_seconds=3600)
def get_access_token(
    base_url: str, client_id: str, client_secret: str, simulate: bool = False
) -> Tuple[str, str]:
    """
    Récupère un token d'accès N2F via l'API d'authentification.

    Args:
        base_url (str): URL de base de l'API N2F.
        client_id (str): ID du client pour l'API N2F.
        client_secret (str): Secret du client pour l'API N2F.
        simulate (bool): Si True, simule la récupération sans l'exécuter.

    Returns:
        Tuple[str, str]: Un tuple contenant le token d'accès et sa validité.

    Laisse lever une exception en cas d'erreur HTTP ou de parsing.
    """

    if simulate:
        return "", ""

    url = base_url + "/auth"
    payload = {"client_id": client_id, "client_secret": client_secret}
    headers = {"Content-Type": "application/json"}

    response = n2f.get_session_write().post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    token = data["response"]["token"]
    validity = data["response"]["validity"]
    return token, validity
