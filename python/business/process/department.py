"""
Module de synchronisation pour les départements.

Ce module démontre l'extensibilité du Pattern Registry en ajoutant
un nouveau scope sans modification du code existant.
"""

import pandas as pd
from typing import List, Optional
from core import SyncContext
from core import register_scope


def synchronize_departments(context: SyncContext, sql_filename: str, sql_column_filter: str = "") -> List[pd.DataFrame]:
    """
    Fonction de synchronisation pour les départements.

    Cette fonction est automatiquement découverte et enregistrée
    par le Pattern Registry grâce à son nom qui commence par 'synchronize_'.

    Args:
        context: Contexte de synchronisation
        sql_filename: Nom du fichier SQL à utiliser

    Returns:
        Liste des DataFrames de résultats
    """
    print(f"--- Synchronisation des départements avec {sql_filename} ---")

    # Simulation de la synchronisation
    print("Chargement des départements depuis Agresso...")
    print("Chargement des départements depuis N2F...")
    print("Comparaison et synchronisation...")

    # Retourne un DataFrame vide pour l'exemple
    result_df = pd.DataFrame({
        'department_id': [],
        'department_name': [],
        'status': []
    })

    print("Synchronisation des départements terminée")
    return [result_df]


# Enregistrement automatique du scope dans le Registry
# Cette ligne démontre comment ajouter un nouveau scope sans modifier le code existant
register_scope(
    scope_name="departments",
    sync_function=synchronize_departments,
    sql_filename="get-agresso-n2f-departments.dev.sql",
    entity_type="department",
    display_name="Départements",
    description="Synchronisation des départements Agresso vers N2F",
    enabled=True
)
