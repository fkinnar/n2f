import pandas as pd
from typing import List
from n2f.api_result import ApiResult


def add_api_logging_columns(df: pd.DataFrame, api_results: List[ApiResult]) -> pd.DataFrame:
    """
    Ajoute les colonnes de logging API au DataFrame.

    Args:
        df: DataFrame à enrichir
        api_results: Liste des résultats d'API

    Returns:
        DataFrame enrichi avec les colonnes de logging
    """
    if not api_results:
        return df

    # Ajouter la colonne de succès
    df["api_success"] = [result.success for result in api_results]

    # Ajouter les colonnes détaillées
    for i, result in enumerate(api_results):
        result_dict = result.to_dict()
        for key, value in result_dict.items():
            if key not in df.columns:
                df[key] = None
            df.loc[df.index[i], key] = value

    return df


def export_api_logs(df: pd.DataFrame, filename: str = None) -> str:
    """
    Exporte les logs d'API vers un fichier CSV.

    Args:
        df: DataFrame contenant les logs d'API
        filename: Nom du fichier (optionnel)

    Returns:
        Chemin du fichier exporté
    """
    if filename is None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_logs_{timestamp}.log.csv"

    # Sélectionner seulement les colonnes de logging si elles existent
    logging_columns = [col for col in df.columns if col.startswith("api_")]
    if logging_columns:
        df_export = df[logging_columns].copy()
    else:
        df_export = df.copy()

    df_export.to_csv(filename, index=False)
    return filename
