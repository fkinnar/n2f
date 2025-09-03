import pandas as pd

from n2f.api.role import get_roles as get_roles_api
from core import cache_get, cache_set


def get_roles(
    base_url: str,
    client_id: str,
    client_secret: str,
    simulate: bool = False,
    cache: bool = True
) -> pd.DataFrame:
    """
    Récupère les rôles depuis l'API N2F et retourne un DataFrame.
    """
    if cache:
        cached = cache_get("get_roles", base_url, client_id, simulate)
        if cached is not None:
            return cached

    roles = get_roles_api(
        base_url,
        client_id,
        client_secret,
        simulate
    )
    result = pd.DataFrame(roles)
    if cache:
        cache_set(result, "get_roles", base_url, client_id, simulate)
    return result.copy(deep=True)
