#!/usr/bin/env python3
"""
Script de vérification des fichiers Markdown.

Ce script vérifie rapidement la qualité de tous les fichiers Markdown
du projet sans les modifier.
"""

import subprocess
import sys
from pathlib import Path


def check_markdown_file(file_path):
    """Vérifie un fichier Markdown avec markdownlint."""
    try:
        result = subprocess.run(
            f'markdownlint "{file_path}"',
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            print(f"✅ {file_path.name} - Aucun problème")
            return True
        else:
            print(f"❌ {file_path.name} - Problèmes détectés:")
            if result.stderr:
                print(f"   {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {file_path.name} - Erreur: {e}")
        return False


def main():
    """Fonction principale."""
    print("🔍 Vérification des fichiers Markdown")
    print("=" * 50)

    # Trouver tous les fichiers Markdown
    project_root = Path(__file__).parent.parent
    markdown_files = [
        f
        for f in project_root.rglob("*.md")
        if not any(
            part.startswith(".") or part in ["env", "venv", "__pycache__"]
            for part in f.parts
        )
    ]

    print(f"\n📁 {len(markdown_files)} fichiers Markdown trouvés")

    if not markdown_files:
        print("❌ Aucun fichier Markdown trouvé")
        return

    # Vérifier chaque fichier
    print("\n🔍 Vérification en cours...")
    print("-" * 50)

    total_files = len(markdown_files)
    valid_files = 0

    for file in markdown_files:

        if check_markdown_file(file):
            valid_files += 1

    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ")
    print("=" * 50)
    print(f"Total de fichiers: {total_files}")
    print(f"Fichiers valides: {valid_files}")
    print(f"Fichiers avec problèmes: {total_files - valid_files}")

    if valid_files == total_files:
        print("\n🎉 Tous les fichiers Markdown sont conformes !")
    else:
        print(f"\n⚠️  {total_files - valid_files} fichier(s) ont des problèmes.")
        print("   Exécutez 'python scripts/fix_markdown.py' pour les corriger.")


if __name__ == "__main__":
    main()
