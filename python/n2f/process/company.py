import pandas as pd
from typing import List

from n2f.api.company import get_companies as get_companies_api
from core import get_from_cache, set_in_cache


def get_companies(
        base_url: str,
        client_id: str,
        client_secret: str,
        simulate: bool = False,
        cache: bool = True
    ) -> pd.DataFrame:
    """
    Récupère toutes les entreprises depuis l'API N2F (toutes les pages) et retourne un DataFrame unique.
    Respecte le quota d'appels à l'API (en secondes entre chaque appel).
    La pagination est gérée automatiquement.
    """

    if cache:
        cached = get_from_cache("get_companies", base_url, client_id, simulate)
        if cached is not None:
            return cached

    all_companies: List[pd.DataFrame] = []
    start = 0
    limit = 200

    while True:
        companies_page = get_companies_api(
            base_url,
            client_id,
            client_secret,
            start,
            limit,
            simulate
        )
        if not companies_page:
            break
        df_page = pd.DataFrame(companies_page)
        if df_page.empty:
            break
        all_companies.append(df_page)
        if len(df_page) < limit:
            break
        start += limit

    if all_companies:
        result = pd.concat(all_companies, ignore_index=True)
    else:
        result = pd.DataFrame()

    if cache:
        set_in_cache(result, "get_companies", base_url, client_id, simulate)
    return result.copy(deep=True)
