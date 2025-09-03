"""
Exemple d'utilisation du système de cache amélioré N2F.

Ce module démontre les fonctionnalités du cache avancé :
- Cache en mémoire et persistant
- Gestion de l'expiration
- Métriques de performance
- Invalidation sélective
"""

import time
import pandas as pd
from pathlib import Path
from typing import Any, Dict
from ..cache import get_cache, cache_get, cache_set, cache_invalidate, cache_stats


def example_cache_basic_usage() -> None:
    """Exemple d'utilisation basique du cache."""
    print("=== Exemple d'utilisation basique ===")

    # Initialisation du cache avec persistance
    cache_dir = Path(__file__).parent.parent.parent / "cache"
    cache = get_cache(cache_dir=cache_dir, max_size_mb=50, default_ttl=300)

    # Simulation de données
    test_data = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "value": [100, 200, 300, 400, 500],
        }
    )

    # Stockage en cache
    print("Stockage de données en cache...")
    cache.set(test_data, "get_users", "company_123")

    # Récupération depuis le cache
    print("Récupération depuis le cache...")
    cached_data = cache.get("get_users", "company_123")

    if cached_data is not None:
        print(f"Données récupérées : {len(cached_data)} lignes")
        print(cached_data.head())
    else:
        print("Aucune donnée en cache")

    # Affichage des statistiques
    print("\nStatistiques du cache :")
    print(cache_stats())


def example_ttl_expiration() -> None:
    """Exemple de gestion de l'expiration TTL."""
    print("\n=== Exemple de gestion TTL ===")

    cache = get_cache()

    # Données avec TTL court (5 secondes)
    short_lived_data = pd.DataFrame({"temp": [1, 2, 3]})
    cache.set(short_lived_data, "temp_data", ttl=5)

    print("Données stockées avec TTL de 5 secondes")

    # Première récupération (devrait fonctionner)
    data1 = cache.get("temp_data")
    print(f"Récupération immédiate : {'Succès' if data1 is not None else 'Échec'}")

    # Attente de l'expiration
    print("Attente de 6 secondes pour l'expiration...")
    time.sleep(6)

    # Deuxième récupération (devrait échouer)
    data2 = cache.get("temp_data")
    print(
        f"Récupération après expiration : {'Succès' if data2 is not None else 'Échec'}"
    )


def example_cache_invalidation() -> None:
    """Exemple d'invalidation sélective du cache."""
    print("\n=== Exemple d'invalidation sélective ===")

    cache = get_cache()

    # Stockage de plusieurs entrées
    cache.set("data1", "function1", "param1")
    cache.set("data2", "function1", "param2")
    cache.set("data3", "function2", "param1")

    print("3 entrées stockées en cache")

    # Vérification de la présence
    print(
        f"function1/param1 : "
        f"{'Présent' if cache.get('function1', 'param1') else 'Absent'}"
    )
    print(
        f"function1/param2 : "
        f"{'Présent' if cache.get('function1', 'param2') else 'Absent'}"
    )
    print(
        f"function2/param1 : "
        f"{'Présent' if cache.get('function2', 'param1') else 'Absent'}"
    )

    # Invalidation sélective
    print("\nInvalidation de function1/param1...")
    cache.invalidate("function1", "param1")

    # Vérification après invalidation
    print(
        f"function1/param1 : "
        f"{'Présent' if cache.get('function1', 'param1') else 'Absent'}"
    )
    print(
        f"function1/param2 : "
        f"{'Présent' if cache.get('function1', 'param2') else 'Absent'}"
    )
    print(
        f"function2/param1 : "
        f"{'Présent' if cache.get('function2', 'param1') else 'Absent'}"
    )


def example_performance_metrics() -> None:
    """Exemple de métriques de performance."""
    print("\n=== Exemple de métriques de performance ===")

    cache = get_cache()

    # Simulation d'utilisation intensive
    for i in range(10):
        # Stockage
        cache.set(f"data_{i}", "test_function", i)

        # Récupération (hit)
        cache.get("test_function", i)

        # Récupération d'une clé inexistante (miss)
        cache.get("test_function", f"missing_{i}")

    # Affichage des métriques détaillées
    metrics = cache.get_metrics()
    print("Métriques détaillées :")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")


def example_persistent_cache() -> None:
    """Exemple de cache persistant."""
    print("\n=== Exemple de cache persistant ===")

    cache_dir = Path(__file__).parent.parent.parent / "cache_persistent"

    # Première session
    print("Session 1 - Stockage de données persistantes...")
    cache1 = get_cache(cache_dir=cache_dir, max_size_mb=10)
    cache1.set("Données persistantes", "persistent_function", "param1")
    print("Données stockées avec persistance")

    # Deuxième session (nouvelle instance)
    print("\nSession 2 - Récupération de données persistantes...")
    cache2 = get_cache(cache_dir=cache_dir, max_size_mb=10)
    data = cache2.get("persistent_function", "param1")

    if data is not None:
        print(f"Données récupérées depuis la persistance : {data}")
    else:
        print("Aucune donnée trouvée en persistance")

    # Nettoyage
    cache_dir.mkdir(exist_ok=True)
    for cache_file in cache_dir.glob("*.cache"):
        cache_file.unlink()


def example_cache_eviction() -> None:
    """Exemple d'éviction LRU du cache."""
    print("\n=== Exemple d'éviction LRU ===")

    # Cache très petit (1 MB)
    cache = get_cache(max_size_mb=1)

    # Stockage de données volumineuses
    large_data = "x" * (500 * 1024)  # 500 KB

    print("Stockage de données volumineuses...")
    for i in range(5):
        cache.set(large_data, "large_function", i)
        print(f"Entrée {i} stockée")

    # Vérification de l'éviction
    print("\nVérification de l'éviction...")
    for i in range(5):
        data = cache.get("large_function", i)
        status = "Présent" if data is not None else "Évincé"
        print(f"Entrée {i}: {status}")

    print(f"\nTaille du cache : {cache.get_metrics()['total_size_mb']:.2f} MB")


if __name__ == "__main__":
    print("Exemples d'utilisation du cache amélioré N2F")
    print("=" * 50)

    try:
        # Exemples d'utilisation
        example_cache_basic_usage()
        example_ttl_expiration()
        example_cache_invalidation()
        example_performance_metrics()
        example_persistent_cache()
        example_cache_eviction()

    except Exception as e:
        print(f"Erreur lors de l'exécution des exemples : {e}")

    print("\n" + "=" * 50)
    print("Exemples terminés")
