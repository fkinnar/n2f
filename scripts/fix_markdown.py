#!/usr/bin/env python3
"""
Script de correction automatique des fichiers Markdown.

Ce script utilise les hooks pre-commit pour corriger automatiquement
tous les fichiers Markdown du projet.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Exécute une commande et affiche le résultat."""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=False
        )

        if result.returncode == 0:
            print(f"✅ {description} - Succès")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"⚠️  {description} - Avertissements/Modifications")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)

        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} - Erreur: {e}")
        return False


def find_markdown_files():
    """Trouve tous les fichiers Markdown du projet."""
    project_root = Path(__file__).parent.parent
    markdown_files = list(project_root.rglob("*.md"))

    # Filtrer les fichiers dans les dossiers d'environnement
    filtered_files = [
        f
        for f in markdown_files
        if not any(
            part.startswith(".") or part in ["env", "venv", "__pycache__"]
            for part in f.parts
        )
    ]

    return filtered_files


def main():
    """Fonction principale."""
    print("🚀 Script de correction automatique des fichiers Markdown")
    print("=" * 60)

    # Trouver tous les fichiers Markdown
    markdown_files = find_markdown_files()
    print(f"\n📁 {len(markdown_files)} fichiers Markdown trouvés:")
    for file in markdown_files:
        print(f"   - {file.relative_to(Path.cwd())}")

    if not markdown_files:
        print("❌ Aucun fichier Markdown trouvé")
        return

    # Étape 1: Formater avec mdformat
    print("\n" + "=" * 60)
    print("ÉTAPE 1: Formatage automatique avec mdformat")
    print("=" * 60)

    for file in markdown_files:
        relative_path = file.relative_to(Path.cwd())
        print(f"\n📝 Formatage de {relative_path}...")

        # Utiliser mdformat directement
        success = run_command(
            f'mdformat "{file}" --wrap=88', f"Formatage de {relative_path}"
        )

        if success:
            print(f"✅ {relative_path} formaté avec succès")
        else:
            print(f"⚠️  {relative_path} - Problèmes détectés")

    # Étape 2: Vérifier avec markdownlint
    print("\n" + "=" * 60)
    print("ÉTAPE 2: Vérification avec markdownlint")
    print("=" * 60)

    for file in markdown_files:
        relative_path = file.relative_to(Path.cwd())
        print(f"\n🔍 Vérification de {relative_path}...")

        # Utiliser markdownlint directement
        success = run_command(
            f'markdownlint "{file}" --fix', f"Vérification de {relative_path}"
        )

        if success:
            print(f"✅ {relative_path} - Aucun problème détecté")
        else:
            print(
                f"⚠️  {relative_path} - Problèmes détectés et corrigés automatiquement"
            )

    # Étape 3: Vérification finale
    print("\n" + "=" * 60)
    print("ÉTAPE 3: Vérification finale")
    print("=" * 60)

    print("\n🔍 Vérification finale de tous les fichiers...")
    all_files = " ".join(f'"{f}"' for f in markdown_files)

    final_check = run_command(f"markdownlint {all_files}", "Vérification finale")

    if final_check:
        print("\n🎉 Tous les fichiers Markdown sont maintenant conformes !")
    else:
        print("\n⚠️  Certains fichiers Markdown ont encore des problèmes.")
        print("   Exécutez ce script à nouveau pour les corriger.")

    print("\n" + "=" * 60)
    print("✅ Script terminé !")
    print("=" * 60)


if __name__ == "__main__":
    main()
