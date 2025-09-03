import pandas as pd
from typing import Dict, Any, Optional

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


def normalize_agresso_users(df_users: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise les utilisateurs Agresso en s'assurant que les colonnes nécessaires sont présentes et correctement formatées.

    Args:
        df_users: DataFrame contenant les utilisateurs Agresso

    Returns:
        DataFrame normalisé

    Raises:
        ValueError: Si le DataFrame est vide ou si les colonnes essentielles sont manquantes
    """
    if df_users.empty:
        raise ValueError("Le DataFrame des utilisateurs Agresso ne peut pas être vide")

    # Vérification des colonnes essentielles
    required_columns = [
        AGRESSO_COL_EMAIL,
        AGRESSO_COL_MANAGER,
        AGRESSO_COL_STRUCTURE,
        AGRESSO_COL_SSO_METHOD,
    ]
    missing_columns = [col for col in required_columns if col not in df_users.columns]
    if missing_columns:
        raise ValueError(
            f"Colonnes manquantes dans le DataFrame Agresso: {missing_columns}"
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

    # Normalisation des structures (remplacement des valeurs vides par la valeur par défaut)
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
    Normalise les utilisateurs N2F en s'assurant que les colonnes nécessaires sont présentes et correctement formatées.
    Remplace les valeurs de 'profile' par leur équivalent français.

    Args:
        df_users: DataFrame contenant les utilisateurs N2F
        profile_mapping: Mapping optionnel pour les profils
        role_mapping: Mapping optionnel pour les rôles

    Returns:
        DataFrame normalisé

    Raises:
        ValueError: Si le DataFrame est vide ou si les colonnes essentielles sont manquantes
    """
    if df_users.empty:
        raise ValueError("Le DataFrame des utilisateurs N2F ne peut pas être vide")

    # Vérification des colonnes essentielles
    required_columns = [N2F_COL_EMAIL, N2F_COL_PROFILE, N2F_COL_ROLE]
    missing_columns = [col for col in required_columns if col not in df_users.columns]
    if missing_columns:
        raise ValueError(
            f"Colonnes manquantes dans le DataFrame N2F: {missing_columns}"
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
    Construit un mapping de toutes les valeurs de profile (toutes langues) vers la valeur française.

    Args:
        df: DataFrame contenant les données de mapping

    Returns:
        Dictionnaire de mapping des valeurs vers la valeur française

    Raises:
        ValueError: Si le DataFrame est vide ou si les colonnes essentielles sont manquantes
    """
    if df.empty:
        return {}

    # Vérification de la colonne essentielle
    if COL_NAMES not in df.columns:
        raise ValueError(f"Colonne manquante dans le DataFrame de mapping: {COL_NAMES}")

    mapping: Dict[str, str] = {}
    for _, row in df.iterrows():
        names = row[COL_NAMES]
        if not names:  # Skip si la liste des noms est vide
            continue

        fr_value: Optional[str] = None
        # Chercher la valeur française
        for name in names:
            if name.get(COL_CULTURE) == CULTURE_FR:
                fr_value = name.get(COL_VALUE, "").strip()
                break

        # Si on a trouvé une valeur française, créer le mapping
        if fr_value:
            for name in names:
                nl_value = name.get(COL_VALUE, "").strip()
                if nl_value:  # Ne pas mapper les valeurs vides
                    mapping[nl_value.lower()] = fr_value

    return mapping
