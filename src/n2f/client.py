import logging
import pandas as pd
import time
import requests
from typing import List, Any, Dict, Optional

import n2f
from core import SyncContext, cache_get, cache_set
from n2f.api.token import get_access_token
from n2f.api_result import ApiResult


class N2fApiClient:
    """
    Client API pour interagir avec l'API N2F.

    Ce client gère l'authentification, les appels API, la pagination,
    le cache et la gestion d'erreur pour toutes les opérations N2F.

    Features principales :
    - Authentification automatique avec gestion des tokens
    - Pagination automatique pour les gros volumes de données
    - Cache intelligent pour optimiser les performances
    - Gestion d'erreur robuste avec retry automatique
    - Support du mode simulation pour les tests

    Example:
        >>> context = SyncContext(...)
        >>> client = N2fApiClient(context)
        >>> users = client.get_users()
        >>> result = client.create_user(user_payload)
    """

    def __init__(self, context: SyncContext) -> None:
        """
        Initialise le client avec le contexte de synchronisation.

        Args:
            context: Contexte contenant la configuration et les credentials

        Raises:
            ConfigurationException: Si la configuration est invalide
            AuthenticationException: Si les credentials sont manquants
        """
        self.context = context
        # Utilise la méthode get_config_value pour supporter l'ancien et le nouveau
        # format
        n2f_config = context.get_config_value("n2f")
        self.base_url = (
            n2f_config.base_urls
            if hasattr(n2f_config, "base_urls")
            else n2f_config["base_urls"]
        )
        self.client_id = context.client_id
        self.client_secret = context.client_secret
        self.simulate = (
            n2f_config.simulate
            if hasattr(n2f_config, "simulate")
            else n2f_config["simulate"]
        )
        self._access_token: Optional[str] = None

    def _get_token(self) -> str:
        """
        Récupère et met en cache le token d'accès.

        Cette méthode gère l'authentification avec l'API N2F en utilisant
        le client_id et client_secret. Le token est mis en cache pour
        éviter les appels d'authentification répétés.

        Returns:
            str: Token d'accès valide

        Raises:
            AuthenticationException: Si l'authentification échoue
            NetworkException: Si la connexion réseau échoue
        """
        if self._access_token is None:
            token, _ = get_access_token(
                self.base_url,
                self.client_id,
                self.client_secret,
                simulate=self.simulate,
            )
            self._access_token = token
        return self._access_token

    def _request(
        self, entity: str, start: int = 0, limit: int = 200
    ) -> List[Dict[str, Any]]:
        """
        Effectue une requête GET paginée à l'API N2F.

        Cette méthode gère les appels API GET avec pagination automatique.
        Elle inclut l'authentification, la gestion d'erreur et le support
        du mode simulation.

        Args:
            entity: Nom de l'entité à récupérer (ex: 'users', 'companies')
            start: Index de départ pour la pagination (défaut: 0)
            limit: Nombre maximum d'éléments par page (défaut: 200)

        Returns:
            List[Dict[str, Any]]: Liste des entités récupérées

        Raises:
            ApiException: Si l'appel API échoue
            NetworkException: Si la connexion réseau échoue
        """
        if self.simulate:
            return []

        access_token = self._get_token()
        url = f"{self.base_url}/{entity}"
        params = {"start": start, "limit": limit}
        headers = {"Authorization": f"Bearer {access_token}"}

        logging.info(f"Requesting entity '{entity}' with start={start}, limit={limit}")
        response = n2f.get_session_get().get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()["response"]
        logging.info(
            f"Successfully retrieved {len(data.get('data', []))} "
            f"items for entity '{entity}'"
        )
        return data.get("data", [])

    def get_companies(self, use_cache: bool = True) -> pd.DataFrame:
        """
        Récupère toutes les entreprises (gère la pagination et le cache).
        """
        cache_key_args = (self.base_url, self.client_id, self.simulate)
        if use_cache:
            cached = cache_get("get_companies", *cache_key_args)
            if cached is not None:
                return cached

        all_companies_list = []
        start, limit = 0, 200
        while True:
            companies_page = self._request("companies", start, limit)
            if not companies_page:
                break

            df_page = pd.DataFrame(companies_page)
            all_companies_list.append(df_page)

            if len(df_page) < limit:
                break
            start += limit

        result = (
            pd.concat(all_companies_list, ignore_index=True)
            if all_companies_list
            else pd.DataFrame()
        )

        if use_cache:
            cache_set(result, "get_companies", *cache_key_args)

        return result.copy(deep=True)

    def get_roles(self, use_cache: bool = True) -> pd.DataFrame:
        """Récupère les rôles et les met en cache."""
        cache_key_args = (self.base_url, self.client_id, self.simulate)
        if use_cache:
            cached = cache_get("get_roles", *cache_key_args)
            if cached is not None:
                return cached

        # L'endpoint "roles" ne semble pas paginé et a une structure différente
        if self.simulate:
            return pd.DataFrame()

        access_token = self._get_token()
        url = f"{self.base_url}/roles"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = n2f.get_session_get().get(url, headers=headers)
        response.raise_for_status()

        # La réponse pour les rôles est directement la liste
        roles_data = response.json()["response"]
        result = pd.DataFrame(roles_data)

        if use_cache:
            cache_set(result, "get_roles", *cache_key_args)

        return result.copy(deep=True)

    def get_userprofiles(self, use_cache: bool = True) -> pd.DataFrame:
        """Récupère les profils utilisateurs et les met en cache."""
        cache_key_args = (self.base_url, self.client_id, self.simulate)
        if use_cache:
            cached = cache_get("get_userprofiles", *cache_key_args)
            if cached is not None:
                return cached

        # L'endpoint "userprofiles" a la même structure de réponse que "roles"
        if self.simulate:
            return pd.DataFrame()

        access_token = self._get_token()
        url = f"{self.base_url}/userprofiles"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = n2f.get_session_get().get(url, headers=headers)
        response.raise_for_status()

        profiles_data = response.json()["response"]
        result = pd.DataFrame(profiles_data)

        if use_cache:
            cache_set(result, "get_userprofiles", *cache_key_args)

        return result.copy(deep=True)

    def get_users(self, use_cache: bool = True) -> pd.DataFrame:
        """Récupère tous les utilisateurs (gère la pagination et le cache)."""
        cache_key_args = (self.base_url, self.client_id, self.simulate)
        if use_cache:
            cached = cache_get("get_users", *cache_key_args)
            if cached is not None:
                return cached

        all_users_list = []
        start, limit = 0, 200
        while True:
            users_page = self._request("users", start, limit)
            if not users_page:
                break

            df_page = pd.DataFrame(users_page)
            all_users_list.append(df_page)

            if len(df_page) < limit:
                break
            start += limit

        result = (
            pd.concat(all_users_list, ignore_index=True)
            if all_users_list
            else pd.DataFrame()
        )

        if use_cache:
            cache_set(result, "get_users", *cache_key_args)

        return result.copy(deep=True)

    def _upsert(
        self,
        endpoint: str,
        payload: dict,
        action_type: str = "upsert",
        object_type: Optional[str] = None,
        object_id: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> ApiResult:
        """Effectue un appel POST pour créer ou mettre à jour un objet."""
        logging.info(
            f"[{scope or 'Generic'}] {action_type.upper()} call to endpoint "
            f"'{endpoint}' for object '{object_id}'"
        )
        if self.simulate:
            logging.info(
                f"SIMULATE: [{scope or 'Generic'}] {action_type.upper()} for object "
                f"'{object_id}' was successful."
            )
            return ApiResult.simulate_result(
                "upsert", action_type, object_type, object_id, scope
            )

        start_time = time.time()
        try:
            access_token = self._get_token()
            url = f"{self.base_url}{endpoint}"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            response = n2f.get_session_write().post(url, headers=headers, json=payload)
            duration_ms = (time.time() - start_time) * 1000

            if 200 <= response.status_code < 300:
                logging.info(
                    f"[{scope or 'Generic'}] {action_type.upper()} for object "
                    f"'{object_id}' was successful (Status: {response.status_code})."
                )
                return ApiResult.success_result(
                    message=f"Upsert successful: {response.status_code}",
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    response_data=response.json() if response.content else None,
                    action_type=action_type,
                    object_type=object_type,
                    object_id=object_id,
                    scope=scope,
                )
            else:
                logging.error(
                    f"[{scope or 'Generic'}] {action_type.upper()} for object "
                    f"'{object_id}' failed (Status: {response.status_code}). "
                    f"Response: {response.text}"
                )
                return ApiResult.error_result(
                    message=f"Upsert failed: {response.status_code}",
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    error_details=response.text,
                    action_type=action_type,
                    object_type=object_type,
                    object_id=object_id,
                    scope=scope,
                )
        except requests.exceptions.RequestException as e:
            duration_ms = (time.time() - start_time) * 1000
            logging.error(
                f"[{scope or 'Generic'}] Network exception during "
                f"{action_type.upper()} for object '{object_id}'.",
                exc_info=True,
            )
            return ApiResult.error_result(
                message=f"Upsert network exception: {str(e)}",
                duration_ms=duration_ms,
                error_details=str(e),
                action_type=action_type,
                object_type=object_type,
                object_id=object_id,
                scope=scope,
            )

    def _delete(
        self,
        endpoint: str,
        object_id: str,
        action_type: str = "delete",
        object_type: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> ApiResult:
        """Effectue un appel DELETE pour supprimer un objet."""
        logging.info(
            f"[{scope or 'Generic'}] DELETE call to endpoint '{endpoint}' for object "
            f"'{object_id}'"
        )
        if self.simulate:
            logging.info(
                f"SIMULATE: [{scope or 'Generic'}] DELETE for object '{object_id}' "
                f"was successful."
            )
            return ApiResult.simulate_result(
                "delete", action_type, object_type, object_id, scope
            )

        start_time = time.time()
        try:
            access_token = self._get_token()
            url = f"{self.base_url}{endpoint}/{object_id}"
            headers = {"Authorization": f"Bearer {access_token}"}

            response = n2f.get_session_write().delete(url, headers=headers)
            duration_ms = (time.time() - start_time) * 1000

            if 200 <= response.status_code < 300:
                logging.info(
                    f"[{scope or 'Generic'}] DELETE for object '{object_id}' was "
                    f"successful (Status: {response.status_code})."
                )
                return ApiResult.success_result(
                    message=f"Delete successful: {response.status_code}",
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    action_type=action_type,
                    object_type=object_type,
                    object_id=object_id,
                    scope=scope,
                )
            else:
                logging.error(
                    f"[{scope or 'Generic'}] DELETE for object '{object_id}' failed "
                    f"(Status: {response.status_code}). Response: {response.text}"
                )
                return ApiResult.error_result(
                    message=f"Delete failed: {response.status_code}",
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    error_details=response.text,
                    action_type=action_type,
                    object_type=object_type,
                    object_id=object_id,
                    scope=scope,
                )
        except requests.exceptions.RequestException as e:
            duration_ms = (time.time() - start_time) * 1000
            logging.error(
                f"[{scope or 'Generic'}] Network exception during DELETE for object "
                f"'{object_id}'.",
                exc_info=True,
            )
            return ApiResult.error_result(
                message=f"Delete network exception: {str(e)}",
                duration_ms=duration_ms,
                error_details=str(e),
                action_type=action_type,
                object_type=object_type,
                object_id=object_id,
                scope=scope,
            )

    def create_user(self, payload: Dict[str, Any]) -> ApiResult:
        """Crée un utilisateur."""
        user_email = payload.get("mail", "unknown")
        return self._upsert("/users", payload, "create", "user", user_email, "users")

    def update_user(self, payload: Dict[str, Any]) -> ApiResult:
        """Met à jour un utilisateur."""
        user_email = payload.get("mail", "unknown")
        return self._upsert("/users", payload, "update", "user", user_email, "users")

    def delete_user(self, user_email: str) -> ApiResult:
        """Supprime un utilisateur par son email."""
        return self._delete("/users", user_email, "delete", "user", user_email, "users")

    def get_custom_axes(self, company_id: str, use_cache: bool = True) -> pd.DataFrame:
        """Récupère les axes personnalisés pour une société."""
        cache_key_args = (self.base_url, self.client_id, company_id, self.simulate)
        if use_cache:
            cached = cache_get(f"get_custom_axes_{company_id}", *cache_key_args)
            if cached is not None:
                return cached

        # Cet endpoint n'est pas paginé dans l'implémentation de référence
        endpoint = f"companies/{company_id}/axes"
        if self.simulate:
            axes_data: List[Dict[str, Any]] = []
        else:
            access_token = self._get_token()
            url = f"{self.base_url}/{endpoint}"
            headers = {"Authorization": f"Bearer {access_token}"}
            response = n2f.get_session_get().get(url, headers=headers)
            response.raise_for_status()
            axes_data = response.json().get("response", {}).get("data", [])

        result = pd.DataFrame(axes_data)

        if use_cache:
            cache_set(result, f"get_custom_axes_{company_id}", *cache_key_args)

        return result.copy(deep=True)

    def get_axe_values(
        self, company_id: str, axe_id: str, use_cache: bool = True
    ) -> pd.DataFrame:
        """Récupère les valeurs d'un axe pour une société (gère pagination et cache)."""
        cache_key_args = (
            self.base_url,
            self.client_id,
            company_id,
            axe_id,
            self.simulate,
        )
        if use_cache:
            cached = cache_get(f"get_axe_values_{axe_id}", *cache_key_args)
            if cached is not None:
                return cached

        all_values_list: List[pd.DataFrame] = []
        start, limit = 0, 200
        endpoint = f"companies/{company_id}/axes/{axe_id}"
        while True:
            # La méthode _request est pour les endpoints globaux, l'URL est spécifique
            if self.simulate:
                values_page: List[Dict[str, Any]] = []
            else:
                access_token = self._get_token()
                url = f"{self.base_url}/{endpoint}"
                params = {"start": start, "limit": limit}
                headers = {"Authorization": f"Bearer {access_token}"}
                response = n2f.get_session_get().get(
                    url, headers=headers, params=params
                )
                response.raise_for_status()
                values_page = response.json().get("response", {}).get("data", [])

            if not values_page:
                break

            df_page = pd.DataFrame(values_page)
            all_values_list.append(df_page)

            if len(df_page) < limit:
                break
            start += limit

        result = (
            pd.concat(all_values_list, ignore_index=True)
            if all_values_list
            else pd.DataFrame()
        )

        if use_cache:
            cache_set(result, f"get_axe_values_{axe_id}", *cache_key_args)

        return result.copy(deep=True)

    def upsert_axe_value(
        self,
        company_id: str,
        axe_id: str,
        payload: Dict[str, Any],
        action_type: str = "upsert",
        scope: Optional[str] = None,
    ) -> ApiResult:
        """Crée ou met à jour une valeur d'axe pour une société."""
        endpoint = f"/companies/{company_id}/axes/{axe_id}"
        object_code = payload.get("code", "unknown")
        return self._upsert(endpoint, payload, action_type, "axe", object_code, scope)

    def delete_axe_value(
        self, company_id: str, axe_id: str, value_code: str, scope: Optional[str] = None
    ) -> ApiResult:
        """Supprime une valeur d'axe pour une société par son code."""
        endpoint = f"/companies/{company_id}/axes/{value_code}"
        return self._delete(endpoint, value_code, "delete", "axe", value_code, scope)
