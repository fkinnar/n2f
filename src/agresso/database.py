import pandas as pd

from Iris.Database.IrisConnect import IrisConnect


def execute_query(db: IrisConnect, query: str) -> pd.DataFrame:
    """
    Exécute la requête SQL passée en paramètre sur la connexion db
    et retourne le résultat sous forme de DataFrame pandas.

    Args:
        db: Connexion à la base de données Iris
        query: Requête SQL à exécuter

    Returns:
        pd.DataFrame: Résultat de la requête sous forme de DataFrame
    """
    df = pd.read_sql_query(query, db.sqlalchemy)
    return df
