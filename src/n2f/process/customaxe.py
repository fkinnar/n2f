"""
Custom axe processing functions for N2F synchronization.
"""

import pandas as pd
from typing import Dict, Any, Tuple
from core.cache import cache_get, cache_set  # noqa: F401
from n2f.client import N2fApiClient
from n2f.payload import create_project_upsert_payload
from n2f.api_result import ApiResult


def get_customaxes(n2f_client: N2fApiClient, company_id: str) -> pd.DataFrame:
    """Récupère les axes personnalisés via le client N2F."""
    return n2f_client.get_custom_axes(company_id)


def get_customaxe_values(
    n2f_client: N2fApiClient, company_id: str, axe_id: str
) -> pd.DataFrame:
    """Récupère les valeurs d'un axe personnalisé via le client N2F."""
    return n2f_client.get_axe_values(company_id, axe_id)


def upsert_customaxe_value(
    n2f_client: N2fApiClient, company_id: str, axe_id: str, payload: Dict[str, Any]
) -> ApiResult:
    """Crée ou met à jour une valeur d'axe personnalisé via le client N2F."""
    return n2f_client.upsert_axe_value(company_id, axe_id, payload)


def delete_customaxe_value(
    n2f_client: N2fApiClient, company_id: str, axe_id: str, value_code: str
) -> ApiResult:
    """Supprime une valeur d'axe personnalisé via le client N2F."""
    return n2f_client.delete_axe_value(company_id, axe_id, value_code)


def build_customaxe_payload(customaxe: pd.Series, sandbox: bool) -> Dict[str, Any]:
    """Construit le payload pour l'upsert d'un axe personnalisé."""
    return create_project_upsert_payload(customaxe.to_dict(), sandbox)


def create_customaxes(
    n2f_client: N2fApiClient,
    axe_id: str,
    df_agresso_customaxes: pd.DataFrame,
    df_n2f_customaxes: pd.DataFrame,
    df_n2f_companies: pd.DataFrame,
    sandbox: bool,
    status_col: str = "created",
) -> Tuple[pd.DataFrame, str]:
    """Crée les valeurs d'un axe personnalisé via le client N2F."""
    # Implémentation similaire à create_axes dans n2f/process/axe.py
    # Nécessite lookup_company_id et gestion des erreurs
    pass


def update_customaxes(
    n2f_client: N2fApiClient,
    axe_id: str,
    df_agresso_customaxes: pd.DataFrame,
    df_n2f_customaxes: pd.DataFrame,
    df_n2f_companies: pd.DataFrame,
    sandbox: bool,
    status_col: str = "updated",
) -> Tuple[pd.DataFrame, str]:
    """Met à jour les valeurs d'un axe personnalisé via le client N2F."""
    # Implémentation similaire à update_axes dans n2f/process/axe.py
    pass


def delete_customaxes(
    n2f_client: N2fApiClient,
    axe_id: str,
    df_agresso_customaxes: pd.DataFrame,
    df_n2f_customaxes: pd.DataFrame,
    df_n2f_companies: pd.DataFrame,
    sandbox: bool,
    status_col: str = "deleted",
) -> Tuple[pd.DataFrame, str]:
    """Supprime les valeurs d'un axe personnalisé via le client N2F."""
    # Implémentation similaire à delete_axes dans n2f/process/axe.py
    pass
