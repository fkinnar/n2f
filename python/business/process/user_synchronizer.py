from typing import Dict, Any
import pandas as pd
from n2f.api_result import ApiResult
from business.process.base_synchronizer import EntitySynchronizer


class UserSynchronizer(EntitySynchronizer):
    """
    Synchroniseur spécifique pour les utilisateurs.

    Implémente les méthodes abstraites de EntitySynchronizer
    pour gérer la synchronisation des utilisateurs entre Agresso et N2F.
    """

    def __init__(self, n2f_client, sandbox: bool):
        """
        Initialise le synchroniseur d'utilisateurs.

        Args:
            n2f_client: Client API N2F
            sandbox: Mode sandbox ou production
        """
        super().__init__(n2f_client, sandbox, "users")

    def build_payload(self, entity: pd.Series, df_agresso: pd.DataFrame,
                     df_n2f: pd.DataFrame, df_n2f_companies: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Construit le payload pour l'API N2F utilisateur.

        Args:
            entity: Entité utilisateur à traiter
            df_agresso: DataFrame des données Agresso
            df_n2f: DataFrame des données N2F
            df_n2f_companies: DataFrame des entreprises N2F (optionnel)

        Returns:
            Dict: Payload pour l'API N2F utilisateur
        """
        # Import déplacé ici pour éviter les imports circulaires
        from n2f.process.user import build_user_payload
        return build_user_payload(entity, df_agresso, df_n2f, self.n2f_client, df_n2f_companies, self.sandbox)

    def get_entity_id(self, entity: pd.Series) -> str:
        """
        Retourne l'identifiant unique de l'utilisateur (email).

        Args:
            entity: Entité utilisateur à traiter

        Returns:
            str: Email de l'utilisateur
        """
        return entity["AdresseEmail"]

    def get_agresso_id_column(self) -> str:
        """
        Retourne le nom de la colonne d'identifiant dans les données Agresso.

        Returns:
            str: Nom de la colonne d'identifiant (AdresseEmail)
        """
        return "AdresseEmail"

    def get_n2f_id_column(self) -> str:
        """
        Retourne le nom de la colonne d'identifiant dans les données N2F.

        Returns:
            str: Nom de la colonne d'identifiant (mail)
        """
        return "mail"

    def _perform_create_operation(self, entity: pd.Series, payload: Dict,
                                df_n2f_companies: pd.DataFrame = None) -> ApiResult:
        """
        Effectue l'opération de création d'utilisateur.

        Args:
            entity: Entité utilisateur à créer
            payload: Payload pour l'API N2F
            df_n2f_companies: DataFrame des entreprises N2F (optionnel)

        Returns:
            ApiResult: Résultat de l'opération
        """
        return self.n2f_client.create_user(payload)

    def _perform_update_operation(self, entity: pd.Series, payload: Dict,
                                n2f_entity: Dict, df_n2f_companies: pd.DataFrame = None) -> ApiResult:
        """
        Effectue l'opération de mise à jour d'utilisateur.

        Args:
            entity: Entité utilisateur à mettre à jour
            payload: Payload pour l'API N2F
            n2f_entity: Entité N2F existante
            df_n2f_companies: DataFrame des entreprises N2F (optionnel)

        Returns:
            ApiResult: Résultat de l'opération
        """
        return self.n2f_client.update_user(payload)

    def _perform_delete_operation(self, entity: pd.Series,
                                df_n2f_companies: pd.DataFrame = None) -> ApiResult:
        """
        Effectue l'opération de suppression d'utilisateur.

        Args:
            entity: Entité utilisateur à supprimer
            df_n2f_companies: DataFrame des entreprises N2F (optionnel)

        Returns:
            ApiResult: Résultat de l'opération
        """
        user_email = self.get_entity_id(entity)
        return self.n2f_client.delete_user(user_email)
