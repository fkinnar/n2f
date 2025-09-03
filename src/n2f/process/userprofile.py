import pandas as pd

from n2f.api.userprofile import get_userprofiles as get_userprofiles_api
from core import cache_get, cache_set


def get_userprofiles(
    base_url: str,
    client_id: str,
    client_secret: str,
    simulate: bool = False,
    cache: bool = True
) -> pd.DataFrame:
    """
    Récupère les profils d'utilisateurs depuis l'API N2F et retourne un DataFrame.
    """
    if cache:
        cached = cache_get("get_userprofiles", base_url, client_id, simulate)
        if cached is not None:
            return cached

    profiles = get_userprofiles_api(
        base_url,
        client_id,
        client_secret,
        simulate
    )
    result = pd.DataFrame(profiles)
    if cache:
        cache_set(result, "get_userprofiles", base_url, client_id, simulate)
    return result.copy(deep=True)
