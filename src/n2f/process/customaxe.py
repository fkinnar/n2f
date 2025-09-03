import pandas as pd
from typing import List

from n2f.api.customaxe import (
    get_customaxes as get_customaxes_api,
    get_customaxes_values as get_customaxes_values_api
)
from core import cache_get, cache_set


def get_customaxes(
    base_url: str,
    client_id: str,
    client_secret: str,
    company_id: str,
    simulate: bool = False,
    cache: bool = True
) -> pd.DataFrame:
    """
    Récupère les axes personnalisés d'une société depuis l'API N2F (toutes les pages) et retourne un DataFrame unique.
    La pagination est gérée automatiquement.
    """
    if cache:
        cached = cache_get("get_customaxes", base_url, client_id, company_id, simulate)
        if cached is not None:
            return cached

    all_axes: List[pd.DataFrame] = []
    start = 0
    limit = 200

    while True:
        axes_page = get_customaxes_api(
            base_url,
            client_id,
            client_secret,
            company_id,
            start,
            limit,
            simulate
        )
        if not axes_page:
            break
        df_page = pd.DataFrame(axes_page)
        if df_page.empty:
            break
        all_axes.append(df_page)
        if len(df_page) < limit:
            break
        start += limit

    if all_axes:
        result = pd.concat(all_axes, ignore_index=True)
    else:
        result = pd.DataFrame()

    if cache:
        cache_set(result, "get_customaxes", base_url, client_id, company_id, simulate)
    return result.copy(deep=True)


def get_customaxes_values(
    base_url: str,
    client_id: str,
    client_secret: str,
    company_id: str,
    axe_id: str,
    simulate: bool = False,
    cache: bool = True
) -> pd.DataFrame:
    """
    Récupère les valeurs d'un axe personnalisé d'une société depuis l'API N2F (toutes les pages) et retourne un DataFrame unique.
    La pagination est gérée automatiquement.
    """
    if cache:
        cached = cache_get("get_customaxes_values", base_url, client_id, company_id, axe_id, simulate)
        if cached is not None:
            return cached

    all_values: List[pd.DataFrame] = []
    start = 0
    limit = 200

    while True:
        values_page = get_customaxes_values_api(
            base_url,
            client_id,
            client_secret,
            company_id,
            axe_id,
            start,
            limit,
            simulate
        )
        if not values_page:
            break
        df_page = pd.DataFrame(values_page)
        if df_page.empty:
            break
        all_values.append(df_page)
        if len(df_page) < limit:
            break
        start += limit

    if all_values:
        result = pd.concat(all_values, ignore_index=True)
    else:
        result = pd.DataFrame()

    if cache:
        cache_set(result, "get_customaxes_values", base_url, client_id, company_id, axe_id, simulate)
    return result.copy(deep=True)
