#!/usr/bin/env python3
"""
Script pour nettoyer les fichiers temporaires de couverture.
"""

import os
import glob
import shutil


def clean_coverage_files():
    """Nettoie tous les fichiers temporaires de couverture."""
    print("🧹 Nettoyage des fichiers de couverture...")

    # Fichiers à supprimer
    files_to_remove = [".coverage", "coverage.xml", "htmlcov", "coverage_html"]

    # Patterns pour les fichiers .coverage.*
    coverage_patterns = [".coverage.*", "coverage.*"]

    removed_count = 0

    # Supprimer les fichiers spécifiques
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
                print(f"  📁 Supprimé le dossier : {file_path}")
            else:
                os.remove(file_path)
                print(f"  📄 Supprimé le fichier : {file_path}")
            removed_count += 1

    # Supprimer les fichiers avec patterns
    for pattern in coverage_patterns:
        for file_path in glob.glob(pattern):
            try:
                os.remove(file_path)
                print(f"  📄 Supprimé le fichier : {file_path}")
                removed_count += 1
            except Exception as e:
                print(f"  ⚠️  Erreur lors de la suppression de {file_path}: {e}")

    if removed_count == 0:
        print("  ✅ Aucun fichier de couverture à nettoyer")
    else:
        print(f"  ✅ {removed_count} fichier(s) nettoyé(s)")


if __name__ == "__main__":
    clean_coverage_files()
