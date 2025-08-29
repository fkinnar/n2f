"""
Exceptions personnalisées pour le projet de synchronisation N2F.

Ce module définit une hiérarchie d'exceptions spécifiques au projet
pour améliorer la gestion d'erreur et faciliter le debugging.
"""

from typing import Optional, Dict, Any


class SyncException(Exception):
    """
    Exception de base pour toutes les erreurs de synchronisation.

    Cette classe sert de point d'entrée pour toutes les exceptions
    spécifiques au projet de synchronisation N2F.
    """

    def __init__(self, message: str, details: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        """
        Initialise l'exception de synchronisation.

        Args:
            message: Message d'erreur principal
            details: Détails supplémentaires de l'erreur (optionnel)
            context: Contexte supplémentaire (optionnel)
        """
        super().__init__(message)
        self.message = message
        self.details = details
        self.context = context or {}

    def __str__(self) -> str:
        """Retourne une représentation string de l'exception."""
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'exception en dictionnaire pour la sérialisation."""
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
            "context": self.context
        }


class ApiException(SyncException):
    """
    Exception levée lors d'erreurs d'API.

    Cette exception est utilisée pour les erreurs liées aux appels API
    vers N2F ou Agresso.
    """

    def __init__(self, message: str, status_code: Optional[int] = None,
                 response_text: Optional[str] = None, endpoint: Optional[str] = None,
                 details: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        """
        Initialise l'exception d'API.

        Args:
            message: Message d'erreur principal
            status_code: Code de statut HTTP (optionnel)
            response_text: Texte de la réponse HTTP (optionnel)
            endpoint: Endpoint appelé (optionnel)
            details: Détails supplémentaires (optionnel)
            context: Contexte supplémentaire (optionnel)
        """
        super().__init__(message, details, context)
        self.status_code = status_code
        self.response_text = response_text
        self.endpoint = endpoint

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'exception en dictionnaire avec les informations d'API."""
        base_dict = super().to_dict()
        base_dict.update({
            "status_code": self.status_code,
            "response_text": self.response_text,
            "endpoint": self.endpoint
        })
        return base_dict


class ValidationException(SyncException):
    """
    Exception levée lors d'erreurs de validation de données.

    Cette exception est utilisée quand les données ne respectent pas
    les règles de validation attendues.
    """

    def __init__(self, message: str, field: Optional[str] = None,
                 value: Optional[Any] = None, expected_format: Optional[str] = None,
                 details: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        """
        Initialise l'exception de validation.

        Args:
            message: Message d'erreur principal
            field: Champ en erreur (optionnel)
            value: Valeur problématique (optionnel)
            expected_format: Format attendu (optionnel)
            details: Détails supplémentaires (optionnel)
            context: Contexte supplémentaire (optionnel)
        """
        super().__init__(message, details, context)
        self.field = field
        self.value = value
        self.expected_format = expected_format

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'exception en dictionnaire avec les informations de validation."""
        base_dict = super().to_dict()
        base_dict.update({
            "field": self.field,
            "value": str(self.value) if self.value is not None else None,
            "expected_format": self.expected_format
        })
        return base_dict


class ConfigurationException(SyncException):
    """
    Exception levée lors d'erreurs de configuration.

    Cette exception est utilisée quand la configuration est invalide
    ou manquante.
    """

    def __init__(self, message: str, config_key: Optional[str] = None,
                 config_file: Optional[str] = None, details: Optional[str] = None,
                 context: Optional[Dict[str, Any]] = None):
        """
        Initialise l'exception de configuration.

        Args:
            message: Message d'erreur principal
            config_key: Clé de configuration problématique (optionnel)
            config_file: Fichier de configuration (optionnel)
            details: Détails supplémentaires (optionnel)
            context: Contexte supplémentaire (optionnel)
        """
        super().__init__(message, details, context)
        self.config_key = config_key
        self.config_file = config_file

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'exception en dictionnaire avec les informations de configuration."""
        base_dict = super().to_dict()
        base_dict.update({
            "config_key": self.config_key,
            "config_file": self.config_file
        })
        return base_dict


class DatabaseException(SyncException):
    """
    Exception levée lors d'erreurs de base de données.

    Cette exception est utilisée pour les erreurs liées aux opérations
    de base de données (Agresso).
    """

    def __init__(self, message: str, sql_query: Optional[str] = None,
                 table: Optional[str] = None, details: Optional[str] = None,
                 context: Optional[Dict[str, Any]] = None):
        """
        Initialise l'exception de base de données.

        Args:
            message: Message d'erreur principal
            sql_query: Requête SQL problématique (optionnel)
            table: Table concernée (optionnel)
            details: Détails supplémentaires (optionnel)
            context: Contexte supplémentaire (optionnel)
        """
        super().__init__(message, details, context)
        self.sql_query = sql_query
        self.table = table

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'exception en dictionnaire avec les informations de base de données."""
        base_dict = super().to_dict()
        base_dict.update({
            "sql_query": self.sql_query,
            "table": self.table
        })
        return base_dict


class AuthenticationException(SyncException):
    """
    Exception levée lors d'erreurs d'authentification.

    Cette exception est utilisée pour les erreurs liées à l'authentification
    avec les APIs (N2F, Agresso).
    """

    def __init__(self, message: str, service: Optional[str] = None,
                 credentials_type: Optional[str] = None, details: Optional[str] = None,
                 context: Optional[Dict[str, Any]] = None):
        """
        Initialise l'exception d'authentification.

        Args:
            message: Message d'erreur principal
            service: Service concerné (N2F, Agresso, etc.)
            credentials_type: Type de credentials (client_id, token, etc.)
            details: Détails supplémentaires (optionnel)
            context: Contexte supplémentaire (optionnel)
        """
        super().__init__(message, details, context)
        self.service = service
        self.credentials_type = credentials_type

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'exception en dictionnaire avec les informations d'authentification."""
        base_dict = super().to_dict()
        base_dict.update({
            "service": self.service,
            "credentials_type": self.credentials_type
        })
        return base_dict


class NetworkException(SyncException):
    """
    Exception levée lors d'erreurs réseau.

    Cette exception est utilisée pour les erreurs de connectivité
    (timeout, connexion refusée, etc.).
    """

    def __init__(self, message: str, url: Optional[str] = None,
                 timeout: Optional[float] = None, retry_count: Optional[int] = None,
                 details: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        """
        Initialise l'exception réseau.

        Args:
            message: Message d'erreur principal
            url: URL concernée (optionnel)
            timeout: Timeout utilisé (optionnel)
            retry_count: Nombre de tentatives (optionnel)
            details: Détails supplémentaires (optionnel)
            context: Contexte supplémentaire (optionnel)
        """
        super().__init__(message, details, context)
        self.url = url
        self.timeout = timeout
        self.retry_count = retry_count

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'exception en dictionnaire avec les informations réseau."""
        base_dict = super().to_dict()
        base_dict.update({
            "url": self.url,
            "timeout": self.timeout,
            "retry_count": self.retry_count
        })
        return base_dict


# Fonctions utilitaires pour la gestion d'exceptions

def wrap_api_call(func):
    """
    Décorateur pour wrapper les appels API avec gestion d'exceptions.

    Args:
        func: Fonction à wrapper

    Returns:
        Fonction wrapper avec gestion d'exceptions
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ApiException:
            # Re-raise les exceptions d'API
            raise
        except Exception as e:
            # Convertir les autres exceptions en ApiException
            raise ApiException(
                message=f"Unexpected error in API call: {str(e)}",
                details=str(e),
                context={"function": func.__name__, "args": str(args), "kwargs": str(kwargs)}
            )
    return wrapper


def handle_sync_exceptions(func):
    """
    Décorateur pour wrapper les fonctions de synchronisation avec gestion d'exceptions.

    Args:
        func: Fonction à wrapper

    Returns:
        Fonction wrapper avec gestion d'exceptions
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SyncException:
            # Re-raise les exceptions de synchronisation
            raise
        except Exception as e:
            # Convertir les autres exceptions en SyncException
            raise SyncException(
                message=f"Unexpected error in synchronization: {str(e)}",
                details=str(e),
                context={"function": func.__name__, "args": str(args), "kwargs": str(kwargs)}
            )
    return wrapper
