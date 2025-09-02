import os
import pandas as pd

from Iris.Database.IrisConnect import IrisConnect
from agresso.database import execute_query
from core import get_from_cache, set_in_cache


def select(
    base_dir     : str,
    db_user      : str,
    db_password  : str,
    sql_path     : str,
    sql_filename : str,
    prod         : bool,
    cache        : bool = True
) -> pd.DataFrame:
    """
    Lit la requête SQL depuis le fichier,
    établit la connexion à la base Agresso et retourne les utilisateurs sous forme de DataFrame.
    """
    # Construction du chemin vers le fichier SQL à exécuter
    sql_file = os.path.join(
        base_dir, '..', sql_path, sql_filename
    )
    with open(sql_file, encoding='utf-8') as f:
        query = f.read()

    if cache:
        cached = get_from_cache("agresso_select", sql_file, prod, db_user, query)
        if cached is not None:
            return cached

    # Connexion à la base Agresso via IrisConnect
    db = IrisConnect(
        server     = IrisConnect.Server.Production if prod else IrisConnect.Server.Development,
        database   = IrisConnect.Database.AgrProd if prod else IrisConnect.Database.AgrDev,
        odbc_trust = False,
        user       = db_user,
        password   = db_password
    )

    # Exécution de la requête et récupération des résultats
    df = execute_query(db, query)

    if cache:
        set_in_cache(df, "agresso_select", sql_file, prod, db_user, query)

    return df
