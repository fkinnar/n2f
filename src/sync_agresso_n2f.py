import argparse
import os
from pathlib import Path
from core import SyncOrchestrator
from core.config import ConfigLoader


def main() -> None:
    """
    Point d'entrée principal du script de synchronisation Agresso-N2F.

    Ce script utilise l'orchestrateur pour coordonner la synchronisation complète
    entre les systèmes Agresso et N2F.

    Workflow :
    1. Parsing des arguments de ligne de commande
    2. Chargement de la configuration et des variables d'environnement
    3. Validation des variables d'environnement requises
    4. Exécution de l'orchestrateur
    5. Gestion des erreurs globales

    Raises:
        FileNotFoundError: Si le fichier de configuration n'existe pas
        ValueError: Si les variables d'environnement requises sont manquantes
        Exception: Pour toute autre erreur non gérée

    Example:
        >>> python sync-agresso-n2f.py --scope users --create --update
        >>> python sync-agresso-n2f.py --config prod --scope all
    """
    args = create_arg_parser().parse_args()

    # Si aucun paramètre n'est passé, on active create et update par défaut
    if not (args.create or args.delete or args.update):
        args.create = True
        args.update = True

    # Construction du chemin de configuration
    base_dir = Path(__file__).resolve().parent
    config_filename = f"{args.config}.yaml"
    config_path = base_dir.parent / config_filename

    # Chargement de la configuration pour déterminer si on est en sandbox
    config_loader = ConfigLoader(config_path)
    sync_config = config_loader.load()

    # Si --skip-dotenv-loading est utilisé, forcer le mode non-sandbox
    if args.skip_dotenv_loading:
        sync_config.api.sandbox = False

    # Chargement des variables d'environnement seulement si en mode sandbox
    if sync_config.api.sandbox:
        from dotenv import load_dotenv

        load_dotenv()
        print("Environment variables loaded from .env file (sandbox mode)")

    # Validation des variables d'environnement requises
    validate_environment_variables()

    # Création et exécution de l'orchestrateur
    orchestrator = SyncOrchestrator(config_path, args)
    orchestrator.run()


def validate_environment_variables() -> None:
    """
    Valide que toutes les variables d'environnement requises sont présentes.

    Raises:
        ValueError: Si une variable d'environnement requise est manquante
    """
    required_vars = [
        "AGRESSO_DB_USER",
        "AGRESSO_DB_PASSWORD",
        "N2F_CLIENT_ID",
        "N2F_CLIENT_SECRET",
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        print(f"ERROR: {error_msg}")
        print("Please ensure these variables are set in your environment or .env file")
        raise ValueError(error_msg)

    print("All required environment variables are present")


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
    parser.add_argument(
        "-c",
        "--create",
        action="store_true",
        help="Créer les éléments manquants dans N2F",
    )
    parser.add_argument(
        "-d",
        "--delete",
        action="store_true",
        help="Supprimer les éléments obsolètes de N2F",
    )
    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="Mettre à jour les éléments existants dans N2F",
    )
    parser.add_argument(
        "-f",
        "--config",
        default="dev",
        help="Nom du fichier de configuration (sans .yaml)",
    )

    # Utilisation des scopes par défaut pour le parser d'arguments
    # Le registry sera initialisé plus tard dans le processus
    scope_choices = ["users", "projects", "plates", "subposts", "all"]

    parser.add_argument(
        "-s",
        "--scope",
        choices=scope_choices,
        nargs="+",
        default=["all"],
        help="Périmètre(s) à synchroniser",
    )

    # Arguments de cache
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Vider complètement le cache avant la synchronisation",
    )
    parser.add_argument(
        "--invalidate-cache",
        nargs="+",
        metavar="FUNCTION",
        help="Invalider des entrées spécifiques du cache (ex: get_users get_companies)",
    )
    parser.add_argument(
        "--skip-dotenv-loading",
        action="store_true",
        help=(
            "Désactiver le chargement du fichier .env, même si le mode sandbox est "
            "configuré dans le YAML. Utile pour tester le comportement de production "
            "des dépendances."
        ),
    )

    return parser


if __name__ == "__main__":
    main()
