from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any
import pandas as pd
from n2f.client import N2fApiClient
from n2f.api_result import ApiResult
from business.process.helper import log_error, has_payload_changes
from n2f.process.helper import add_api_logging_columns


class EntitySynchronizer(ABC):
    """
    Classe abstraite pour la synchronisation d'entités entre Agresso et N2F.

    Cette classe extrait le pattern commun de synchronisation (CREATE, UPDATE, DELETE)
    utilisé dans user.py et axe.py pour éliminer la duplication de code.
    """

    def __init__(self, n2f_client: N2fApiClient, sandbox: bool, scope: str):
        """
        Initialise le synchroniseur.

        Args:
            n2f_client: Client API N2F
            sandbox: Mode sandbox ou production
            scope: Scope de synchronisation (ex: "users", "projects")
        """
        self.n2f_client = n2f_client
        self.sandbox = sandbox
        self.scope = scope

    def create_entities(
        self,
        df_agresso: pd.DataFrame,
        df_n2f: pd.DataFrame,
        df_n2f_companies: pd.DataFrame = None,
        status_col: str = "created"
    ) -> Tuple[pd.DataFrame, str]:
        """
        Crée les nouvelles entités dans N2F.

        Args:
            df_agresso: DataFrame des données Agresso
            df_n2f: DataFrame des données N2F existantes
            df_n2f_companies: DataFrame des entreprises N2F (optionnel)
            status_col: Nom de la colonne de statut

        Returns:
            Tuple[DataFrame, str]: DataFrame des résultats et nom de la colonne de statut
        """
        # Identifier les entités à créer (présentes dans Agresso mais pas dans N2F)
        entities_to_create = self._get_entities_to_create(df_agresso, df_n2f)

        if entities_to_create.empty:
            return pd.DataFrame(), status_col

        api_results: List[ApiResult] = []

        for _, entity in entities_to_create.iterrows():
            try:
                # Construire le payload et effectuer l'opération
                payload = self.build_payload(entity, df_agresso, df_n2f, df_n2f_companies)
                api_result = self._perform_create_operation(entity, payload, df_n2f_companies)
                api_results.append(api_result)
            except Exception as e:
                # Gestion d'erreur standardisée
                entity_id = self.get_entity_id(entity)
                log_error(self.scope.upper(), "CREATE", entity_id, e, f"Payload: {payload}")
                api_results.append(self._create_error_result("CREATE", entity_id, str(e)))

        # Ajouter les colonnes de logging
        entities_to_create[status_col] = [result.success for result in api_results]
        entities_to_create = add_api_logging_columns(entities_to_create, api_results)

        return entities_to_create, status_col

    def update_entities(
        self,
        df_agresso: pd.DataFrame,
        df_n2f: pd.DataFrame,
        df_n2f_companies: pd.DataFrame = None,
        status_col: str = "updated"
    ) -> Tuple[pd.DataFrame, str]:
        """
        Met à jour les entités existantes dans N2F.

        Args:
            df_agresso: DataFrame des données Agresso
            df_n2f: DataFrame des données N2F existantes
            df_n2f_companies: DataFrame des entreprises N2F (optionnel)
            status_col: Nom de la colonne de statut

        Returns:
            Tuple[DataFrame, str]: DataFrame des résultats et nom de la colonne de statut
        """
        if df_agresso.empty or df_n2f.empty:
            return pd.DataFrame(), status_col

        # Identifier les entités à mettre à jour (présentes dans les deux systèmes)
        entities_to_update = self._get_entities_to_update(df_agresso, df_n2f)

        if entities_to_update.empty:
            return pd.DataFrame(), status_col

        # Créer un index pour accéder rapidement aux données N2F
        n2f_index = self._create_n2f_index(df_n2f)

        api_results: List[ApiResult] = []
        updated_entities: List[Dict] = []

        for _, entity in entities_to_update.iterrows():
            try:
                # Construire le payload
                payload = self.build_payload(entity, df_agresso, df_n2f, df_n2f_companies)

                # Récupérer l'entité N2F correspondante
                n2f_entity = self._get_n2f_entity(entity, n2f_index)

                # Vérifier s'il y a des changements
                if not self._has_changes(payload, n2f_entity):
                    continue

                # Effectuer l'opération de mise à jour
                api_result = self._perform_update_operation(entity, payload, n2f_entity, df_n2f_companies)
                api_results.append(api_result)
                updated_entities.append(entity.to_dict())

            except Exception as e:
                # Gestion d'erreur standardisée
                entity_id = self.get_entity_id(entity)
                log_error(self.scope.upper(), "UPDATE", entity_id, e, f"Payload: {payload}")
                api_results.append(self._create_error_result("UPDATE", entity_id, str(e)))
                updated_entities.append(entity.to_dict())

        if updated_entities:
            df_result = pd.DataFrame(updated_entities)
            df_result[status_col] = [result.success for result in api_results]
            df_result = add_api_logging_columns(df_result, api_results)
            return df_result, status_col

        return pd.DataFrame(), status_col

    def delete_entities(
        self,
        df_agresso: pd.DataFrame,
        df_n2f: pd.DataFrame,
        df_n2f_companies: pd.DataFrame = None,
        status_col: str = "deleted"
    ) -> Tuple[pd.DataFrame, str]:
        """
        Supprime les entités obsolètes de N2F.

        Args:
            df_agresso: DataFrame des données Agresso
            df_n2f: DataFrame des données N2F existantes
            df_n2f_companies: DataFrame des entreprises N2F (optionnel)
            status_col: Nom de la colonne de statut

        Returns:
            Tuple[DataFrame, str]: DataFrame des résultats et nom de la colonne de statut
        """
        if df_n2f.empty:
            return pd.DataFrame(), status_col

        # Identifier les entités à supprimer (présentes dans N2F mais pas dans Agresso)
        entities_to_delete = self._get_entities_to_delete(df_agresso, df_n2f)

        if entities_to_delete.empty:
            return pd.DataFrame(), status_col

        api_results: List[ApiResult] = []

        for _, entity in entities_to_delete.iterrows():
            try:
                # Effectuer l'opération de suppression
                api_result = self._perform_delete_operation(entity, df_n2f_companies)
                api_results.append(api_result)
            except Exception as e:
                # Gestion d'erreur standardisée
                entity_id = self.get_entity_id(entity)
                log_error(self.scope.upper(), "DELETE", entity_id, e)
                api_results.append(self._create_error_result("DELETE", entity_id, str(e)))

        # Ajouter les colonnes de logging
        entities_to_delete[status_col] = [result.success for result in api_results]
        entities_to_delete = add_api_logging_columns(entities_to_delete, api_results)

        return entities_to_delete, status_col

    # Méthodes abstraites à implémenter dans les classes concrètes
    @abstractmethod
    def build_payload(self, entity: pd.Series, df_agresso: pd.DataFrame,
                     df_n2f: pd.DataFrame, df_n2f_companies: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Construit le payload pour l'API N2F.

        Args:
            entity: Entité à traiter
            df_agresso: DataFrame des données Agresso
            df_n2f: DataFrame des données N2F
            df_n2f_companies: DataFrame des entreprises N2F (optionnel)

        Returns:
            Dict: Payload pour l'API N2F
        """
        pass

    @abstractmethod
    def get_entity_id(self, entity: pd.Series) -> str:
        """
        Retourne l'identifiant unique de l'entité.

        Args:
            entity: Entité à traiter

        Returns:
            str: Identifiant unique de l'entité
        """
        pass

    @abstractmethod
    def get_agresso_id_column(self) -> str:
        """
        Retourne le nom de la colonne d'identifiant dans les données Agresso.

        Returns:
            str: Nom de la colonne d'identifiant
        """
        pass

    @abstractmethod
    def get_n2f_id_column(self) -> str:
        """
        Retourne le nom de la colonne d'identifiant dans les données N2F.

        Returns:
            str: Nom de la colonne d'identifiant
        """
        pass

    # Méthodes abstraites pour les opérations spécifiques
    @abstractmethod
    def _perform_create_operation(self, entity: pd.Series, payload: Dict,
                                df_n2f_companies: pd.DataFrame = None) -> ApiResult:
        """Effectue l'opération de création spécifique à l'entité."""
        pass

    @abstractmethod
    def _perform_update_operation(self, entity: pd.Series, payload: Dict,
                                n2f_entity: Dict, df_n2f_companies: pd.DataFrame = None) -> ApiResult:
        """Effectue l'opération de mise à jour spécifique à l'entité."""
        pass

    @abstractmethod
    def _perform_delete_operation(self, entity: pd.Series,
                                df_n2f_companies: pd.DataFrame = None) -> ApiResult:
        """Effectue l'opération de suppression spécifique à l'entité."""
        pass

    # Méthodes utilitaires
    def _get_entities_to_create(self, df_agresso: pd.DataFrame, df_n2f: pd.DataFrame) -> pd.DataFrame:
        """Identifie les entités à créer."""
        if df_n2f.empty:
            return df_agresso.copy()

        agresso_id_col = self.get_agresso_id_column()
        n2f_id_col = self.get_n2f_id_column()

        return df_agresso[~df_agresso[agresso_id_col].isin(df_n2f[n2f_id_col])].copy()

    def _get_entities_to_update(self, df_agresso: pd.DataFrame, df_n2f: pd.DataFrame) -> pd.DataFrame:
        """Identifie les entités à mettre à jour."""
        agresso_id_col = self.get_agresso_id_column()
        n2f_id_col = self.get_n2f_id_column()

        return df_agresso[df_agresso[agresso_id_col].isin(df_n2f[n2f_id_col])].copy()

    def _get_entities_to_delete(self, df_agresso: pd.DataFrame, df_n2f: pd.DataFrame) -> pd.DataFrame:
        """Identifie les entités à supprimer."""
        if df_agresso.empty:
            return df_n2f.copy()

        agresso_id_col = self.get_agresso_id_column()
        n2f_id_col = self.get_n2f_id_column()

        return df_n2f[~df_n2f[n2f_id_col].isin(df_agresso[agresso_id_col])].copy()

    def _create_n2f_index(self, df_n2f: pd.DataFrame) -> Dict:
        """Crée un index pour accéder rapidement aux données N2F."""
        n2f_id_col = self.get_n2f_id_column()
        return df_n2f.set_index(n2f_id_col).to_dict(orient="index")

    def _get_n2f_entity(self, entity: pd.Series, n2f_index: Dict) -> Dict:
        """Récupère l'entité N2F correspondante."""
        entity_id = self.get_entity_id(entity)
        n2f_entity = n2f_index.get(entity_id, {})

        # Ajouter l'ID car set_index() le retire des valeurs
        if n2f_entity:
            n2f_entity[self.get_n2f_id_column()] = entity_id

        return n2f_entity

    def _has_changes(self, payload: Dict, n2f_entity: Dict) -> bool:
        """Vérifie s'il y a des changements entre le payload et l'entité N2F."""
        entity_type = self.scope.rstrip('s')  # "users" -> "user", "projects" -> "project"
        return has_payload_changes(payload, n2f_entity, entity_type)

    def _create_error_result(self, action: str, entity_id: str, error_message: str) -> ApiResult:
        """Crée un ApiResult d'erreur standardisé."""
        return ApiResult.error_result(
            error_message,
            error_details=error_message,
            action_type=action.lower(),
            object_type=self.scope.rstrip('s'),
            object_id=entity_id,
            scope=self.scope
        )
