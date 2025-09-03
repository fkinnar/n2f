from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any


@dataclass
class ApiResult:
    """Résultat standardisé d'un appel API avec informations de debugging."""

    success: bool
    message: str = ""
    status_code: Optional[int] = None
    duration_ms: Optional[float] = None
    timestamp: Optional[datetime] = None
    response_data: Optional[Any] = None
    error_details: Optional[str] = None

    # Informations de contexte
    action_type: Optional[str] = None  # "create", "update", "delete"
    object_type: Optional[str] = None  # "user", "project", "plate", "subpost"
    object_id: Optional[str] = None  # email pour user, code pour axe, etc.
    scope: Optional[str] = None  # "users", "projects", "plates", "subposts"

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> dict:
        """Convertit le résultat en dictionnaire pour stockage dans DataFrame."""
        return {
            "api_success": self.success,
            "api_message": self.message,
            "api_status_code": self.status_code,
            "api_duration_ms": self.duration_ms,
            "api_timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "api_error_details": self.error_details,
            "api_action_type": self.action_type,
            "api_object_type": self.object_type,
            "api_object_id": self.object_id,
            "api_scope": self.scope,
        }

    @classmethod
    def success_result(
        cls,
        message: str = "Success",
        status_code: int = 200,
        duration_ms: Optional[float] = None,
        response_data: Optional[Any] = None,
        action_type: Optional[str] = None,
        object_type: Optional[str] = None,
        object_id: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> "ApiResult":
        """Crée un résultat de succès."""
        return cls(
            success=True,
            message=message,
            status_code=status_code,
            duration_ms=duration_ms,
            response_data=response_data,
            action_type=action_type,
            object_type=object_type,
            object_id=object_id,
            scope=scope,
        )

    @classmethod
    def error_result(
        cls,
        message: str,
        status_code: Optional[int] = None,
        duration_ms: Optional[float] = None,
        error_details: Optional[str] = None,
        action_type: Optional[str] = None,
        object_type: Optional[str] = None,
        object_id: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> "ApiResult":
        """Crée un résultat d'erreur."""
        return cls(
            success=False,
            message=message,
            status_code=status_code,
            duration_ms=duration_ms,
            error_details=error_details,
            action_type=action_type,
            object_type=object_type,
            object_id=object_id,
            scope=scope,
        )

    @classmethod
    def simulate_result(
        cls,
        operation: str,
        action_type: Optional[str] = None,
        object_type: Optional[str] = None,
        object_id: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> "ApiResult":
        """Crée un résultat pour les opérations en mode simulation."""
        return cls(
            success=True,
            message=f"Simulated {operation}",
            status_code=200,
            duration_ms=0.0,
            action_type=action_type,
            object_type=object_type,
            object_id=object_id,
            scope=scope,
        )
