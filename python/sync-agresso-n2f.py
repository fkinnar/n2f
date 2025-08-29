import argparse
import os
import pandas as pd
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

from helper.context import SyncContext
from core import ConfigLoader, get_registry
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

    # Chargement de la configuration centralisée
    config_loader = ConfigLoader(config_path)
    sync_config = config_loader.load()

    # Initialisation du registry
    registry = get_registry()
    # Auto-découverte pour les nouveaux scopes seulement
    registry.auto_discover_scopes("business.process")

    context = SyncContext(
        args=args,
        config=sync_config,
        base_dir=base_dir,
        db_user=os.getenv("AGRESSO_DB_USER"),
        db_password=os.getenv("AGRESSO_DB_PASSWORD"),
        client_id=os.getenv("N2F_CLIENT_ID"),
        client_secret=os.getenv("N2F_CLIENT_SECRET")
    )

    # Sélection du périmètre à traiter
    selected_scopes = set(args.scope) if hasattr(args, "scope") else {"all"}
    if "all" in selected_scopes:
        # Utilise le registry pour obtenir les scopes disponibles
        registry = get_registry()
        selected_scopes = set(registry.get_enabled_scopes())

    # Boucle de traitement
    all_results = []
    registry = get_registry()
    
    for scope_name in selected_scopes:
        scope_config = registry.get(scope_name)
        if scope_config and scope_config.enabled:
            print(f"--- Starting synchronization for scope : {scope_name} ({scope_config.display_name}) ---")

            results = scope_config.sync_function(
                context=context,
                sql_filename=scope_config.sql_filename
            )

            if results:
                all_results.extend(results)

            print(f"--- End of synchronization for scope : {scope_name} ---")
        else:
            print(f"Warning: Scope '{scope_name}' not found or disabled")

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
    
    # Utilisation des scopes par défaut pour le parser d'arguments
    # Le registry sera initialisé plus tard dans le processus
    scope_choices = ['users', 'projects', 'plates', 'subposts', 'departments', 'all']
    
    parser.add_argument('-s', '--scope', choices=scope_choices, nargs='+', default=['all'], help="Périmètre(s) à synchroniser")
    return parser


if __name__ == "__main__":
    # Forcer l'encodage UTF-8 pour la sortie
    import sys
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    main()
