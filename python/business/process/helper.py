import pandas as pd
from typing import Dict, Any


def reporting(
    result_df      : pd.DataFrame,
    empty_message  : str,
    update_message : str,
    status_col     : str
) -> None:
    """
    Génère un rapport à partir du DataFrame de résultats.
    Affiche le nombre de succès et d'échecs si une colonne de statut est fournie.
    """
    if result_df.empty:
        print(empty_message)
    else:
        print(update_message + " :")
        if status_col and status_col in result_df.columns:
            nb_success = result_df[status_col].sum()
            nb_total = len(result_df)
            nb_failed = nb_total - nb_success
            print(f"  Succès : {nb_success} / {nb_total}")
            print(f"  Échecs : {nb_failed} / {nb_total}")
        else:
            print(f"  Total : {len(result_df)}")


def has_payload_changes(payload: Dict[str, Any], n2f_entity: Dict[str, Any], entity_type: str = None) -> bool:
    """
    Compare les champs du payload avec les données N2F pour détecter les changements.
    Ignore les champs non pertinents et gère les types de données.

    Args:
        payload: Dictionnaire contenant les données à envoyer à l'API
        n2f_entity: Dictionnaire contenant les données actuelles de N2F
        entity_type: Type d'entité ('axe' ou 'user') pour adapter la logique

    Returns:
        bool: True si des changements sont détectés, False sinon
    """
            # Champs à ignorer car ils peuvent changer sans être des changements métier
    ignored_fields = {
        'uuid', 'id', 'created_at', 'updated_at', 'created', 'updated',
        'company_id', 'manager_id', 'profile_id', 'role_id'
    }

    # Champs spécifiques aux axes à ignorer (code est un identifiant technique pour les axes)
    axe_ignored_fields = {
        'axe_id', 'company_uuid', 'created_by', 'modified_by', 'code'
    }

    for key, value in payload.items():
        # Ignorer les champs non pertinents
        if key in ignored_fields:
            continue

        # Pour les axes, ignorer aussi les champs spécifiques aux axes
        if entity_type == 'axe' and key in axe_ignored_fields:
            continue

        # Vérifier si le champ existe dans N2F
        if key not in n2f_entity:
            # Si le champ n'existe pas dans N2F mais est None dans le payload, ignorer
            if value is None:
                continue
            # Sinon, c'est un vrai changement
            return True

        n2f_value = n2f_entity[key]

        # Normaliser les types pour la comparaison
        if isinstance(value, (int, float)) and isinstance(n2f_value, (int, float)):
            # Comparaison numérique avec tolérance pour les floats
            if abs(float(value) - float(n2f_value)) > 0.001:
                return True
        elif isinstance(value, str) and isinstance(n2f_value, str):
            # Comparaison de chaînes (ignorer les espaces en début/fin)
            if value.strip() != n2f_value.strip():
                return True
        elif value != n2f_value:
            # Gérer les cas spéciaux None vs nan
            if (value is None and (n2f_value is None or str(n2f_value).lower() == 'nan')) or \
               (n2f_value is None and (value is None or str(value).lower() == 'nan')):
                continue
            # Comparaison directe pour les autres types
            return True

    return False


def debug_payload_changes(payload: Dict[str, Any], n2f_entity: Dict[str, Any], entity_type: str = None) -> Dict[str, Any]:
    """
    Debug: Affiche les différences entre payload et n2f_entity.

    Args:
        payload: Dictionnaire contenant les données à envoyer à l'API
        n2f_entity: Dictionnaire contenant les données actuelles de N2F
        entity_type: Type d'entité ('axe' ou 'user') pour adapter la logique

    Returns:
        Dict contenant les différences détectées
    """
    differences = {}

        # Champs à ignorer car ils peuvent changer sans être des changements métier
    ignored_fields = {
        'uuid', 'id', 'created_at', 'updated_at', 'created', 'updated',
        'company_id', 'manager_id', 'profile_id', 'role_id'
    }

    # Champs spécifiques aux axes à ignorer (code est un identifiant technique pour les axes)
    axe_ignored_fields = {
        'axe_id', 'company_uuid', 'created_by', 'modified_by', 'code'
    }

    for key, value in payload.items():
        # Ignorer les champs non pertinents
        if key in ignored_fields:
            continue

        # Pour les axes, ignorer aussi les champs spécifiques aux axes
        if entity_type == 'axe' and key in axe_ignored_fields:
            continue

        # Vérifier si le champ existe dans N2F
        if key not in n2f_entity:
            # Si le champ n'existe pas dans N2F mais est None dans le payload, ignorer
            if value is None:
                continue
            # Sinon, c'est un vrai changement
            differences[key] = {
                'payload_value': value,
                'n2f_value': 'MISSING',
                'type': 'missing_field'
            }
            continue

        n2f_value = n2f_entity[key]

        # Normaliser les types pour la comparaison
        if isinstance(value, (int, float)) and isinstance(n2f_value, (int, float)):
            # Comparaison numérique avec tolérance pour les floats
            if abs(float(value) - float(n2f_value)) > 0.001:
                differences[key] = {
                    'payload_value': value,
                    'n2f_value': n2f_value,
                    'type': 'numeric_difference'
                }
        elif isinstance(value, str) and isinstance(n2f_value, str):
            # Comparaison de chaînes (ignorer les espaces en début/fin)
            if value.strip() != n2f_value.strip():
                differences[key] = {
                    'payload_value': value,
                    'n2f_value': n2f_value,
                    'type': 'string_difference'
                }
        elif value != n2f_value:
            # Gérer les cas spéciaux None vs nan
            if (value is None and (n2f_value is None or str(n2f_value).lower() == 'nan')) or \
               (n2f_value is None and (value is None or str(value).lower() == 'nan')):
                continue
            # Comparaison directe pour les autres types
            differences[key] = {
                'payload_value': value,
                'n2f_value': n2f_value,
                'type': 'direct_difference'
            }

    return differences
