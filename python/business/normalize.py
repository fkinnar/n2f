import pandas as pd


def normalize_agresso_users(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise les utilisateurs Agresso en s'assurant que les colonnes nécessaires sont présentes et correctement formatées.
    """
    df = df.copy()
    df["AdresseEmail"] = df["AdresseEmail"].str.lower()
    df["Manager"] = df["Manager"].str.lower()
    df["Structure"] = df["Structure"].replace("", pd.NA).fillna("L3")
    df["Methode_SSO"] = df["Methode_SSO"].replace("Saml", "Sso")

    return df

def normalize_n2f_users(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise les utilisateurs N2F en s'assurant que les colonnes nécessaires sont présentes et correctement formatées.
    """
    df = df.copy()
    df["mail"] = df["mail"].str.lower()
    df["profile"] = df["profile"].replace("", pd.NA).fillna("Standard")
    df["role"] = df["role"].replace("Gebruiker", "Utilisateur")

    return df