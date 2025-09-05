"""
Data normalization functions for business logic.
"""

from typing import Dict, Optional

import pandas as pd

from business.constants import (
    AGRESSO_COL_EMAIL,
    AGRESSO_COL_MANAGER,
    AGRESSO_COL_STRUCTURE,
    AGRESSO_COL_SSO_METHOD,
    N2F_COL_EMAIL,
    N2F_COL_PROFILE,
    N2F_COL_ROLE,
    COL_NAMES,
    COL_CULTURE,
    COL_VALUE,
    DEFAULT_STRUCTURE,
    DEFAULT_PROFILE,
    DEFAULT_ROLE,
    DEFAULT_SSO_METHOD,
    CULTURE_FR,
)
from core.exceptions import ValidationException


def normalize_agresso_users(df_users: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise les utilisateurs Agresso en s'assurant que les colonnes nécessaires
    sont présentes.

        Args:
            df_users: DataFrame contenant les utilisateurs Agresso

        Returns:
            DataFrame normalisé

        Raises:
            ValidationException: Si le DataFrame est vide ou si des colonnes
                essentielles sont manquantes.
    """
    if df_users.empty:
        raise ValidationException(
            message="Le DataFrame des utilisateurs Agresso ne peut pas être vide",
            details="Le DataFrame en entrée est vide.",
        )

    # Vérification des colonnes essentielles
    required_columns = [
        AGRESSO_COL_EMAIL,
        AGRESSO_COL_MANAGER,
        AGRESSO_COL_STRUCTURE,
        AGRESSO_COL_SSO_METHOD,
    ]
    missing_columns = [col for col in required_columns if col not in df_users.columns]
    if missing_columns:
        raise ValidationException(
            message="Colonnes manquantes dans le DataFrame Agresso",
            details=f"Les colonnes suivantes sont requises : {missing_columns}",
        )

    df_users = df_users.copy()

    # Normalisation des emails (gestion des NaN)
    df_users[AGRESSO_COL_EMAIL] = df_users[AGRESSO_COL_EMAIL].astype(str).str.lower()

    # Normalisation des emails de manager (gestion des NaN et chaînes vides)
    df_users[AGRESSO_COL_MANAGER] = (
        df_users[AGRESSO_COL_MANAGER].astype(str).str.lower()
    )
    df_users[AGRESSO_COL_MANAGER] = df_users[AGRESSO_COL_MANAGER].replace(
        ["nan", "none", ""], ""
    )

    # Normalisation des structures (remplacement des valeurs vides par défaut)
    df_users[AGRESSO_COL_STRUCTURE] = (
        df_users[AGRESSO_COL_STRUCTURE]
        .replace(["", "nan", "none"], pd.NA)
        .fillna(DEFAULT_STRUCTURE)
    )

    # Normalisation des méthodes SSO (remplacement de 'Saml' par la valeur par défaut)
    df_users[AGRESSO_COL_SSO_METHOD] = df_users[AGRESSO_COL_SSO_METHOD].replace(
        "Saml", DEFAULT_SSO_METHOD
    )

    return df_users


def normalize_n2f_users(
    df_users: pd.DataFrame,
    profile_mapping: Optional[Dict[str, str]] = None,
    role_mapping: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    """
    Normalise les utilisateurs N2F en s'assurant que les colonnes nécessaires
    sont présentes.
        Remplace les valeurs de 'profile' par leur équivalent français.

        Args:
            df_users: DataFrame contenant les utilisateurs N2F
            profile_mapping: Mapping optionnel pour les profils
            role_mapping: Mapping optionnel pour les rôles

        Returns:
            DataFrame normalisé

        Raises:
            ValidationException: Si le DataFrame est vide ou si des colonnes
                essentielles sont manquantes.
    """
    if df_users.empty:
        raise ValidationException(
            message="Le DataFrame des utilisateurs N2F ne peut pas être vide",
            details="Le DataFrame en entrée est vide.",
        )

    # Vérification des colonnes essentielles
    required_columns = [N2F_COL_EMAIL, N2F_COL_PROFILE, N2F_COL_ROLE]
    missing_columns = [col for col in required_columns if col not in df_users.columns]
    if missing_columns:
        raise ValidationException(
            message="Colonnes manquantes dans le DataFrame N2F",
            details=f"Les colonnes suivantes sont requises : {missing_columns}",
        )

    df_users = df_users.copy()

    # Normalisation des emails (gestion des NaN)
    df_users[N2F_COL_EMAIL] = df_users[N2F_COL_EMAIL].astype(str).str.lower()

    # Normalisation des profils
    df_users[N2F_COL_PROFILE] = (
        df_users[N2F_COL_PROFILE]
        .replace(["", "nan", "none"], pd.NA)
        .fillna(DEFAULT_PROFILE)
    )
    if profile_mapping:
        # Remplacement des valeurs de profile par la version française
        df_users[N2F_COL_PROFILE] = df_users[N2F_COL_PROFILE].apply(
            lambda x: profile_mapping.get(str(x).strip().lower(), x)
        )

    # Normalisation des rôles
    df_users[N2F_COL_ROLE] = (
        df_users[N2F_COL_ROLE].replace(["", "nan", "none"], pd.NA).fillna(DEFAULT_ROLE)
    )
    if role_mapping:
        # Remplacement des valeurs de role par la version française
        df_users[N2F_COL_ROLE] = df_users[N2F_COL_ROLE].apply(
            lambda x: role_mapping.get(str(x).strip().lower(), x)
        )

    return df_users


def build_mapping(df: pd.DataFrame) -> Dict[str, str]:
    """
    Construit un mapping de toutes les valeurs de profile (toutes langues) vers la
    valeur française de manière optimisée.

    Args:
        df: DataFrame contenant les données de mapping

    Returns:
        Dictionnaire de mapping des valeurs vers la valeur française

    Raises:
        ValidationException: Si le DataFrame est vide ou si les colonnes essentielles
            sont manquantes.
    """
    if df.empty:
        return {}

    if COL_NAMES not in df.columns:
        raise ValidationException(
            message="Colonne manquante dans le DataFrame de mapping",
            field=COL_NAMES,
            details=f"La colonne '{COL_NAMES}' est requise.",
        )

    # Crée une copie pour éviter les SettingWithCopyWarning
    df_work = pd.DataFrame(df[[COL_NAMES]].copy())
    df_work = pd.DataFrame(df_work.dropna(subset=[COL_NAMES]))

    # Associe un identifiant unique à chaque ligne originale
    df_work["group_id"] = range(len(df_work))

    # Déplie la liste de dictionnaires en plusieurs lignes
    df_exploded = pd.DataFrame(df_work.explode(COL_NAMES, ignore_index=True))
    df_exploded.reset_index(drop=True, inplace=True)

    # Vérification que COL_NAMES contient des dictionnaires
    dict_check = df_exploded[COL_NAMES].apply(lambda x: isinstance(x, dict))
    if not bool(dict_check.all()):
        raise ValidationException(
            message="Les données dans la colonne names ne sont pas des dictionnaires",
            field=COL_NAMES,
            details="Toutes les valeurs doivent être des dictionnaires valides",
        )

    # Crée des colonnes à partir des dictionnaires
    df_exploded = pd.DataFrame(
        pd.concat(
            [
                df_exploded.drop([COL_NAMES], axis=1),
                df_exploded[COL_NAMES].apply(pd.Series),
            ],
            axis=1,
        )
    )

    # Vérification que COL_VALUE existe après l'explosion
    if COL_VALUE not in df_exploded.columns:
        raise ValidationException(
            message=f"Colonne '{COL_VALUE}' manquante après explosion des données",
            field=COL_VALUE,
            details="La colonne value n'a pas été créée lors de l'explosion",
        )

    df_exploded = pd.DataFrame(df_exploded.dropna(subset=[COL_VALUE]))
    df_exploded = pd.DataFrame(
        df_exploded[df_exploded[COL_VALUE].astype(str).str.strip() != ""]
    )
    df_exploded[COL_VALUE] = df_exploded[COL_VALUE].astype(str).str.strip().str.lower()

    # Trouve la valeur française pour chaque groupe
    fr_values_df = pd.DataFrame(
        df_exploded[df_exploded[COL_CULTURE] == CULTURE_FR].copy()
    )
    fr_values_df["fr_value"] = fr_values_df[COL_VALUE].str.capitalize()
    fr_values = pd.DataFrame(fr_values_df[["group_id", "fr_value"]].copy())

    # Fusionne les valeurs françaises avec toutes les autres valeurs
    df_merged = pd.DataFrame(pd.merge(df_exploded, fr_values, on="group_id"))

    # Crée le mapping final
    mapping = df_merged.set_index(COL_VALUE)["fr_value"].to_dict()

    return mapping
