import pandas as pd


def to_bool(val) -> bool:
    """
    Convertit une valeur en booléen.
    Gère les cas courants : '1', 1, 'true', 'True', 'yes', 'y', 'on' → True
                           '0', 0, 'false', 'False', 'no', 'n', 'off' → False
    """
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    if isinstance(val, str):
        val_lower = val.strip().lower()
        return val_lower in {"1", "true", "yes", "y", "on"}
    return False


def normalize_date_for_payload(value):
    """
    Normalise une date pour l'API: renvoie None si vide/NaN
    et si la date représente 31/12/2099 (sentinelle d'illimité).
    Accepte datetime/date ou chaîne (jour/mois/année OK).
    Retourne une chaîne ISO formatée (YYYY-MM-DD) ou None.
    """
    if pd.isna(value) or value is None:
        return None
    try:
        dt = pd.to_datetime(value, dayfirst=True, errors="coerce")
    except Exception:
        dt = None
    if dt is not None and not pd.isna(dt):
        # Vérifier si c'est la date sentinelle
        if dt.date().strftime("%Y-%m-%d") == "2099-12-31":
            return None
        # Retourner la date au format ISO (YYYY-MM-DD)
        return dt.date().strftime("%Y-%m-%d") + "T00:00:00Z"
    return None
