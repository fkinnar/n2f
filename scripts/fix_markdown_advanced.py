#!/usr/bin/env python3
"""
Script avancé de correction des fichiers Markdown.

Ce script corrige automatiquement les problèmes de numérotation
des listes ordonnées qui ne peuvent pas être résolus par markdownlint.
"""

import re
import subprocess
from pathlib import Path


def _fix_ordered_lists(file_path):
    """Corrige les listes ordonnées dans un fichier Markdown."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        fixed_lines = []
        current_list_number = 1
        in_list = False

        for line in lines:
            # Détecter si c'est une ligne de liste ordonnée
            match = re.match(r"^(\s*)\d+\.\s+(.*)", line)
            if match:
                indent = match.group(1)
                content = match.group(2)

                # Si c'est le début d'une nouvelle liste (commence par "1.")
                if match.group(0).strip().startswith("1."):
                    current_list_number = 1
                    in_list = True

                # Créer la ligne corrigée
                corrected_line = f"{indent}{current_list_number}. {content}\n"
                fixed_lines.append(corrected_line)
                current_list_number += 1
            else:
                # Si ce n'est pas une ligne de liste, réinitialiser le compteur
                if in_list:
                    in_list = False
                    current_list_number = 1
                fixed_lines.append(line)

        # Écrire le fichier corrigé
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(fixed_lines)

        print(f"✅ {file_path.name} corrigé avec succès")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de la correction de {file_path.name}: {e}")
        return False


def _find_markdown_files():
    """Trouve tous les fichiers Markdown du projet."""
    project_root = Path(__file__).parent.parent
    markdown_files = [
        f
        for f in project_root.rglob("*.md")
        if not any(
            part.startswith(".") or part in ["env", "venv", "__pycache__"]
            for part in f.parts
        )
    ]
    return markdown_files


def _format_files_with_mdformat(markdown_files):
    """Formate les fichiers avec mdformat."""
    print("\n" + "=" * 60)
    print("ÉTAPE 2: Formatage avec mdformat")
    print("=" * 60)

    for file in markdown_files:
        print(f"📝 Formatage de {file.name}...")
        try:
            result = subprocess.run(
                f'mdformat "{file}" --wrap=88',
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                print(f"✅ {file.name} formaté avec succès")
            else:
                print(f"⚠️  {file.name} - Problèmes de formatage")
        except Exception as e:
            print(f"❌ Erreur lors du formatage de {file.name}: {e}")


def _final_verification(markdown_files):
    """Vérification finale avec markdownlint."""
    print("\n" + "=" * 60)
    print("ÉTAPE 3: Vérification finale avec markdownlint")
    print("=" * 60)

    print("\n🔍 Vérification finale de tous les fichiers...")
    all_files = " ".join(f'"{f}"' for f in markdown_files)

    try:
        result = subprocess.run(
            f"markdownlint {all_files}",
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            print("\n🎉 Tous les fichiers Markdown sont maintenant conformes !")
        else:
            print("\n⚠️  Certains fichiers Markdown ont encore des problèmes.")
            print("   Sortie markdownlint:")
            if result.stderr:
                print(result.stderr)

            # Afficher un résumé des problèmes restants
            print("\n📊 Résumé des problèmes restants:")
            for file in markdown_files:
                try:
                    check_result = subprocess.run(
                        f'markdownlint "{file}"',
                        shell=True,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    if check_result.returncode == 0:
                        print(f"✅ {file.name} - Aucun problème")
                    else:
                        print(f"❌ {file.name} - Problèmes détectés")
                except Exception as e:
                    print(f"❌ {file.name} - Erreur de vérification: {e}")

    except Exception as e:
        print(f"❌ Erreur lors de la vérification finale: {e}")


def main():
    """Fonction principale."""
    print("🚀 Script avancé de correction des fichiers Markdown")
    print("=" * 60)

    # Trouver tous les fichiers Markdown du projet
    markdown_files = _find_markdown_files()
    print(f"\n📁 {len(markdown_files)} fichiers Markdown trouvés")

    if not markdown_files:
        print("❌ Aucun fichier Markdown trouvé")
        return

    # Étape 1: Correction automatique des listes ordonnées
    print("\n" + "=" * 60)
    print("ÉTAPE 1: Correction automatique des listes ordonnées")
    print("=" * 60)

    for file in markdown_files:
        _fix_ordered_lists(file)

    # Étape 2: Formatage avec mdformat
    _format_files_with_mdformat(markdown_files)

    # Étape 3: Vérification finale avec markdownlint
    _final_verification(markdown_files)

    print("\n" + "=" * 60)
    print("✅ Script terminé !")
    print("=" * 60)


if __name__ == "__main__":
    main()
