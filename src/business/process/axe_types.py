from enum import Enum
from typing import Tuple, Dict, Optional
import pandas as pd

from n2f.client import N2fApiClient

class AxeType(Enum):
    PROJECTS = "projects"
    PLATES = "plates"
    SUBPOSTS = "subposts"

_dynamic_mappings: Optional[Dict[AxeType, Tuple[str, str]]] = None

def _get_dynamic_mappings(
    n2f_client: N2fApiClient,
    company_id: str
) -> Dict[AxeType, Tuple[str, str]]:
    """Récupère dynamiquement les mappings des axes personnalisés via le client N2F."""
    global _dynamic_mappings
    if _dynamic_mappings is not None:
        return _dynamic_mappings

    mappings = {AxeType.PROJECTS: ("PROJECT", "projects")}

    try:
        df_customaxes = n2f_client.get_custom_axes(company_id)
        if not df_customaxes.empty:
            for _, row in df_customaxes.iterrows():
                names = row.get('names', [])
                french_name = next((name.get('value', '').lower() for name in names if isinstance(name, dict) and name.get('culture') == 'fr'), None)
                
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
    n2f_client: N2fApiClient,
    company_id: str
) -> Tuple[str, str]:
    """Retourne le mapping pour un type d'axe donné en utilisant le client N2F."""
    if axe_type == AxeType.PROJECTS:
        return ("PROJECT", "projects")

    if not company_id:
        raise ValueError("company_id est requis pour les mappings dynamiques")

    mappings = _get_dynamic_mappings(n2f_client, company_id)
    if axe_type not in mappings:
        raise ValueError(f"Type d'axe non supporté ou non trouvé dans l'API: {axe_type}")

    return mappings[axe_type]

def clear_mappings_cache() -> None:
    """Efface le cache des mappings dynamiques."""
    global _dynamic_mappings
    _dynamic_mappings = None