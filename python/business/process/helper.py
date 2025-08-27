import pandas as pd


def reporting(
    result_df      : pd.DataFrame,
    empty_message  : str,
    update_message : str,
    status_col     : str
) -> None:
    """
    Génère un rapport à partir du DataFrame de résultats.
    Affiche le nombre de succès et d'échecs si une colonne de statut est fournie.
    """
    if result_df.empty:
        print(empty_message)
    else:
        print(update_message + " :")
        if status_col and status_col in result_df.columns:
            nb_success = result_df[status_col].sum()
            nb_total = len(result_df)
            nb_failed = nb_total - nb_success
            print(f"  Succès : {nb_success} / {nb_total}")
            print(f"  Échecs : {nb_failed} / {nb_total}")
        else:
            print(f"  Total : {len(result_df)}")
