"""
Tests unitaires pour les fonctions de normalisation.

Ce module teste les fonctions de normalisation et de transformation
des données pour la synchronisation N2F.
"""

import unittest


import pandas as pd
import numpy as np
from typing import cast

from business.normalize import (
    normalize_agresso_users,
    normalize_n2f_users,
    build_mapping,
)
from business.constants import (
    AGRESSO_COL_EMAIL,
    AGRESSO_COL_MANAGER,
    AGRESSO_COL_STRUCTURE,
    AGRESSO_COL_SSO_METHOD,
    N2F_COL_EMAIL,
    N2F_COL_PROFILE,
    N2F_COL_ROLE,
    COL_NAMES,
    COL_CULTURE,
    COL_VALUE,
    DEFAULT_STRUCTURE,
    DEFAULT_PROFILE,
    DEFAULT_ROLE,
    DEFAULT_SSO_METHOD,
    CULTURE_FR,
    CULTURE_NL,
)
from core.exceptions import ValidationException


class TestNormalize(unittest.TestCase):
    """Tests unitaires pour les fonctions de normalisation."""

    def setUp(self):
        """Configure l'environnement de test."""
        # Données de test pour les utilisateurs Agresso
        self.agresso_users_data = {
            AGRESSO_COL_EMAIL: [
                "TEST@EXAMPLE.COM",
                "user@test.com",
                "ADMIN@DOMAIN.COM",
            ],
            AGRESSO_COL_MANAGER: ["MANAGER@EXAMPLE.COM", "boss@test.com", ""],
            AGRESSO_COL_STRUCTURE: ["IT", "", "HR"],
            AGRESSO_COL_SSO_METHOD: ["SSO", "Saml", "LDAP"],
        }

        # Données de test pour les utilisateurs N2F
        self.n2f_users_data = {
            N2F_COL_EMAIL: ["TEST@EXAMPLE.COM", "user@test.com", "ADMIN@DOMAIN.COM"],
            N2F_COL_PROFILE: ["STANDARD", "", "PREMIUM"],
            N2F_COL_ROLE: ["USER", "", "ADMIN"],
        }

        # Données de test pour le mapping
        self.mapping_data = {
            COL_NAMES: [
                [
                    {COL_CULTURE: CULTURE_FR, COL_VALUE: "Standard"},
                    {COL_CULTURE: CULTURE_NL, COL_VALUE: "Standaard"},
                ],
                [
                    {COL_CULTURE: CULTURE_FR, COL_VALUE: "Premium"},
                    {COL_CULTURE: CULTURE_NL, COL_VALUE: "Premium"},
                ],
            ]
        }

    def test_normalize_agresso_users_email_lowercase(self):
        """Test la normalisation des emails en minuscules."""
        df = pd.DataFrame(self.agresso_users_data)
        result = normalize_agresso_users(df)

        # Vérification que les emails sont en minuscules
        expected_emails = ["test@example.com", "user@test.com", "admin@domain.com"]
        self.assertEqual(result[AGRESSO_COL_EMAIL].tolist(), expected_emails)

    def test_normalize_agresso_users_manager_lowercase(self):
        """Test la normalisation des emails de manager en minuscules."""
        df = pd.DataFrame(self.agresso_users_data)
        result = normalize_agresso_users(df)

        # Vérification que les emails de manager sont en minuscules
        expected_managers = ["manager@example.com", "boss@test.com", ""]
        self.assertEqual(result[AGRESSO_COL_MANAGER].tolist(), expected_managers)

    def test_normalize_agresso_users_structure_default(self):
        """Test la normalisation des structures avec valeur par défaut."""
        df = pd.DataFrame(self.agresso_users_data)
        result = normalize_agresso_users(df)

        # Vérification que les structures vides sont remplacées par la valeur par défaut
        expected_structures = ["IT", DEFAULT_STRUCTURE, "HR"]
        self.assertEqual(result[AGRESSO_COL_STRUCTURE].tolist(), expected_structures)

    def test_normalize_agresso_users_sso_method_replacement(self):
        """Test le remplacement de 'Saml' par la valeur par défaut."""
        df = pd.DataFrame(self.agresso_users_data)
        result = normalize_agresso_users(df)

        # Vérification que 'Saml' est remplacé par la valeur par défaut
        expected_sso_methods = ["SSO", DEFAULT_SSO_METHOD, "LDAP"]
        self.assertEqual(result[AGRESSO_COL_SSO_METHOD].tolist(), expected_sso_methods)

    def test_normalize_agresso_users_with_nan_values(self):
        """Test la normalisation avec des valeurs NaN."""
        # Ajout de valeurs NaN
        data_with_nan = self.agresso_users_data.copy()
        data_with_nan[AGRESSO_COL_STRUCTURE] = cast(list, ["IT", np.nan, "HR"])
        data_with_nan[AGRESSO_COL_MANAGER] = cast(
            list, ["manager@test.com", np.nan, ""]
        )

        df = pd.DataFrame(data_with_nan)
        result = normalize_agresso_users(df)

        # Vérification que les NaN sont gérés correctement
        expected_structures = ["IT", DEFAULT_STRUCTURE, "HR"]
        self.assertEqual(result[AGRESSO_COL_STRUCTURE].tolist(), expected_structures)

        expected_managers = ["manager@test.com", "", ""]
        self.assertEqual(result[AGRESSO_COL_MANAGER].tolist(), expected_managers)

    def test_normalize_agresso_users_preserves_original_data(self):
        """Test que la normalisation préserve les données originales non modifiées."""
        df = pd.DataFrame(self.agresso_users_data)
        original_df = df.copy()
        result = normalize_agresso_users(df)

        # Vérification que le DataFrame original n'est pas modifié
        pd.testing.assert_frame_equal(df, original_df)

    def test_normalize_n2f_users_email_lowercase(self):
        """Test la normalisation des emails N2F en minuscules."""
        df = pd.DataFrame(self.n2f_users_data)
        result = normalize_n2f_users(df)

        # Vérification que les emails sont en minuscules
        expected_emails = ["test@example.com", "user@test.com", "admin@domain.com"]
        self.assertEqual(result[N2F_COL_EMAIL].tolist(), expected_emails)

    def test_normalize_n2f_users_profile_default(self):
        """Test la normalisation des profils avec valeur par défaut."""
        df = pd.DataFrame(self.n2f_users_data)
        result = normalize_n2f_users(df)

        # Vérification que les profils vides sont remplacés par la valeur par défaut
        expected_profiles = ["STANDARD", DEFAULT_PROFILE, "PREMIUM"]
        self.assertEqual(result[N2F_COL_PROFILE].tolist(), expected_profiles)

    def test_normalize_n2f_users_role_default(self):
        """Test la normalisation des rôles avec valeur par défaut."""
        df = pd.DataFrame(self.n2f_users_data)
        result = normalize_n2f_users(df)

        # Vérification que les rôles vides sont remplacés par la valeur par défaut
        expected_roles = ["USER", DEFAULT_ROLE, "ADMIN"]
        self.assertEqual(result[N2F_COL_ROLE].tolist(), expected_roles)

    def test_normalize_n2f_users_with_profile_mapping(self):
        """Test la normalisation avec mapping de profils."""
        df = pd.DataFrame(self.n2f_users_data)
        profile_mapping = {"standard": "Standard", "premium": "Premium"}

        result = normalize_n2f_users(df, profile_mapping=profile_mapping)

        # Vérification que le mapping est appliqué
        expected_profiles = ["Standard", DEFAULT_PROFILE, "Premium"]
        self.assertEqual(result[N2F_COL_PROFILE].tolist(), expected_profiles)

    def test_normalize_n2f_users_with_role_mapping(self):
        """Test la normalisation avec mapping de rôles."""
        df = pd.DataFrame(self.n2f_users_data)
        role_mapping = {"user": "Utilisateur", "admin": "Administrateur"}

        result = normalize_n2f_users(df, role_mapping=role_mapping)

        # Vérification que le mapping est appliqué
        expected_roles = ["Utilisateur", DEFAULT_ROLE, "Administrateur"]
        self.assertEqual(result[N2F_COL_ROLE].tolist(), expected_roles)

    def test_normalize_n2f_users_with_both_mappings(self):
        """Test la normalisation avec mapping de profils et rôles."""
        df = pd.DataFrame(self.n2f_users_data)
        profile_mapping = {"standard": "Standard", "premium": "Premium"}
        role_mapping = {"user": "Utilisateur", "admin": "Administrateur"}

        result = normalize_n2f_users(
            df, profile_mapping=profile_mapping, role_mapping=role_mapping
        )

        # Vérification que les deux mappings sont appliqués
        expected_profiles = ["Standard", DEFAULT_PROFILE, "Premium"]
        expected_roles = ["Utilisateur", DEFAULT_ROLE, "Administrateur"]

        self.assertEqual(result[N2F_COL_PROFILE].tolist(), expected_profiles)
        self.assertEqual(result[N2F_COL_ROLE].tolist(), expected_roles)

    def test_normalize_n2f_users_mapping_case_insensitive(self):
        """Test que le mapping est insensible à la casse."""
        df = pd.DataFrame(self.n2f_users_data)
        # Le mapping doit utiliser des clés en minuscules car la fonction convertit en
        # minuscules
        profile_mapping = {"standard": "Standard", "premium": "Premium"}

        result = normalize_n2f_users(df, profile_mapping=profile_mapping)

        # Vérification que le mapping fonctionne (les valeurs originales restent
        # inchangées si pas dans le mapping)
        expected_profiles = ["Standard", DEFAULT_PROFILE, "Premium"]
        self.assertEqual(result[N2F_COL_PROFILE].tolist(), expected_profiles)

    def test_normalize_n2f_users_with_nan_values(self):
        """Test la normalisation N2F avec des valeurs NaN."""
        # Ajout de valeurs NaN
        data_with_nan = self.n2f_users_data.copy()
        data_with_nan[N2F_COL_PROFILE] = cast(list, ["STANDARD", np.nan, "PREMIUM"])
        data_with_nan[N2F_COL_ROLE] = cast(list, ["USER", np.nan, "ADMIN"])

        df = pd.DataFrame(data_with_nan)
        result = normalize_n2f_users(df)

        # Vérification que les NaN sont gérés correctement
        expected_profiles = ["STANDARD", DEFAULT_PROFILE, "PREMIUM"]
        expected_roles = ["USER", DEFAULT_ROLE, "ADMIN"]

        self.assertEqual(result[N2F_COL_PROFILE].tolist(), expected_profiles)
        self.assertEqual(result[N2F_COL_ROLE].tolist(), expected_roles)

    def test_normalize_n2f_users_preserves_original_data(self):
        """Test que la normalisation N2F préserve les données originales."""
        df = pd.DataFrame(self.n2f_users_data)
        original_df = df.copy()
        result = normalize_n2f_users(df)

        # Vérification que le DataFrame original n'est pas modifié
        pd.testing.assert_frame_equal(df, original_df)

    def test_build_mapping_simple(self):
        """Test la construction d'un mapping simple."""
        df = pd.DataFrame(self.mapping_data)
        result = build_mapping(df)

        # Vérification du mapping
        expected_mapping = {
            "standard": "Standard",
            "standaard": "Standard",
            "premium": "Premium",
        }
        self.assertEqual(result, expected_mapping)

    def test_build_mapping_with_multiple_entries(self):
        """Test la construction d'un mapping avec plusieurs entrées."""
        mapping_data = {
            COL_NAMES: [
                [
                    {COL_CULTURE: CULTURE_FR, COL_VALUE: "Standard"},
                    {COL_CULTURE: CULTURE_NL, COL_VALUE: "Standaard"},
                ],
                [
                    {COL_CULTURE: CULTURE_FR, COL_VALUE: "Premium"},
                    {COL_CULTURE: CULTURE_NL, COL_VALUE: "Premium"},
                ],
                [
                    {COL_CULTURE: CULTURE_FR, COL_VALUE: "Admin"},
                    {COL_CULTURE: CULTURE_NL, COL_VALUE: "Beheerder"},
                ],
            ]
        }

        df = pd.DataFrame(mapping_data)
        result = build_mapping(df)

        # Vérification du mapping complet
        expected_mapping = {
            "standard": "Standard",
            "standaard": "Standard",
            "premium": "Premium",
            "admin": "Admin",
            "beheerder": "Admin",
        }
        self.assertEqual(result, expected_mapping)

    def test_build_mapping_without_french_value(self):
        """Test la construction d'un mapping sans valeur française."""
        mapping_data = {
            COL_NAMES: [[{COL_CULTURE: CULTURE_NL, COL_VALUE: "Standaard"}]]
        }

        df = pd.DataFrame(mapping_data)
        result = build_mapping(df)

        # Vérification qu'aucun mapping n'est créé sans valeur française
        self.assertEqual(result, {})

    def test_build_mapping_with_empty_names(self):
        """Test la construction d'un mapping avec des noms vides."""
        mapping_data = {
            COL_NAMES: [
                [
                    {COL_CULTURE: CULTURE_FR, COL_VALUE: ""},
                    {COL_CULTURE: CULTURE_NL, COL_VALUE: ""},
                ]
            ]
        }

        df = pd.DataFrame(mapping_data)
        result = build_mapping(df)

        # Vérification que les noms vides ne sont pas mappés (comportement amélioré)
        self.assertEqual(result, {})

    def test_build_mapping_with_whitespace(self):
        """Test la construction d'un mapping avec des espaces."""
        mapping_data = {
            COL_NAMES: [
                [
                    {COL_CULTURE: CULTURE_FR, COL_VALUE: " Standard "},
                    {COL_CULTURE: CULTURE_NL, COL_VALUE: " Standaard "},
                ]
            ]
        }

        df = pd.DataFrame(mapping_data)
        result = build_mapping(df)

        # Vérification que les espaces sont gérés correctement (les clés sont en
        # minuscules et sans espaces)
        # La fonction strip() supprime les espaces des clés et des valeurs
        expected_mapping = {"standard": "Standard", "standaard": "Standard"}
        self.assertEqual(result, expected_mapping)

    def test_normalize_agresso_users_empty_dataframe(self):
        """Test la normalisation d'un DataFrame vide."""
        df = pd.DataFrame()

        # Vérification que la fonction lève une ValueError pour un DataFrame vide
        with self.assertRaises(ValidationException) as context:
            normalize_agresso_users(df)
        self.assertIn("ne peut pas être vide", str(context.exception))

    def test_normalize_n2f_users_empty_dataframe(self):
        """Test la normalisation N2F d'un DataFrame vide."""
        df = pd.DataFrame()

        # Vérification que la fonction lève une ValueError pour un DataFrame vide
        with self.assertRaises(ValidationException) as context:
            normalize_n2f_users(df)
        self.assertIn("ne peut pas être vide", str(context.exception))

    def test_build_mapping_empty_dataframe(self):
        """Test la construction d'un mapping avec un DataFrame vide."""
        df = pd.DataFrame()
        result = build_mapping(df)

        # Vérification qu'un mapping vide est retourné
        self.assertEqual(result, {})

    def test_normalize_agresso_users_missing_columns(self):
        """Test la normalisation avec des colonnes manquantes."""
        # Création d'un DataFrame avec seulement quelques colonnes
        partial_data = {
            AGRESSO_COL_EMAIL: ["test@example.com"],
            AGRESSO_COL_MANAGER: ["manager@example.com"],
        }
        df = pd.DataFrame(partial_data)

        # Vérification que la fonction lève une ValueError pour les colonnes manquantes
        with self.assertRaises(ValidationException) as context:
            normalize_agresso_users(df)
        self.assertIn("Colonnes manquantes", str(context.exception))

    def test_normalize_n2f_users_missing_columns(self):
        """Test la normalisation N2F avec des colonnes manquantes."""
        # Création d'un DataFrame avec seulement quelques colonnes
        partial_data = {
            N2F_COL_EMAIL: ["test@example.com"],
            N2F_COL_PROFILE: ["STANDARD"],
        }
        df = pd.DataFrame(partial_data)

        # Vérification que la fonction lève une ValueError pour les colonnes manquantes
        with self.assertRaises(ValidationException) as context:
            normalize_n2f_users(df)
        self.assertIn("Colonnes manquantes", str(context.exception))


if __name__ == "__main__":
    unittest.main()
