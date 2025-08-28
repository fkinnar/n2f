import pandas as pd

from n2f.api.userprofile import get_userprofiles as get_userprofiles_api
from helper.cache import get_from_cache, set_in_cache


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
        cached = get_from_cache("get_userprofiles", base_url, client_id, simulate)
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
        set_in_cache(result, "get_userprofiles", base_url, client_id, simulate)
    return result.copy(deep=True)
