#!/usr/bin/env python3
"""
Script pour analyser la présence et la qualité des type hints dans le projet.
Usage: python scripts/analyze_type_hints.py
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set, Any
from collections import defaultdict


class TypeHintAnalyzer(ast.NodeVisitor):
    """Analyseur AST pour détecter les type hints dans le code Python."""

    def __init__(self):
        self.functions = []
        self.classes = []
        self.imports = []
        self.missing_type_hints = []
        self.partial_type_hints = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Analyse une définition de fonction."""
        func_info = {
            "name": node.name,
            "line": node.lineno,
            "args": [],
            "returns": None,
            "has_return_annotation": node.returns is not None,
            "missing_arg_annotations": [],
            "total_args": 0,
        }

        # Analyser les arguments
        for arg in node.args.args:
            func_info["total_args"] += 1
            if arg.annotation is None:
                func_info["missing_arg_annotations"].append(arg.arg)
            else:
                func_info["args"].append((arg.arg, arg.annotation))

        # Analyser le type de retour
        if node.returns:
            func_info["returns"] = node.returns

        # Classifier la fonction
        if (
            not func_info["has_return_annotation"]
            and func_info["missing_arg_annotations"]
        ):
            self.missing_type_hints.append(func_info)
        elif (
            not func_info["has_return_annotation"]
            or func_info["missing_arg_annotations"]
        ):
            self.partial_type_hints.append(func_info)
        else:
            func_info["complete"] = True

        self.functions.append(func_info)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Analyse une définition de fonction asynchrone."""
        # Traiter comme une fonction normale
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Analyse une définition de classe."""
        class_info = {
            "name": node.name,
            "line": node.lineno,
            "methods": [],
            "has_type_hints": False,
        }

        # Analyser les méthodes de la classe
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = {
                    "name": item.name,
                    "line": item.lineno,
                    "has_args_annotations": all(
                        arg.annotation is not None for arg in item.args.args
                    ),
                    "has_return_annotation": item.returns is not None,
                }
                class_info["methods"].append(method_info)

        # Déterminer si la classe a des type hints
        class_info["has_type_hints"] = any(
            method["has_args_annotations"] or method["has_return_annotation"]
            for method in class_info["methods"]
        )

        self.classes.append(class_info)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Analyse les imports."""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Analyse les imports from."""
        module = node.module or ""
        for alias in node.names:
            self.imports.append(f"{module}.{alias.name}")
        self.generic_visit(node)


def analyze_file(file_path: Path) -> Dict[str, Any]:
    """Analyse un fichier Python pour ses type hints."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        analyzer = TypeHintAnalyzer()
        analyzer.visit(tree)

        return {
            "file": str(file_path),
            "functions": analyzer.functions,
            "classes": analyzer.classes,
            "imports": analyzer.imports,
            "missing_type_hints": analyzer.missing_type_hints,
            "partial_type_hints": analyzer.partial_type_hints,
            "total_functions": len(analyzer.functions),
            "total_classes": len(analyzer.classes),
            "functions_with_complete_hints": len(
                [f for f in analyzer.functions if f.get("complete", False)]
            ),
            "functions_with_partial_hints": len(analyzer.partial_type_hints),
            "functions_without_hints": len(analyzer.missing_type_hints),
        }

    except Exception as e:
        return {
            "file": str(file_path),
            "error": str(e),
            "functions": [],
            "classes": [],
            "imports": [],
            "missing_type_hints": [],
            "partial_type_hints": [],
            "total_functions": 0,
            "total_classes": 0,
            "functions_with_complete_hints": 0,
            "functions_with_partial_hints": 0,
            "functions_without_hints": 0,
        }


def analyze_project(project_root: Path) -> Dict[str, Any]:
    """Analyse tout le projet pour les type hints."""
    python_files = list(project_root.rglob("*.py"))

    # Exclure les fichiers dans env/ et __pycache__/
    python_files = [
        f for f in python_files if "env" not in str(f) and "__pycache__" not in str(f)
    ]

    print(f"Analyse de {len(python_files)} fichiers Python...")

    results = []
    total_stats = {
        "total_files": len(python_files),
        "total_functions": 0,
        "total_classes": 0,
        "functions_with_complete_hints": 0,
        "functions_with_partial_hints": 0,
        "functions_without_hints": 0,
        "files_with_errors": 0,
    }

    for file_path in python_files:
        result = analyze_file(file_path)
        results.append(result)

        if "error" in result:
            total_stats["files_with_errors"] += 1
        else:
            total_stats["total_functions"] += result["total_functions"]
            total_stats["total_classes"] += result["total_classes"]
            total_stats["functions_with_complete_hints"] += result[
                "functions_with_complete_hints"
            ]
            total_stats["functions_with_partial_hints"] += result[
                "functions_with_partial_hints"
            ]
            total_stats["functions_without_hints"] += result["functions_without_hints"]

    return {
        "files": results,
        "stats": total_stats,
    }


def print_summary(analysis: Dict[str, Any]) -> None:
    """Affiche un résumé de l'analyse."""
    stats = analysis["stats"]

    print("\n" + "=" * 60)
    print("RESUME DE L'ANALYSE DES TYPE HINTS")
    print("=" * 60)

    print(f"Fichiers analyses: {stats['total_files']}")
    print(f"Fichiers avec erreurs: {stats['files_with_errors']}")
    print(f"Fonctions totales: {stats['total_functions']}")
    print(f"Classes totales: {stats['total_classes']}")

    if stats["total_functions"] > 0:
        complete_percent = (
            stats["functions_with_complete_hints"] / stats["total_functions"]
        ) * 100
        partial_percent = (
            stats["functions_with_partial_hints"] / stats["total_functions"]
        ) * 100
        none_percent = (
            stats["functions_without_hints"] / stats["total_functions"]
        ) * 100

        print(
            f"\nFonctions avec type hints complets: {stats['functions_with_complete_hints']} ({complete_percent:.1f}%)"
        )
        print(
            f"Fonctions avec type hints partiels: {stats['functions_with_partial_hints']} ({partial_percent:.1f}%)"
        )
        print(
            f"Fonctions sans type hints: {stats['functions_without_hints']} ({none_percent:.1f}%)"
        )

    print("\n" + "=" * 60)


def print_detailed_analysis(analysis: Dict[str, Any]) -> None:
    """Affiche l'analyse détaillée par fichier."""
    print("\nANALYSE DETAILLEE PAR FICHIER")
    print("=" * 60)

    for file_result in analysis["files"]:
        if "error" in file_result:
            print(f"❌ {file_result['file']}: Erreur - {file_result['error']}")
            continue

        if file_result["total_functions"] == 0 and file_result["total_classes"] == 0:
            continue

        print(f"\nFichier: {file_result['file']}")
        print(f"   Fonctions: {file_result['total_functions']}")
        print(f"   Classes: {file_result['total_classes']}")

        if file_result["functions_without_hints"] > 0:
            print(
                f"   Fonctions sans type hints: {file_result['functions_without_hints']}"
            )
            for func in file_result["missing_type_hints"][
                :3
            ]:  # Afficher seulement les 3 premières
                print(f"      - {func['name']} (ligne {func['line']})")
            if len(file_result["missing_type_hints"]) > 3:
                print(
                    f"      ... et {len(file_result['missing_type_hints']) - 3} autres"
                )

        if file_result["functions_with_partial_hints"] > 0:
            print(
                f"   Fonctions avec type hints partiels: {file_result['functions_with_partial_hints']}"
            )


def main():
    """Fonction principale."""
    project_root = Path(__file__).parent.parent

    print("Analyse des type hints dans le projet N2F")
    print(f"Repertoire: {project_root}")

    # Analyser le projet
    analysis = analyze_project(project_root)

    # Afficher les résultats
    print_summary(analysis)
    print_detailed_analysis(analysis)

    # Recommandations
    print("\n" + "=" * 60)
    print("RECOMMANDATIONS")
    print("=" * 60)

    stats = analysis["stats"]
    if stats["total_functions"] > 0:
        complete_percent = (
            stats["functions_with_complete_hints"] / stats["total_functions"]
        ) * 100

        if complete_percent < 50:
            print("Priorite HAUTE: Le projet a tres peu de type hints")
            print("   - Commencer par les fonctions publiques des modules principaux")
            print("   - Ajouter des types pour les paramètres et valeurs de retour")
        elif complete_percent < 80:
            print("Priorite MOYENNE: Le projet a des type hints partiels")
            print("   - Compléter les fonctions sans annotations")
            print("   - Vérifier la cohérence des types existants")
        else:
            print("Priorite BASSE: Le projet a une bonne couverture de type hints")
            print("   - Maintenir la qualité des types existants")
            print("   - Ajouter des types pour les nouvelles fonctionnalités")

    print("\nRessources pour améliorer les type hints:")
    print("   - PEP 484: Type Hints (https://www.python.org/dev/peps/pep-0484/)")
    print("   - mypy: Static Type Checker (https://mypy.readthedocs.io/)")
    print("   - typing module: https://docs.python.org/3/library/typing.html")


if __name__ == "__main__":
    main()
