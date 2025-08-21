def to_bool(val) -> bool:
    """
    Convertit une valeur en booléen.
    Gère les cas courants : '1', 1, 'true', 'True', 'yes', 'on' → True
                           '0', 0, 'false', 'False', 'no', 'off' → False
    """
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    if isinstance(val, str):
        return val.strip().lower() in {'1', 'true', 'yes', 'on'}
    return False