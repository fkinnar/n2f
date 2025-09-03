import pandas as pd
from typing import Dict, Any


def reporting(
    result_df: pd.DataFrame, empty_message: str, update_message: str, status_col: str
) -> None:
    """
    Génère un rapport détaillé à partir d'un DataFrame de résultats.

    Cette fonction analyse les résultats d'une opération de synchronisation
    et affiche un résumé formaté avec les statistiques de succès/échec.

    Args:
        result_df: DataFrame contenant les résultats des opérations
        empty_message: Message à afficher si le DataFrame est vide
        update_message: Message de base pour les opérations avec résultats
        status_col: Nom de la colonne contenant le statut (True=succès, False=échec)

    Example:
        >>> df = pd.DataFrame({
        ...     'entity_id': ['user1', 'user2', 'user3'],
        ...     'success': [True, True, False]
        ... })
        >>> reporting(df, "Aucune opération", "Opérations effectuées", "success")
        Opérations effectuées :
          Success : 2 / 3
          Failures : 1 / 3
    """
    if result_df.empty:
        print(empty_message)
    else:
        print(update_message + " :")
        if status_col and status_col in result_df.columns:
            nb_success = result_df[status_col].sum()
            nb_total = len(result_df)
            nb_failed = nb_total - nb_success
            print(f"  Success : {nb_success} / {nb_total}")
            print(f"  Failures : {nb_failed} / {nb_total}")
        else:
            print(f"  Total : {len(result_df)}")


def log_error(
    scope: str, action: str, entity_id: str, error: Exception, context: str = ""
) -> None:
    """
    Enregistre une erreur avec son contexte pour faciliter le debugging.

    Cette fonction formate et affiche les erreurs de manière structurée,
    incluant toutes les informations nécessaires pour identifier et
    résoudre le problème.

    Args:
        scope: Périmètre de synchronisation (USERS, PROJECTS, PLATES, SUBPOSTS)
        action: Action effectuée (CREATE, UPDATE, DELETE)
        entity_id: Identifiant de l'entité (email pour users, code pour axes)
        error: Exception levée
        context: Contexte supplémentaire optionnel

    Example:
        >>> try:
        ...     # Opération qui peut échouer
        ...     pass
        ... except Exception as e:
        ...     log_error("USERS", "CREATE", "john@example.com", e, "Payload validation")
        [ERROR] [USERS] [CREATE] [john@example.com] - Payload validation - Invalid email format
    """
    context_str = f" - {context}" if context else ""
    print(f"[ERROR] [{scope}] [{action}] [{entity_id}]{context_str} - {str(error)}")


def has_payload_changes(
    payload: Dict[str, Any], n2f_entity: Dict[str, Any], entity_type: str = None
) -> bool:
    """
    Compare les champs du payload avec les données N2F pour détecter les changements.

    Cette fonction effectue une comparaison intelligente entre les données
    à synchroniser et les données existantes dans N2F. Elle ignore les
    champs techniques non pertinents et gère les différents types de données.

    Args:
        payload: Dictionnaire contenant les données à envoyer à l'API
        n2f_entity: Dictionnaire contenant les données actuelles de N2F
        entity_type: Type d'entité ('axe' ou 'user') pour adapter la logique

    Returns:
        bool: True si des changements sont détectés, False sinon

    Example:
        >>> payload = {'name': 'John Doe', 'email': 'john@example.com'}
        >>> n2f_entity = {'name': 'John Doe', 'email': 'john@example.com', 'id': 123}
        >>> has_payload_changes(payload, n2f_entity, 'user')
        False

        >>> payload = {'name': 'Jane Doe', 'email': 'jane@example.com'}
        >>> has_payload_changes(payload, n2f_entity, 'user')
        True
    """
    # Fields to ignore as they can change without being business changes
    ignored_fields = {
        "uuid",
        "id",
        "created_at",
        "updated_at",
        "created",
        "updated",
        "company_id",
        "manager_id",
        "profile_id",
        "role_id",
    }

    # Axe-specific fields to ignore (code is a technical identifier for axes)
    axe_ignored_fields = {"axe_id", "company_uuid", "created_by", "modified_by", "code"}

    for key, value in payload.items():
        # Ignore irrelevant fields
        if key in ignored_fields:
            continue

        # For axes, also ignore axe-specific fields
        if entity_type == "axe" and key in axe_ignored_fields:
            continue

        # Check if field exists in N2F
        if key not in n2f_entity:
            # If field doesn't exist in N2F but is None in payload, ignore
            if value is None:
                continue
            # Otherwise, it's a real change
            return True

        n2f_value = n2f_entity[key]

        # Normalize types for comparison
        if isinstance(value, (int, float)) and isinstance(n2f_value, (int, float)):
            # Numeric comparison with tolerance for floats
            if abs(float(value) - float(n2f_value)) > 0.001:
                return True
        elif isinstance(value, str) and isinstance(n2f_value, str):
            # String comparison (ignore leading/trailing spaces)
            if value.strip() != n2f_value.strip():
                return True
        elif value != n2f_value:
            # Handle special cases None vs nan
            if (
                value is None and (n2f_value is None or str(n2f_value).lower() == "nan")
            ) or (n2f_value is None and (value is None or str(value).lower() == "nan")):
                continue
            # Direct comparison for other types
            return True

    return False
