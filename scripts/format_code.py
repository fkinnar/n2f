#!/usr/bin/env python3
"""
Script pour formater automatiquement le code Python avec Black.
Usage: python scripts/format_code.py [--check]
"""

import subprocess
import sys
import os
from pathlib import Path


def run_black(check_only=False):
    """Exécute Black sur tous les fichiers Python du projet."""
    project_root = Path(__file__).parent.parent
    python_dirs = ["src", "tests", "python", "scripts"]

    # Construire la commande Black
    cmd = ["black"]
    if check_only:
        cmd.extend(["--check", "--diff"])
    cmd.extend(python_dirs)

    print(f"Exécution de: {' '.join(cmd)}")
    print(f"Répertoire de travail: {project_root}")

    try:
        # Changer vers le répertoire du projet
        os.chdir(project_root)

        # Exécuter Black
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            if check_only:
                print("✅ Tous les fichiers sont correctement formatés avec Black !")
            else:
                print("✅ Formatage Black terminé avec succès !")
        else:
            if check_only:
                print(
                    "❌ Certains fichiers ne sont pas formatés selon les standards Black."
                )
                print("Exécutez 'python scripts/format_code.py' pour les formater.")
            else:
                print("❌ Erreur lors du formatage avec Black.")

            if result.stdout:
                print("\nSortie standard:")
                print(result.stdout)
            if result.stderr:
                print("\nErreurs:")
                print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de Black: {e}")
        return False


def main():
    """Fonction principale."""
    check_only = "--check" in sys.argv

    if check_only:
        print("🔍 Vérification du formatage avec Black...")
    else:
        print("🎨 Formatage du code avec Black...")

    success = run_black(check_only)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
