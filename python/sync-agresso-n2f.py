import yaml
import argparse
import os
from pathlib import Path
from typing import Any, Callable
from dotenv import load_dotenv

from helper.context import SyncContext
from business.process import (
    synchronize_users,
    synchronize_projects,
    synchronize_plates,
    synchronize_subposts
)

def main() -> None:
    """
    Point d'entrée du script.
    Gère les arguments, charge la configuration dans un contexte,
    puis lance la synchronisation pour chaque périmètre sélectionné.
    """
    load_dotenv()
    args = create_arg_parser().parse_args()

    # Si aucun paramètre n'est passé, on active create et update par défaut
    if not (args.create or args.delete or args.update):
        args.create = True
        args.update = True

    # Construction du contexte
    base_dir = Path(__file__).resolve().parent
    config_filename = f"{args.config}.yaml"
    config_path = base_dir.parent / config_filename
    
    with config_path.open('r') as config_file:
        config = yaml.safe_load(config_file)

    context = SyncContext(
        args=args,
        config=config,
        base_dir=base_dir,
        db_user=os.getenv("AGRESSO_DB_USER"),
        db_password=os.getenv("AGRESSO_DB_PASSWORD"),
        client_id=os.getenv("N2F_CLIENT_ID"),
        client_secret=os.getenv("N2F_CLIENT_SECRET")
    )

    # Mapping des périmètres (scopes) à leurs fonctions et fichiers SQL
    scope_map: dict[str, tuple[Callable, str]] = {
        "users": (synchronize_users, context.config["agresso"]["sql-filename-users"]),
        "projects": (synchronize_projects, context.config["agresso"]["sql-filename-customaxes"]),
        "plates": (synchronize_plates, context.config["agresso"]["sql-filename-customaxes"]),
        "subposts": (synchronize_subposts, context.config["agresso"]["sql-filename-customaxes"]),
    }

    # Sélection du périmètre à traiter
    selected_scopes = set(args.scope) if hasattr(args, "scope") else {"all"}
    if "all" in selected_scopes:
        selected_scopes = set(scope_map.keys())

    # Boucle de traitement
    for scope_name in selected_scopes:
        if scope_name in scope_map:
            sync_function, sql_filename = scope_map[scope_name]
            
            print(f"--- Début de la synchronisation pour le périmètre : {scope_name} ---")
            
            sync_function(
                context=context,
                sql_filename=sql_filename
            )
            
            print(f"--- Fin de la synchronisation pour le périmètre : {scope_name} ---\
")


def create_arg_parser() -> argparse.ArgumentParser:
    """Crée et retourne un parser d'arguments pour la ligne de commande."""
    parser = argparse.ArgumentParser(description="Synchronisation Agresso <-> N2F")
    parser.add_argument('-c', '--create', action='store_true', help="Créer les éléments manquants dans N2F")
    parser.add_argument('-d', '--delete', action='store_true', help="Supprimer les éléments obsolètes de N2F")
    parser.add_argument('-u', '--update', action='store_true', help="Mettre à jour les éléments existants dans N2F")
    parser.add_argument('-f', '--config', default='dev', help="Nom du fichier de configuration (sans .yaml)")
    parser.add_argument('-s', '--scope', choices=['users', 'projects', 'plates', 'subposts', 'all'], nargs='+', default=['all'], help="Périmètre(s) à synchroniser")
    return parser


if __name__ == "__main__":
    main()
