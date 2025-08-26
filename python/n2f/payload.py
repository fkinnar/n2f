import pandas as pd

from n2f.helper import to_bool


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
        "mail": user["AdresseEmail"],
        "firstname": user["Prenom"],
        "lastname": user["Nom"],
        "company": company_id,
        "role": user["Role"],
        "profile": user["Profil"],
        "managerMail": user["Manager"],
        "defaultCostCenter": user["Centre_Cout"],
        "canCreateVehicle": user["Creation_Vehicule"],
        "personnalCarHaveToBeApproved": to_bool(user["Appro_Veh_Adm"]),
        "removeHomeWorkDistance": to_bool(user["Deduction_Distance_TravDom"]),
        "culture": user["langue"],
        "currencyIsoCode": user["Devise"],
        "jobTitle": user["Fonction"],
        "employeeNumber": user["Matricule"],
        "structure": user["Structure"],
        "ssoLogin": user["Champs_Liaison_SSO"],
        "gotProPayment":  to_bool(user["Moyen_Paiement_Prof"]),
        "accountingAuxiliaryAccount": user["Compte_Auxiliaire_Agresso"],
        "accountingAuxiliaryNotReimbursableAccount": user["Compte_Auxiliaire2"],
        "canRaiseLimits": to_bool(user["Droit_Relever_Plafond"]),
        "authMode": user["Methode_SSO"] if not sandbox else "Integrated",
        "canDefineHisAnalytics": user["Update_Champs_Perso"],
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
    "code": project["Code"],
    "names": [
        {
        "culture": "fr",
        "value": project["Nom_Fr"]
        },
        {
        "culture": "nl",
        "value": project["Nom_Nl"]
        }
    ]
    }

    return payload