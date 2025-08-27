from enum import Enum
from typing import Tuple, Dict, Optional
import pandas as pd

from n2f.process import get_customaxes


class AxeType(Enum):
    """
    Enumération des types d'axes supportés.
    """
    PROJECTS = "projects"
    PLATES = "plates"
    SUBPOSTS = "subposts"


# Cache pour les mappings dynamiques
_dynamic_mappings: Optional[Dict[AxeType, Tuple[str, str]]] = None


def _get_dynamic_mappings(
    base_url: str,
    client_id: str,
    client_secret: str,
    company_id: str,
    simulate: bool = False
) -> Dict[AxeType, Tuple[str, str]]:
    """
    Récupère dynamiquement les mappings des axes personnalisés depuis l'API N2F.

    Args:
        base_url (str): URL de base de l'API N2F
        client_id (str): ID du client pour l'API N2F
        client_secret (str): Secret du client pour l'API N2F
        company_id (str): ID de la société
        simulate (bool): Si True, simule les appels sans les exécuter

    Returns:
        Dict[AxeType, Tuple[str, str]]: Mapping des types d'axes vers (colonne_sql, code_n2f)
    """
    global _dynamic_mappings

    if _dynamic_mappings is not None:
        return _dynamic_mappings

    # Mapping statique pour les projets (cas particulier de l'API N2F)
    mappings = {
        AxeType.PROJECTS: ("PROJECT", "projects")
    }

    try:
        # Récupération des axes personnalisés depuis l'API
        df_customaxes = get_customaxes(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            company_id=company_id,
            simulate=simulate
        )

        if not df_customaxes.empty:
            # Parcours des axes pour trouver les plaques et subposts
            for _, row in df_customaxes.iterrows():
                # Recherche du nom français dans la liste des noms
                names = row.get('names', [])
                french_name = None
                for name in names:
                    if isinstance(name, dict) and name.get('culture') == 'fr':
                        french_name = name.get('value', '').lower()
                        break

                if french_name:
                    uuid = row.get('uuid', '')
                    if french_name == 'plaque':
                        mappings[AxeType.PLATES] = ("PLAQUE", uuid)
                    elif french_name == 'subpost':
                        mappings[AxeType.SUBPOSTS] = ("SUBPOST", uuid)

    except Exception as e:
        raise RuntimeError(f"Erreur lors de la récupération des mappings dynamiques: {e}")

    _dynamic_mappings = mappings
    return mappings


def get_axe_mapping(
    axe_type: AxeType,
    base_url: str = "",
    client_id: str = "",
    client_secret: str = "",
    company_id: str = "",
    simulate: bool = False
) -> Tuple[str, str]:
    """
    Retourne le mapping pour un type d'axe donné.

    Pour les projets, utilise le mapping statique.
    Pour les plaques et subposts, tente de récupérer dynamiquement depuis l'API N2F.

    Args:
        axe_type (AxeType): Le type d'axe
        base_url (str): URL de base de l'API N2F (requis pour les mappings dynamiques)
        client_id (str): ID du client pour l'API N2F (requis pour les mappings dynamiques)
        client_secret (str): Secret du client pour l'API N2F (requis pour les mappings dynamiques)
        company_id (str): ID de la société (requis pour les mappings dynamiques)
        simulate (bool): Si True, simule les appels sans les exécuter

    Returns:
        Tuple[str, str]: (colonne_sql, code_n2f)
            - colonne_sql: La valeur de la colonne 'typ' dans la vue SQL Agresso
            - code_n2f: Le code à utiliser pour l'API N2F
    """
    # Pour les projets, toujours utiliser le mapping statique
    if axe_type == AxeType.PROJECTS:
        return ("PROJECT", "projects")

        # Pour les autres types, utiliser les mappings dynamiques
    if not (base_url and client_id and client_secret and company_id):
        raise ValueError("Paramètres API requis pour les mappings dynamiques (base_url, client_id, client_secret, company_id)")

    mappings = _get_dynamic_mappings(base_url, client_id, client_secret, company_id, simulate)
    if axe_type not in mappings:
        raise ValueError(f"Type d'axe non supporté ou non trouvé dans l'API: {axe_type}")

    return mappings[axe_type]


def clear_mappings_cache() -> None:
    """
    Efface le cache des mappings dynamiques.
    Utile pour forcer une nouvelle récupération depuis l'API.
    """
    global _dynamic_mappings
    _dynamic_mappings = None
