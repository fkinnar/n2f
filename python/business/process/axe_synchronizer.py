from typing import Dict, Any
import pandas as pd
from n2f.api_result import ApiResult
from business.process.base_synchronizer import EntitySynchronizer
from n2f.process.axe import build_axe_payload, lookup_company_id


class AxeSynchronizer(EntitySynchronizer):
    """
    Synchroniseur spécifique pour les axes.

    Implémente les méthodes abstraites de EntitySynchronizer
    pour gérer la synchronisation des axes entre Agresso et N2F.
    """

    def __init__(self, n2f_client, sandbox: bool, axe_id: str, scope: str = "projects"):
        """
        Initialise le synchroniseur d'axes.

        Args:
            n2f_client: Client API N2F
            sandbox: Mode sandbox ou production
            axe_id: Identifiant de l'axe à synchroniser
            scope: Scope de synchronisation (ex: "projects", "plates")
        """
        super().__init__(n2f_client, sandbox, scope)
        self.axe_id = axe_id

    def build_payload(self, entity: pd.Series, df_agresso: pd.DataFrame,
                     df_n2f: pd.DataFrame, df_n2f_companies: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Construit le payload pour l'API N2F axe.

        Args:
            entity: Entité axe à traiter
            df_agresso: DataFrame des données Agresso
            df_n2f: DataFrame des données N2F
            df_n2f_companies: DataFrame des entreprises N2F (optionnel)

        Returns:
            Dict: Payload pour l'API N2F axe
        """
        return build_axe_payload(entity, self.sandbox)

    def get_entity_id(self, entity: pd.Series) -> str:
        """
        Retourne l'identifiant unique de l'axe (code).

        Args:
            entity: Entité axe à traiter

        Returns:
            str: Code de l'axe
        """
        return entity["code"]

    def get_agresso_id_column(self) -> str:
        """
        Retourne le nom de la colonne d'identifiant dans les données Agresso.

        Returns:
            str: Nom de la colonne d'identifiant (code)
        """
        return "code"

    def get_n2f_id_column(self) -> str:
        """
        Retourne le nom de la colonne d'identifiant dans les données N2F.

        Returns:
            str: Nom de la colonne d'identifiant (code)
        """
        return "code"

    def _perform_create_operation(self, entity: pd.Series, payload: Dict,
                                df_n2f_companies: pd.DataFrame = None) -> ApiResult:
        """
        Effectue l'opération de création d'axe.

        Args:
            entity: Entité axe à créer
            payload: Payload pour l'API N2F
            df_n2f_companies: DataFrame des entreprises N2F (optionnel)

        Returns:
            ApiResult: Résultat de l'opération
        """
        company_code = entity.get("client")
        company_id = lookup_company_id(company_code, df_n2f_companies, self.sandbox)

        if company_id:
            return self.n2f_client.upsert_axe_value(company_id, self.axe_id, payload, "create", self.scope)
        else:
            # Créer un ApiResult d'erreur si l'entreprise n'est pas trouvée
            error_msg = f"Company not found: {company_code}"
            return self._create_error_result("CREATE", self.get_entity_id(entity), error_msg)

    def _perform_update_operation(self, entity: pd.Series, payload: Dict,
                                n2f_entity: Dict, df_n2f_companies: pd.DataFrame = None) -> ApiResult:
        """
        Effectue l'opération de mise à jour d'axe.

        Args:
            entity: Entité axe à mettre à jour
            payload: Payload pour l'API N2F
            n2f_entity: Entité N2F existante
            df_n2f_companies: DataFrame des entreprises N2F (optionnel)

        Returns:
            ApiResult: Résultat de l'opération
        """
        company_code = entity.get("client")
        company_id = lookup_company_id(company_code, df_n2f_companies, self.sandbox)

        if company_id:
            return self.n2f_client.upsert_axe_value(company_id, self.axe_id, payload, "update", self.scope)
        else:
            # Créer un ApiResult d'erreur si l'entreprise n'est pas trouvée
            error_msg = f"Company not found: {company_code}"
            return self._create_error_result("UPDATE", self.get_entity_id(entity), error_msg)

    def _perform_delete_operation(self, entity: pd.Series,
                                df_n2f_companies: pd.DataFrame = None) -> ApiResult:
        """
        Effectue l'opération de suppression d'axe.

        Args:
            entity: Entité axe à supprimer
            df_n2f_companies: DataFrame des entreprises N2F (optionnel)

        Returns:
            ApiResult: Résultat de l'opération
        """
        company_id = entity.get("company_id")  # Assumes company_id was added during get_axes

        if company_id:
            return self.n2f_client.delete_axe_value(company_id, self.axe_id, self.get_entity_id(entity), self.scope)
        else:
            # Créer un ApiResult d'erreur si l'ID de l'entreprise n'est pas trouvé
            error_msg = "Company ID not found: company_id field missing"
            return self._create_error_result("DELETE", self.get_entity_id(entity), error_msg)
