"""
Company processing functions for N2F synchronization.
"""

import pandas as pd
from core.cache import cache_get, cache_set  # noqa: F401
from n2f.client import N2fApiClient


def get_companies(n2f_client: N2fApiClient) -> pd.DataFrame:
    """Récupère les entreprises via le client N2F."""
    return n2f_client.get_companies()


def lookup_company_id(
    company_code: str,
    df_n2f_companies: pd.DataFrame,
    sandbox: bool = False,
) -> str:
    """Recherche l'UUID d'une entreprise à partir de son code."""
    if df_n2f_companies.empty:
        return ""
    match = df_n2f_companies.loc[df_n2f_companies["code"] == company_code, "uuid"]
    if not match.empty:
        return match.iloc[0]
    if sandbox and not df_n2f_companies.empty and "uuid" in df_n2f_companies.columns:
        return df_n2f_companies["uuid"].iloc[0]
    return ""
