import yaml
import argparse
import os
import pandas as pd
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
from n2f.process.helper import export_api_logs

def main() -> None:
    """
    Point d'entrée principal du script de synchronisation Agresso-N2F.

    Ce script orchestre la synchronisation complète entre les systèmes Agresso et N2F.
    Il gère la configuration, les arguments de ligne de commande, et coordonne
    l'exécution des synchronisations pour chaque scope sélectionné.

    Workflow :
    1. Chargement des variables d'environnement
    2. Parsing des arguments de ligne de commande
    3. Chargement de la configuration YAML
    4. Construction du contexte de synchronisation
    5. Exécution des synchronisations par scope
    6. Export et affichage des logs d'API

    Raises:
        FileNotFoundError: Si le fichier de configuration n'existe pas
        KeyError: Si des clés de configuration sont manquantes
        Exception: Pour toute autre erreur non gérée

    Example:
        >>> python sync-agresso-n2f.py --scope users --create --update
        >>> python sync-agresso-n2f.py --config prod --scope all
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
    all_results = []
    for scope_name in selected_scopes:
        if scope_name in scope_map:
            sync_function, sql_filename = scope_map[scope_name]

            print(f"--- Starting synchronization for scope : {scope_name} ---")

            results = sync_function(
                context=context,
                sql_filename=sql_filename
            )

            if results:
                all_results.extend(results)

            print(f"--- End of synchronization for scope : {scope_name} ---")

    # Export des logs d'API si des résultats sont disponibles
    if all_results:
        print("\n--- API Logs Export ---")
        try:
            # Combiner tous les résultats
            combined_df = pd.concat(all_results, ignore_index=True)

            # Exporter les logs
            log_filename = export_api_logs(combined_df)
            print(f"API logs exported to : {log_filename}")

            # Afficher un résumé des erreurs
            if "api_success" in combined_df.columns:
                success_count = combined_df["api_success"].sum()
                total_count = len(combined_df)
                error_count = total_count - success_count

                print(f"\nAPI Operations Summary :")
                print(f"  - Success : {success_count}/{total_count}")
                print(f"  - Errors : {error_count}/{total_count}")

                if error_count > 0:
                    print(f"\nError Details :")
                    errors_df = combined_df[~combined_df["api_success"]]
                    for _, row in errors_df.iterrows():
                        print(f"  - {row.get('api_message', 'Unknown error')}")
                        if 'api_error_details' in row and pd.notna(row['api_error_details']):
                            print(f"    Details : {row['api_error_details']}")

        except Exception as e:
            print(f"Error during logs export : {e}")


def create_arg_parser() -> argparse.ArgumentParser:
    """
    Crée et configure le parser d'arguments pour la ligne de commande.

    Définit tous les arguments disponibles pour contrôler le comportement
    de la synchronisation : actions à effectuer, scopes à traiter,
    configuration à utiliser.

    Returns:
        argparse.ArgumentParser: Parser configuré avec tous les arguments

    Example:
        >>> parser = create_arg_parser()
        >>> args = parser.parse_args(['--create', '--scope', 'users'])
    """
    parser = argparse.ArgumentParser(description="Synchronisation Agresso <-> N2F")
    parser.add_argument('-c', '--create', action='store_true', help="Créer les éléments manquants dans N2F")
    parser.add_argument('-d', '--delete', action='store_true', help="Supprimer les éléments obsolètes de N2F")
    parser.add_argument('-u', '--update', action='store_true', help="Mettre à jour les éléments existants dans N2F")
    parser.add_argument('-f', '--config', default='dev', help="Nom du fichier de configuration (sans .yaml)")
    parser.add_argument('-s', '--scope', choices=['users', 'projects', 'plates', 'subposts', 'all'], nargs='+', default=['all'], help="Périmètre(s) à synchroniser")
    return parser


if __name__ == "__main__":
    # Forcer l'encodage UTF-8 pour la sortie
    import sys
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    main()
