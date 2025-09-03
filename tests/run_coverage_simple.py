#!/usr / bin/env python3
"""
Script simplifié pour analyser la couverture des tests unitaires du projet N2F.
"""

import coverage
import unittest
import sys
import os
import time

# Ajouter le répertoire python au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def run_coverage_analysis():
    """Exécute l'analyse de couverture des tests."""
    print("N2F Synchronization - Analyse de Couverture des Tests")
    print("=" * 60)

    # Initialiser coverage
    cov = coverage.Coverage(
        source=["src"],
        omit=[
            "*/tests/*",
            "*/__pycache__/*",
            "*/site - packages/*",
            "*/env/*",
            "*/venv/*",
            "*/example*.py",
            "*/_example*.py",
            "*_example.py",
            "*/sync_example.py",
            "*/test_*.py",
        ],
    )

    # Démarrer la collecte de données
    cov.start()

    # Découvrir et exécuter tous les tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=1)
    start_time = time.time()

    result = runner.run(suite)

    end_time = time.time()
    duration = end_time - start_time

    # Arrêter la collecte et générer le rapport
    cov.stop()
    cov.save()

    # Afficher le rapport de couverture
    print("\n" + "=" * 60)
    print("RAPPORT DE COUVERTURE")
    print("=" * 60)

    # Rapport détaillé
    cov.report(show_missing=True, skip_covered=False)

    # Analyser les fichiers avec faible couverture
    print("\nFichiers avec couverture < 80%:")
    print("-" * 40)

    low_coverage_files = []

    # Obtenir les données de couverture
    data = cov.get_data()

    for filename in data.measured_files():
        if filename.startswith("src/"):
            # Obtenir les statistiques pour ce fichier
            file_coverage = data.get_file_coverage(filename)
            if file_coverage:
                total_lines = len(file_coverage)
                covered_lines = sum(1 for line in file_coverage if line > 0)
                file_percentage = (
                    (covered_lines / total_lines * 100) if total_lines > 0 else 0
                )

                if file_percentage < 80:
                    low_coverage_files.append(
                        (filename, file_percentage, total_lines, covered_lines)
                    )

    if low_coverage_files:
        for filename, percentage, total, covered in sorted(
            low_coverage_files, key=lambda x: x[1]
        ):
            print(f"  {filename}: {percentage:.1f}% ({covered}/{total} lignes)")
    else:
        print("  Aucun fichier avec couverture < 80% trouvé.")

    # Résumé des tests
    print("\nRésumé des tests:")
    print(f"  Durée totale : {duration:.2f} secondes")
    print(
        f"  Tests réussis : {result.testsRun - len(result.failures) - len(result.errors)}"
    )
    print(f"  Échecs : {len(result.failures)}")
    print(f"  Erreurs : {len(result.errors)}")
    print(f"  Total : {result.testsRun}")

    # Générer un rapport HTML
    cov.html_report(directory="coverage_html")
    print("\nRapport HTML généré dans le dossier 'coverage_html'")

    return result.failures, result.errors


def analyze_missing_coverage():
    """Analyse détaillée des lignes manquantes."""
    print("\n" + "=" * 60)
    print("ANALYSE DÉTAILLÉE DES LIGNES MANQUANTES")
    print("=" * 60)

    cov = coverage.Coverage()
    cov.load()

    missing_by_file = {}

    data = cov.get_data()

    for filename in data.measured_files():
        if filename.startswith("src/"):
            file_coverage = data.get_file_coverage(filename)
            if file_coverage:
                missing_lines = [
                    i + 1 for i, line in enumerate(file_coverage) if line == 0
                ]
                if missing_lines:
                    missing_by_file[filename] = missing_lines

    if missing_by_file:
        for filename in sorted(missing_by_file.keys()):
            print(f"\n{filename}:")
            missing_lines = missing_by_file[filename]

            # Lire le fichier pour afficher les lignes manquantes
            try:
                with open(filename, "r", encoding="utf - 8") as f:
                    lines = f.readlines()

                print(f"  Lignes non couvertes : {missing_lines}")
                print("  Extrait des lignes manquantes :")
                for line_num in missing_lines[:10]:  # Limiter à 10 lignes
                    if 0 < line_num <= len(lines):
                        line_content = lines[line_num - 1].strip()
                        if line_content:
                            print(f"    Ligne {line_num}: {line_content}")

                if len(missing_lines) > 10:
                    print(f"    ... et {len(missing_lines) - 10} autres lignes")

            except Exception as e:
                print(f"    Erreur lors de la lecture du fichier : {e}")
    else:
        print("Aucune ligne manquante trouvée.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyser la couverture des tests unitaires N2F"
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Afficher l'analyse détaillée des lignes manquantes",
    )
    parser.add_argument("--html", action="store_true", help="Générer le rapport HTML")

    args = parser.parse_args()

    try:
        failures, errors = run_coverage_analysis()

        if args.detailed:
            analyze_missing_coverage()

        # Code de sortie
        if failures or errors:
            print("\n⚠️  Certains tests ont échoué !")
            sys.exit(1)
        else:
            print("\n✅ Tous les tests ont réussi !")
            sys.exit(0)

    except Exception as e:
        print(f"❌ Erreur lors de l'analyse de couverture : {e}")
        sys.exit(1)
