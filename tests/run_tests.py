#!/usr/bin/env python3
"""
Script principal pour exécuter tous les tests unitaires du projet N2F.
"""

import unittest
import sys
import os
import time

# Ajouter le répertoire python au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))


def run_all_tests():
    """Exécute tous les tests unitaires."""
    print("N2F Synchronization - Tests Unitaires")
    print("=" * 50)

    # Découvrir et charger tous les tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')

    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.time()

    result = runner.run(suite)

    end_time = time.time()
    duration = end_time - start_time

    # Afficher le résumé
    print("\n" + "=" * 50)
    print("RÉSUMÉ DES TESTS")
    print("=" * 50)
    print(f"Durée totale : {duration:.2f} secondes")
    print(f"Tests réussis : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Échecs : {len(result.failures)}")
    print(f"Erreurs : {len(result.errors)}")
    print(f"Total : {result.testsRun}")

    if result.failures:
        print("\nÉCHECS :")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")

    if result.errors:
        print("\nERREURS :")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")

    # Code de sortie
    if result.failures or result.errors:
        print("\nCertains tests ont échoué !")
        return 1
    else:
        print("\nTous les tests ont réussi !")
        return 0



def run_specific_test(test_module):
    """Exécute un module de test spécifique."""
    print(f"🧪 Exécution du test : {test_module}")
    print("=" * 50)

    # Importer et exécuter le module spécifique
    try:
        module = __import__(test_module)
        suite = unittest.TestLoader().loadTestsFromModule(module)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        if result.failures or result.errors:
            return 1
        else:
            return 0
    except ImportError as e:
        print(f"❌ Impossible d'importer le module {test_module}: {e}")
        return 1


def list_available_tests():
    """Liste tous les modules de test disponibles."""
    print("📋 Modules de test disponibles :")
    print("=" * 30)

    test_files = []
    for file in os.listdir(os.path.dirname(__file__)):
        if file.startswith('test_') and file.endswith('.py'):
            test_files.append(file[:-3])  # Enlever l'extension .py

    for test_file in sorted(test_files):
        print(f"  - {test_file}")

    print(f"\nTotal : {len(test_files)} modules de test")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Exécuter les tests unitaires N2F')
    parser.add_argument('--list', action='store_true', help='Lister tous les tests disponibles')
    parser.add_argument('--module', type=str, help='Exécuter un module de test spécifique')
    parser.add_argument('--verbose', '-v', action='store_true', help='Mode verbeux')

    args = parser.parse_args()

    if args.list:
        list_available_tests()
    elif args.module:
        sys.exit(run_specific_test(args.module))
    else:
        sys.exit(run_all_tests())
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'list':
            list_available_tests()
        elif command == 'run':
            if len(sys.argv) > 2:
                # Exécuter un test spécifique
                test_module = sys.argv[2]
                exit_code = run_specific_test(test_module)
                sys.exit(exit_code)
            else:
                # Exécuter tous les tests
                exit_code = run_all_tests()
                sys.exit(exit_code)
        else:
            print("Usage:")
            print("  python run_tests.py list          # Lister tous les tests")
            print("  python run_tests.py run           # Exécuter tous les tests")
            print("  python run_tests.py run test_name # Exécuter un test spécifique")
            sys.exit(1)
    else:
        # Par défaut, exécuter tous les tests
        exit_code = run_all_tests()
        sys.exit(exit_code)
