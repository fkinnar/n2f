from unittest.mock import Mock, patch, MagicMock

import n2f.payload

import unittest
import sys
import os

import pandas as pd
from datetime import datetime

from n2f.payload import create_user_upsert_payload, create_project_upsert_payload
from business.constants import (
    AGRESSO_COL_EMAIL, AGRESSO_COL_FIRSTNAME, AGRESSO_COL_LASTNAME,
    AGRESSO_COL_ROLE, AGRESSO_COL_PROFILE, AGRESSO_COL_MANAGER,
    AGRESSO_COL_CREATE_VEHICLE, AGRESSO_COL_APPROVE_VEHICLE,
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

class TestPayloads(unittest.TestCase):
    """Tests unitaires pour les fonctions de construction de payloads."""

    def setUp(self):
        """Configure l'environnement de test."""
        # Données de test pour un utilisateur
        self.user_data = {
            AGRESSO_COL_EMAIL: "test@example.com",
            AGRESSO_COL_FIRSTNAME: "John",
            AGRESSO_COL_LASTNAME: "Doe",
            AGRESSO_COL_ROLE: "USER",
            AGRESSO_COL_PROFILE: "STANDARD",
            AGRESSO_COL_MANAGER: "manager@example.com",
            AGRESSO_COL_CREATE_VEHICLE: "Y",
            AGRESSO_COL_APPROVE_VEHICLE: "Y",
            AGRESSO_COL_DEDUCT_DISTANCE: "N",
            AGRESSO_COL_LANGUAGE: "FR",
            AGRESSO_COL_CURRENCY: "EUR",
            AGRESSO_COL_FUNCTION: "Developer",
            AGRESSO_COL_EMPLOYEE_NUMBER: "EMP001",
            AGRESSO_COL_STRUCTURE: "IT",
            AGRESSO_COL_SSO_LOGIN: "john.doe",
            AGRESSO_COL_PRO_PAYMENT: "Y",
            AGRESSO_COL_AUX_ACCOUNT: "AUX001",
            AGRESSO_COL_AUX_ACCOUNT2: "AUX002",
            AGRESSO_COL_RAISE_LIMITS: "N",
            AGRESSO_COL_SSO_METHOD: "SSO",
            AGRESSO_COL_UPDATE_PERSONAL: "Y"
        }

        # Données de test pour un projet
        self.project_data = {
            COL_CODE: "PROJ001",
            AGRESSO_COL_DESCRIPTION: "Test Project",
            AGRESSO_COL_DATE_FROM: "2025-01-01",
            AGRESSO_COL_DATE_TO: "2025-12-31"
        }

    def test_create_user_upsert_payload_production(self):
        """Test la création d'un payload utilisateur en production."""
        company_id = "company-uuid-123"
        sandbox = False
        
        payload = create_user_upsert_payload(self.user_data, company_id, sandbox)
        
        # Vérification des champs obligatoires
        self.assertEqual(payload[N2F_COL_EMAIL], "test@example.com")
        self.assertEqual(payload[N2F_COL_FIRSTNAME], "John")
        self.assertEqual(payload[N2F_COL_LASTNAME], "Doe")
        self.assertEqual(payload[N2F_COL_COMPANY], company_id)
        self.assertEqual(payload[N2F_COL_ROLE], "USER")
        self.assertEqual(payload[N2F_COL_PROFILE], "STANDARD")
        self.assertEqual(payload[N2F_COL_MANAGER_MAIL], "manager@example.com")
        
        # Vérification des champs booléens
        self.assertTrue(payload[N2F_COL_APPROVE_VEHICLE])
        self.assertFalse(payload[N2F_COL_DEDUCT_DISTANCE])
        self.assertTrue(payload[N2F_COL_PRO_PAYMENT])
        self.assertFalse(payload[N2F_COL_RAISE_LIMITS])
        
        # Vérification des champs de configuration
        self.assertEqual(payload[N2F_COL_CULTURE], "FR")
        self.assertEqual(payload[N2F_COL_CURRENCY], "EUR")
        self.assertEqual(payload[N2F_COL_JOB_TITLE], "Developer")
        self.assertEqual(payload[N2F_COL_EMPLOYEE_NUMBER], "EMP001")
        self.assertEqual(payload[N2F_COL_STRUCTURE], "IT")
        self.assertEqual(payload[N2F_COL_AUX_ACCOUNT], "AUX001")
        
        # Vérification du mode d'authentification en production
        self.assertEqual(payload[N2F_COL_AUTH_MODE], "SSO")

    def test_create_user_upsert_payload_sandbox(self):
        """Test la création d'un payload utilisateur en sandbox."""
        company_id = "company-uuid-123"
        sandbox = True
        
        payload = create_user_upsert_payload(self.user_data, company_id, sandbox)
        
        # Vérification que le mode d'authentification est forcé en sandbox
        self.assertEqual(payload[N2F_COL_AUTH_MODE], DEFAULT_AUTH_MODE_SANDBOX)
        
        # Vérification que les autres champs restent identiques
        self.assertEqual(payload[N2F_COL_EMAIL], "test@example.com")
        self.assertEqual(payload[N2F_COL_COMPANY], company_id)

    def test_create_user_upsert_payload_with_missing_optional_fields(self):
        """Test la création d'un payload utilisateur avec des champs optionnels manquants."""
        # Données utilisateur avec champs manquants
        minimal_user = {
            AGRESSO_COL_EMAIL: "minimal@example.com",
            AGRESSO_COL_FIRSTNAME: "Minimal",
            AGRESSO_COL_LASTNAME: "User",
            AGRESSO_COL_ROLE: "USER",
            AGRESSO_COL_PROFILE: "STANDARD",
            AGRESSO_COL_MANAGER: "",
            AGRESSO_COL_CREATE_VEHICLE: "",
            AGRESSO_COL_APPROVE_VEHICLE: "",
            AGRESSO_COL_DEDUCT_DISTANCE: "",
            AGRESSO_COL_LANGUAGE: "",
            AGRESSO_COL_CURRENCY: "",
            AGRESSO_COL_FUNCTION: "",
            AGRESSO_COL_EMPLOYEE_NUMBER: "",
            AGRESSO_COL_STRUCTURE: "",
            AGRESSO_COL_SSO_LOGIN: "",
            AGRESSO_COL_PRO_PAYMENT: "",
            AGRESSO_COL_AUX_ACCOUNT: "",
            AGRESSO_COL_AUX_ACCOUNT2: "",
            AGRESSO_COL_RAISE_LIMITS: "",
            AGRESSO_COL_SSO_METHOD: "",
            AGRESSO_COL_UPDATE_PERSONAL: ""
        }
        
        company_id = "company-uuid-123"
        sandbox = False
        
        payload = create_user_upsert_payload(minimal_user, company_id, sandbox)
        
        # Vérification que les champs obligatoires sont présents
        self.assertEqual(payload[N2F_COL_EMAIL], "minimal@example.com")
        self.assertEqual(payload[N2F_COL_FIRSTNAME], "Minimal")
        self.assertEqual(payload[N2F_COL_LASTNAME], "User")
        self.assertEqual(payload[N2F_COL_COMPANY], company_id)
        
        # Vérification que les champs vides sont gérés correctement
        self.assertEqual(payload[N2F_COL_MANAGER_MAIL], "")
        self.assertEqual(payload[N2F_COL_CULTURE], "")
        self.assertEqual(payload[N2F_COL_CURRENCY], "")

    def test_create_user_upsert_payload_boolean_conversion(self):
        """Test la conversion des valeurs booléennes."""
        # Test avec différentes valeurs pour les champs booléens
        test_cases = [
            ("yes", True),
            ("YES", True),
            ("1", True),
            ("true", True),
            ("True", True),
            ("on", True),
            ("no", False),
            ("NO", False),
            ("0", False),
            ("false", False),
            ("False", False),
            ("off", False),
            ("", False),
            ("invalid", False)
        ]
        
        for input_value, expected_output in test_cases:
            with self.subTest(input_value=input_value):
                user_data = self.user_data.copy()
                user_data[AGRESSO_COL_APPROVE_VEHICLE] = input_value
                
                payload = create_user_upsert_payload(user_data, "company-uuid", False)
                self.assertEqual(payload[N2F_COL_APPROVE_VEHICLE], expected_output)

    def test_create_project_upsert_payload(self):
        """Test la création d'un payload projet."""
        sandbox = False
        
        payload = create_project_upsert_payload(self.project_data, sandbox)
        
        # Vérification des champs de base
        self.assertEqual(payload[COL_CODE], "PROJ001")
        
        # Vérification des noms multilingues
        names = payload[COL_NAMES]
        self.assertEqual(len(names), 2)
        
        # Vérification du nom français
        fr_name = next((name for name in names if name[COL_CULTURE] == CULTURE_FR), None)
        self.assertIsNotNone(fr_name)
        self.assertEqual(fr_name[COL_VALUE], "Test Project")
        
        # Vérification du nom néerlandais
        nl_name = next((name for name in names if name[COL_CULTURE] == CULTURE_NL), None)
        self.assertIsNotNone(nl_name)
        self.assertEqual(nl_name[COL_VALUE], "Test Project")
        
        # Vérification des dates
        self.assertEqual(payload[N2F_COL_VALIDITY_DATE_FROM], "2025-01-01T00:00:00Z")
        self.assertEqual(payload[N2F_COL_VALIDITY_DATE_TO], "2025-12-31T00:00:00Z")

    def test_create_project_upsert_payload_with_missing_dates(self):
        """Test la création d'un payload projet avec des dates manquantes."""
        project_data = {
            COL_CODE: "PROJ002",
            AGRESSO_COL_DESCRIPTION: "Project without dates"
        }
        
        payload = create_project_upsert_payload(project_data, False)
        
        # Vérification que les dates manquantes sont gérées
        self.assertIsNone(payload[N2F_COL_VALIDITY_DATE_FROM])
        self.assertIsNone(payload[N2F_COL_VALIDITY_DATE_TO])

    def test_create_project_upsert_payload_with_none_dates(self):
        """Test la création d'un payload projet avec des dates None."""
        project_data = {
            COL_CODE: "PROJ003",
            AGRESSO_COL_DESCRIPTION: "Project with None dates",
            AGRESSO_COL_DATE_FROM: None,
            AGRESSO_COL_DATE_TO: None
        }
        
        payload = create_project_upsert_payload(project_data, False)
        
        # Vérification que les dates None sont gérées
        self.assertIsNone(payload[N2F_COL_VALIDITY_DATE_FROM])
        self.assertIsNone(payload[N2F_COL_VALIDITY_DATE_TO])

    def test_create_project_upsert_payload_sandbox_vs_production(self):
        """Test que le payload projet est identique en sandbox et production."""
        sandbox_payload = create_project_upsert_payload(self.project_data, True)
        production_payload = create_project_upsert_payload(self.project_data, False)
        
        # Les payloads projets doivent être identiques (pas d'impact du sandbox)
        self.assertEqual(sandbox_payload, production_payload)

    def test_create_user_upsert_payload_all_fields_mapped(self):
        """Test que tous les champs Agresso sont correctement mappés vers N2F."""
        payload = create_user_upsert_payload(self.user_data, "company-uuid", False)
        
        # Vérification que tous les champs attendus sont présents
        expected_fields = [
            N2F_COL_EMAIL, N2F_COL_FIRSTNAME, N2F_COL_LASTNAME, N2F_COL_COMPANY,
            N2F_COL_ROLE, N2F_COL_PROFILE, N2F_COL_MANAGER_MAIL, N2F_COL_CREATE_VEHICLE,
            N2F_COL_APPROVE_VEHICLE, N2F_COL_DEDUCT_DISTANCE, N2F_COL_CULTURE,
            N2F_COL_CURRENCY, N2F_COL_JOB_TITLE, N2F_COL_EMPLOYEE_NUMBER,
            N2F_COL_STRUCTURE, N2F_COL_PRO_PAYMENT, N2F_COL_AUX_ACCOUNT,
            N2F_COL_RAISE_LIMITS, N2F_COL_AUTH_MODE
        ]
        
        for field in expected_fields:
            self.assertIn(field, payload, f"Le champ {field} est manquant dans le payload")

    def test_create_project_upsert_payload_structure(self):
        """Test la structure du payload projet."""
        payload = create_project_upsert_payload(self.project_data, False)
        
        # Vérification de la structure des noms
        self.assertIn(COL_NAMES, payload)
        self.assertIsInstance(payload[COL_NAMES], list)
        
        for name_entry in payload[COL_NAMES]:
            self.assertIn(COL_CULTURE, name_entry)
            self.assertIn(COL_VALUE, name_entry)
            self.assertIsInstance(name_entry[COL_CULTURE], str)
            self.assertIsInstance(name_entry[COL_VALUE], str)

    def test_create_user_upsert_payload_with_special_characters(self):
        """Test la création d'un payload utilisateur avec des caractères spéciaux."""
        user_data = self.user_data.copy()
        user_data[AGRESSO_COL_FIRSTNAME] = "José"
        user_data[AGRESSO_COL_LASTNAME] = "O'Connor"
        user_data[AGRESSO_COL_FUNCTION] = "Développeur Senior"
        
        payload = create_user_upsert_payload(user_data, "company-uuid", False)
        
        self.assertEqual(payload[N2F_COL_FIRSTNAME], "José")
        self.assertEqual(payload[N2F_COL_LASTNAME], "O'Connor")
        self.assertEqual(payload[N2F_COL_JOB_TITLE], "Développeur Senior")

    def test_create_project_upsert_payload_with_special_characters(self):
        """Test la création d'un payload projet avec des caractères spéciaux."""
        project_data = {
            COL_CODE: "PROJ-ÉTÉ",
            AGRESSO_COL_DESCRIPTION: "Projet d'été avec accents",
            AGRESSO_COL_DATE_FROM: "2025-06-01",
            AGRESSO_COL_DATE_TO: "2025-08-31"
        }
        
        payload = create_project_upsert_payload(project_data, False)
        
        self.assertEqual(payload[COL_CODE], "PROJ-ÉTÉ")
        
        # Vérification que les caractères spéciaux sont préservés dans les noms
        names = payload[COL_NAMES]
        for name_entry in names:
            self.assertEqual(name_entry[COL_VALUE], "Projet d'été avec accents")

    def test_create_user_upsert_payload_empty_strings(self):
        """Test la gestion des chaînes vides dans le payload utilisateur."""
        user_data = self.user_data.copy()
        user_data[AGRESSO_COL_FIRSTNAME] = ""
        user_data[AGRESSO_COL_LASTNAME] = ""
        user_data[AGRESSO_COL_FUNCTION] = ""
        
        payload = create_user_upsert_payload(user_data, "company-uuid", False)
        
        # Les chaînes vides doivent être préservées
        self.assertEqual(payload[N2F_COL_FIRSTNAME], "")
        self.assertEqual(payload[N2F_COL_LASTNAME], "")
        self.assertEqual(payload[N2F_COL_JOB_TITLE], "")

    def test_create_project_upsert_payload_empty_description(self):
        """Test la gestion d'une description vide dans le payload projet."""
        project_data = {
            COL_CODE: "PROJ004",
            AGRESSO_COL_DESCRIPTION: "",
            AGRESSO_COL_DATE_FROM: "2025-01-01",
            AGRESSO_COL_DATE_TO: "2025-12-31"
        }
        
        payload = create_project_upsert_payload(project_data, False)
        
        # La description vide doit être préservée dans les noms
        names = payload[COL_NAMES]
        for name_entry in names:
            self.assertEqual(name_entry[COL_VALUE], "")

if __name__ == '__main__':
    unittest.main()
