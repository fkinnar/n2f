import pandas as pd
from typing import Dict, Any


def reporting(
    result_df      : pd.DataFrame,
    empty_message  : str,
    update_message : str,
    status_col     : str
) -> None:
    """
    Generates a report from the results DataFrame.
    Displays the number of successes and failures if a status column is provided.
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


def log_error(scope: str, action: str, entity_id: str, error: Exception, context: str = "") -> None:
    """
    Log an error with context to facilitate debugging.

    Args:
        scope: Scope (USERS, PROJECTS, PLATES, SUBPOSTS)
        action: Action performed (CREATE, UPDATE, DELETE)
        entity_id: Entity identifier (email for users, code for axes)
        error: Exception raised
        context: Optional additional context
    """
    context_str = f" - {context}" if context else ""
    print(f"[ERROR] [{scope}] [{action}] [{entity_id}]{context_str} - {str(error)}")


def has_payload_changes(payload: Dict[str, Any], n2f_entity: Dict[str, Any], entity_type: str = None) -> bool:
    """
    Compare payload fields with N2F data to detect changes.
    Ignores irrelevant fields and handles data types.

    Args:
        payload: Dictionary containing data to send to API
        n2f_entity: Dictionary containing current N2F data
        entity_type: Entity type ('axe' or 'user') to adapt logic

    Returns:
        bool: True if changes are detected, False otherwise
    """
    # Fields to ignore as they can change without being business changes
    ignored_fields = {
        'uuid', 'id', 'created_at', 'updated_at', 'created', 'updated',
        'company_id', 'manager_id', 'profile_id', 'role_id'
    }

    # Axe-specific fields to ignore (code is a technical identifier for axes)
    axe_ignored_fields = {
        'axe_id', 'company_uuid', 'created_by', 'modified_by', 'code'
    }

    for key, value in payload.items():
        # Ignore irrelevant fields
        if key in ignored_fields:
            continue

        # For axes, also ignore axe-specific fields
        if entity_type == 'axe' and key in axe_ignored_fields:
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
            if (value is None and (n2f_value is None or str(n2f_value).lower() == 'nan')) or \
               (n2f_value is None and (value is None or str(value).lower() == 'nan')):
                continue
            # Direct comparison for other types
            return True

    return False


def debug_payload_changes(payload: Dict[str, Any], n2f_entity: Dict[str, Any], entity_type: str = None) -> Dict[str, Any]:
    """
    Debug: Shows differences between payload and n2f_entity.

    Args:
        payload: Dictionary containing data to send to API
        n2f_entity: Dictionary containing current N2F data
        entity_type: Entity type ('axe' or 'user') to adapt logic

    Returns:
        Dict containing detected differences
    """
    differences = {}

    # Fields to ignore as they can change without being business changes
    ignored_fields = {
        'uuid', 'id', 'created_at', 'updated_at', 'created', 'updated',
        'company_id', 'manager_id', 'profile_id', 'role_id'
    }

    # Axe-specific fields to ignore (code is a technical identifier for axes)
    axe_ignored_fields = {
        'axe_id', 'company_uuid', 'created_by', 'modified_by', 'code'
    }

    for key, value in payload.items():
        # Ignore irrelevant fields
        if key in ignored_fields:
            continue

        # For axes, also ignore axe-specific fields
        if entity_type == 'axe' and key in axe_ignored_fields:
            continue

        # Check if field exists in N2F
        if key not in n2f_entity:
            # If field doesn't exist in N2F but is None in payload, ignore
            if value is None:
                continue
            # Otherwise, it's a real change
            differences[key] = {
                'payload_value': value,
                'n2f_value': 'MISSING',
                'type': 'missing_field'
            }
            continue

        n2f_value = n2f_entity[key]

        # Normalize types for comparison
        if isinstance(value, (int, float)) and isinstance(n2f_value, (int, float)):
            # Numeric comparison with tolerance for floats
            if abs(float(value) - float(n2f_value)) > 0.001:
                differences[key] = {
                    'payload_value': value,
                    'n2f_value': n2f_value,
                    'type': 'numeric_difference'
                }
        elif isinstance(value, str) and isinstance(n2f_value, str):
            # String comparison (ignore leading/trailing spaces)
            if value.strip() != n2f_value.strip():
                differences[key] = {
                    'payload_value': value,
                    'n2f_value': n2f_value,
                    'type': 'string_difference'
                }
        elif value != n2f_value:
            # Handle special cases None vs nan
            if (value is None and (n2f_value is None or str(n2f_value).lower() == 'nan')) or \
               (n2f_value is None and (value is None or str(value).lower() == 'nan')):
                continue
            # Direct comparison for other types
            differences[key] = {
                'payload_value': value,
                'n2f_value': n2f_value,
                'type': 'direct_difference'
            }

    return differences
