"""
Role processing functions for N2F synchronization.
"""

import pandas as pd
from core.cache import cache_get, cache_set  # noqa: F401
from n2f.client import N2fApiClient


def get_roles(n2f_client: N2fApiClient) -> pd.DataFrame:
    """Récupère les rôles via le client N2F."""
    return n2f_client.get_roles()
