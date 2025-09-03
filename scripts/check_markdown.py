#!/usr/bin/env python3
"""
Script pour vérifier automatiquement les erreurs de linting Markdown.
À exécuter après chaque modification de fichiers .md pour s'assurer de la qualité.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path


def find_markdown_files():
    """Trouve tous les fichiers Markdown du projet (excluant env/)."""
    markdown_files = []

    # Chercher dans le répertoire racine et les sous-répertoires
    for root, dirs, files in os.walk("."):
        # Ignorer le répertoire env/
        if "env" in dirs:
            dirs.remove("env")

        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                markdown_files.append(file_path)

    return markdown_files


def check_markdown_files():
    """Vérifie les erreurs de linting dans tous les fichiers Markdown."""
    print("🔍 Vérification des erreurs de linting Markdown")
    print("=" * 50)

    markdown_files = find_markdown_files()

    if not markdown_files:
        print("✅ Aucun fichier Markdown trouvé")
        return True

    print(f"📁 Fichiers Markdown trouvés : {len(markdown_files)}")
    for file_path in markdown_files:
        print(f"   - {file_path}")

    print("\n🔍 Vérification en cours...")

    # Vérifier si markdownlint est disponible
    markdownlint_cmd = shutil.which("markdownlint")
    if not markdownlint_cmd:
        print("❌ markdownlint-cli n'est pas installé ou n'est pas dans le PATH.")
        print("Installez-le avec : npm install -g markdownlint-cli")
        return False

    # Construire la commande markdownlint
    cmd = [markdownlint_cmd] + markdown_files

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            print("✅ Tous les fichiers Markdown passent la validation !")
            return True
        else:
            print("❌ Erreurs de linting détectées :")
            print(result.stdout)
            if result.stderr:
                print("Erreurs :", result.stderr)
            return False

    except Exception as e:
        print(f"❌ Erreur lors de la vérification : {e}")
        return False


def main():
    """Fonction principale."""
    success = check_markdown_files()

    if not success:
        print("\n💡 Conseils pour corriger les erreurs :")
        print(
            "   - Utilisez le script fix_all_markdown.py pour corriger automatiquement"
        )
        print("   - Ou corrigez manuellement selon les messages d'erreur")
        sys.exit(1)
    else:
        print("\n🎉 Tous les fichiers Markdown sont conformes !")


if __name__ == "__main__":
    main()
