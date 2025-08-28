import pandas as pd

from business.constants import (
    AGRESSO_COL_EMAIL, AGRESSO_COL_MANAGER, AGRESSO_COL_STRUCTURE,
    AGRESSO_COL_SSO_METHOD, N2F_COL_EMAIL, N2F_COL_PROFILE, N2F_COL_ROLE,
    COL_NAMES, COL_CULTURE, COL_VALUE, DEFAULT_STRUCTURE, DEFAULT_PROFILE,
    DEFAULT_ROLE, DEFAULT_SSO_METHOD, CULTURE_FR
)


def normalize_agresso_users(df_users: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise les utilisateurs Agresso en s'assurant que les colonnes nécessaires sont présentes et correctement formatées.
    """
    df_users = df_users.copy()
    df_users[AGRESSO_COL_EMAIL] = df_users[AGRESSO_COL_EMAIL].str.lower()
    df_users[AGRESSO_COL_MANAGER] = df_users[AGRESSO_COL_MANAGER].str.lower()
    df_users[AGRESSO_COL_STRUCTURE] = df_users[AGRESSO_COL_STRUCTURE].replace("", pd.NA).fillna(DEFAULT_STRUCTURE)
    df_users[AGRESSO_COL_SSO_METHOD] = df_users[AGRESSO_COL_SSO_METHOD].replace("Saml", DEFAULT_SSO_METHOD)

    return df_users


def normalize_n2f_users(df_users: pd.DataFrame, profile_mapping: dict = None, role_mapping: dict = None) -> pd.DataFrame:
    """
    Normalise les utilisateurs N2F en s'assurant que les colonnes nécessaires sont présentes et correctement formatées.
    Remplace les valeurs de 'profile' par leur équivalent français.
    """
    df_users = df_users.copy()
    df_users[N2F_COL_EMAIL] = df_users[N2F_COL_EMAIL].str.lower()

    df_users[N2F_COL_PROFILE] = df_users[N2F_COL_PROFILE].replace("", pd.NA).fillna(DEFAULT_PROFILE)
    if profile_mapping:
        # Remplacement des valeurs de profile par la version française
        df_users[N2F_COL_PROFILE] = df_users[N2F_COL_PROFILE].apply(lambda x: profile_mapping.get(str(x).strip().lower(), x))

    df_users[N2F_COL_ROLE] = df_users[N2F_COL_ROLE].replace("", pd.NA).fillna(DEFAULT_ROLE)
    if role_mapping:
        # Remplacement des valeurs de role par la version française
        df_users[N2F_COL_ROLE] = df_users[N2F_COL_ROLE].apply(lambda x: role_mapping.get(str(x).strip().lower(), x))

    return df_users


def build_mapping(df: pd.DataFrame) -> dict:
    """
    Construit un mapping de toutes les valeurs de profile (toutes langues) vers la valeur française.
    """
    mapping = {}
    for _, row in df.iterrows():
        names = row[COL_NAMES]
        fr_value = None
        for name in names:
            if name[COL_CULTURE] == CULTURE_FR:
                fr_value = name[COL_VALUE]
                break
        if fr_value:
            for name in names:
                mapping[name[COL_VALUE].strip().lower()] = fr_value

    return mapping