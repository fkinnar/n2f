import pandas as pd

from n2f.helper import to_bool, normalize_date_for_payload
from business.constants import (
    AGRESSO_COL_EMAIL, AGRESSO_COL_FIRSTNAME, AGRESSO_COL_LASTNAME,
    AGRESSO_COL_ROLE, AGRESSO_COL_PROFILE, AGRESSO_COL_MANAGER,
    AGRESSO_COL_COST_CENTER, AGRESSO_COL_CREATE_VEHICLE, AGRESSO_COL_APPROVE_VEHICLE,
    AGRESSO_COL_DEDUCT_DISTANCE, AGRESSO_COL_LANGUAGE, AGRESSO_COL_CURRENCY,
    AGRESSO_COL_FUNCTION, AGRESSO_COL_EMPLOYEE_NUMBER, AGRESSO_COL_STRUCTURE,
    AGRESSO_COL_SSO_LOGIN, AGRESSO_COL_PRO_PAYMENT, AGRESSO_COL_AUX_ACCOUNT,
    AGRESSO_COL_AUX_ACCOUNT2, AGRESSO_COL_RAISE_LIMITS, AGRESSO_COL_SSO_METHOD,
    AGRESSO_COL_UPDATE_PERSONAL, AGRESSO_COL_DESCRIPTION, AGRESSO_COL_DATE_FROM,
    AGRESSO_COL_DATE_TO, COL_CODE, COL_NAMES, COL_CULTURE, COL_VALUE,
    N2F_COL_EMAIL, N2F_COL_FIRSTNAME, N2F_COL_LASTNAME, N2F_COL_COMPANY,
    N2F_COL_ROLE, N2F_COL_PROFILE, N2F_COL_MANAGER_MAIL, N2F_COL_COST_CENTER,
    N2F_COL_CREATE_VEHICLE, N2F_COL_APPROVE_VEHICLE, N2F_COL_DEDUCT_DISTANCE,
    N2F_COL_CULTURE, N2F_COL_CURRENCY, N2F_COL_JOB_TITLE, N2F_COL_EMPLOYEE_NUMBER,
    N2F_COL_STRUCTURE, N2F_COL_SSO_LOGIN, N2F_COL_PRO_PAYMENT, N2F_COL_AUX_ACCOUNT,
    N2F_COL_AUX_ACCOUNT2, N2F_COL_RAISE_LIMITS, N2F_COL_AUTH_MODE,
    N2F_COL_UPDATE_PERSONAL, N2F_COL_VALIDITY_DATE_FROM, N2F_COL_VALIDITY_DATE_TO,
    DEFAULT_AUTH_MODE_SANDBOX, CULTURE_FR, CULTURE_NL
)


def create_user_upsert_payload(user: dict, company_id: str, sandbox: bool) -> dict:
    """
    Construit le payload JSON pour l'upsert (création ou mise à jour) d'un utilisateur N2F
    à partir d'une ligne du DataFrame Agresso, en remplaçant le code entreprise par son UUID.

    Args:
        user (dict): Dictionnaire représentant un utilisateur.
        company_id (str): ID de l'entreprise à laquelle l'utilisateur appartient.
        sandbox (bool): Indique si l'environnement est un sandbox.

    Returns:
        dict: Dictionnaire prêt à être converti en JSON pour l'API N2F.
    """

    payload = {
        N2F_COL_EMAIL: user[AGRESSO_COL_EMAIL],
        N2F_COL_FIRSTNAME: user[AGRESSO_COL_FIRSTNAME],
        N2F_COL_LASTNAME: user[AGRESSO_COL_LASTNAME],
        N2F_COL_COMPANY: company_id,
        N2F_COL_ROLE: user[AGRESSO_COL_ROLE],
        N2F_COL_PROFILE: user[AGRESSO_COL_PROFILE],
        N2F_COL_MANAGER_MAIL: user[AGRESSO_COL_MANAGER],
        N2F_COL_COST_CENTER: user[AGRESSO_COL_COST_CENTER],
        N2F_COL_CREATE_VEHICLE: user[AGRESSO_COL_CREATE_VEHICLE],
        N2F_COL_APPROVE_VEHICLE: to_bool(user[AGRESSO_COL_APPROVE_VEHICLE]),
        N2F_COL_DEDUCT_DISTANCE: to_bool(user[AGRESSO_COL_DEDUCT_DISTANCE]),
        N2F_COL_CULTURE: user[AGRESSO_COL_LANGUAGE],
        N2F_COL_CURRENCY: user[AGRESSO_COL_CURRENCY],
        N2F_COL_JOB_TITLE: user[AGRESSO_COL_FUNCTION],
        N2F_COL_EMPLOYEE_NUMBER: user[AGRESSO_COL_EMPLOYEE_NUMBER],
        N2F_COL_STRUCTURE: user[AGRESSO_COL_STRUCTURE],
        N2F_COL_SSO_LOGIN: user[AGRESSO_COL_SSO_LOGIN],
        N2F_COL_PRO_PAYMENT: to_bool(user[AGRESSO_COL_PRO_PAYMENT]),
        N2F_COL_AUX_ACCOUNT: user[AGRESSO_COL_AUX_ACCOUNT],
        N2F_COL_AUX_ACCOUNT2: user[AGRESSO_COL_AUX_ACCOUNT2],
        N2F_COL_RAISE_LIMITS: to_bool(user[AGRESSO_COL_RAISE_LIMITS]),
        N2F_COL_AUTH_MODE: user[AGRESSO_COL_SSO_METHOD] if not sandbox else DEFAULT_AUTH_MODE_SANDBOX,
        N2F_COL_UPDATE_PERSONAL: user[AGRESSO_COL_UPDATE_PERSONAL],
    }

    return payload


def create_project_upsert_payload(project: dict, sandbox: bool) -> dict:
    """
    Construit le payload JSON pour l'upsert (création ou mise à jour) d'un projet N2F
    à partir d'une ligne du DataFrame Agresso.

    Args:
        project (dict): Dictionnaire représentant un projet.
        sandbox (bool): Indique si l'environnement est un sandbox.

    Returns:
        dict: Dictionnaire prêt à être converti en JSON pour l'API N2F.
    """

    payload = {
        COL_CODE: project[COL_CODE],
        COL_NAMES: [
            {
                COL_CULTURE: CULTURE_FR,
                COL_VALUE: project[AGRESSO_COL_DESCRIPTION]
            },
            {
                COL_CULTURE: CULTURE_NL,
                COL_VALUE: project[AGRESSO_COL_DESCRIPTION]
            }
        ],
        N2F_COL_VALIDITY_DATE_FROM: normalize_date_for_payload(project.get(AGRESSO_COL_DATE_FROM)),
        N2F_COL_VALIDITY_DATE_TO: normalize_date_for_payload(project.get(AGRESSO_COL_DATE_TO)),
    }

    return payload