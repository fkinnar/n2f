import pandas as pd


def normalize_agresso_users(df_users: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise les utilisateurs Agresso en s'assurant que les colonnes nécessaires sont présentes et correctement formatées.
    """
    df_users = df_users.copy()
    df_users["AdresseEmail"] = df_users["AdresseEmail"].str.lower()
    df_users["Manager"] = df_users["Manager"].str.lower()
    df_users["Structure"] = df_users["Structure"].replace("", pd.NA).fillna("L3")
    df_users["Methode_SSO"] = df_users["Methode_SSO"].replace("Saml", "Sso")

    return df_users


def normalize_n2f_users(df_users: pd.DataFrame, profile_mapping: dict = None, role_mapping: dict = None) -> pd.DataFrame:
    """
    Normalise les utilisateurs N2F en s'assurant que les colonnes nécessaires sont présentes et correctement formatées.
    Remplace les valeurs de 'profile' par leur équivalent français.
    """
    df_users = df_users.copy()
    df_users["mail"] = df_users["mail"].str.lower()

    df_users["profile"] = df_users["profile"].replace("", pd.NA).fillna("Standard")
    if profile_mapping:
        # Remplacement des valeurs de profile par la version française
        df_users["profile"] = df_users["profile"].apply(lambda x: profile_mapping.get(str(x).strip().lower(), x))

    df_users["role"] = df_users["role"].replace("", pd.NA).fillna("Utilisateur")
    if role_mapping:
        # Remplacement des valeurs de role par la version française
        df_users["role"] = df_users["role"].apply(lambda x: role_mapping.get(str(x).strip().lower(), x))

    return df_users


def build_mapping(df: pd.DataFrame) -> dict:
    """
    Construit un mapping de toutes les valeurs de profile (toutes langues) vers la valeur française.
    """
    mapping = {}
    for _, row in df.iterrows():
        names = row["names"]
        fr_value = None
        for name in names:
            if name["culture"] == "fr":
                fr_value = name["value"]
                break
        if fr_value:
            for name in names:
                mapping[name["value"].strip().lower()] = fr_value

    return mapping