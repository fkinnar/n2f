import os
import yaml
import argparse

from typing import Any
from dotenv import load_dotenv

from business.process import synchronize_users


def main() -> None:
    """
    Point d'entrée du script.
    Gère les arguments en ligne de commande, charge les paramètres,
    puis lance la synchronisation selon les options.
    """

    # Chargement des variables d'environnement
    load_dotenv()

    # Gestion des arguments
    args = create_arg_parser().parse_args()

    # Chargement de la configuration YAML
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_filename = args.config + ".yaml"
    config_path = os.path.join(base_dir, '..', config_filename)
    with open(config_path, 'r') as config_file:
        config: dict[str, Any] = yaml.safe_load(config_file)

    # Si aucun paramètre n'est passé, on active create et update par défaut
    if not (args.create or args.delete or args.update):
        args.create = True
        args.update = True

    # Logique métier
    synchronize_users(
        do_create     = args.create,
        do_update     = args.update,
        do_delete     = args.delete,
        base_dir      = base_dir,
        db_user       = os.getenv("AGRESSO_DB_USER"),
        db_password   = os.getenv("AGRESSO_DB_PASSWORD"),
        sql_path      = config["agresso"]["sql-path"],
        sql_filename  = config["agresso"]["sql-filename"],
        base_url      = config["n2f"]["base_urls"],
        client_id     = os.getenv("N2F_CLIENT_ID"),
        client_secret = os.getenv("N2F_CLIENT_SECRET"),
        prod          = config["agresso"]["prod"],
        simulate      = config["n2f"]["simulate"],
        sandbox       = config["n2f"]["sandbox"]
    )


def create_arg_parser() -> argparse.ArgumentParser:
    """
    Crée et retourne un parser d'arguments pour la ligne de commande.
    Permet de spécifier les actions à effectuer (create, delete, update) et le fichier de configuration.
    """

    parser = argparse.ArgumentParser(description="Synchronisation des utilisateurs Agresso <-> N2F")
    parser.add_argument('-c', '--create', action='store_true', help="Créer les utilisateurs manquants dans N2F")
    parser.add_argument('-d', '--delete', action='store_true', help="Supprimer les utilisateurs obsolètes de N2F")
    parser.add_argument('-u', '--update', action='store_true', help="Mettre à jour les utilisateurs existants dans N2F")
    parser.add_argument('-f', '--config', default='dev', help="Nom du fichier de configuration (sans extension .yaml)")
    return parser


# Point d'entrée du script
if __name__ == "__main__":
    main()