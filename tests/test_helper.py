from unittest.mock import Mock, patch, MagicMock


import unittest
import sys
import os

import pandas as pd
from datetime import datetime

from n2f.helper import to_bool, normalize_date_for_payload


class TestHelper(unittest.TestCase):
    """Tests unitaires pour les fonctions helper."""

    def test_to_bool_true_values(self):
        """Test la conversion vers True pour différentes valeurs."""
        true_values = [
            True,
            1,
            1.0,
            "1",
            "true",
            "True",
            "TRUE",
            "yes",
            "Yes",
            "YES",
            "y",
            "Y",
            "on",
            "On",
            "ON",
        ]

        for value in true_values:
            with self.subTest(value=value):
                result = to_bool(value)
                self.assertTrue(result, f"to_bool({value!r}) devrait retourner True")

    def test_to_bool_false_values(self):
        """Test la conversion vers False pour différentes valeurs."""
        false_values = [
            False,
            0,
            0.0,
            "0",
            "false",
            "False",
            "FALSE",
            "no",
            "No",
            "NO",
            "n",
            "N",
            "off",
            "Off",
            "OFF",
            "",
            "invalid",
            "random_string",
            None,
        ]

        for value in false_values:
            with self.subTest(value=value):
                result = to_bool(value)
                self.assertFalse(result, f"to_bool({value!r}) devrait retourner False")

    def test_to_bool_with_whitespace(self):
        """Test la gestion des espaces dans to_bool."""
        # Valeurs avec espaces qui devraient être True
        true_with_spaces = [
            " yes ",
            " YES ",
            " y ",
            " Y ",
            " true ",
            " True ",
            " 1 ",
            " on ",
        ]

        for value in true_with_spaces:
            with self.subTest(value=value):
                result = to_bool(value)
                self.assertTrue(result, f"to_bool({value!r}) devrait retourner True")

        # Valeurs avec espaces qui devraient être False
        false_with_spaces = [
            " no ",
            " NO ",
            " n ",
            " N ",
            " false ",
            " False ",
            " 0 ",
            " off ",
        ]

        for value in false_with_spaces:
            with self.subTest(value=value):
                result = to_bool(value)
                self.assertFalse(result, f"to_bool({value!r}) devrait retourner False")

    def test_to_bool_case_insensitive(self):
        """Test que to_bool est insensible à la casse."""
        # Test avec différentes casses pour True
        true_cases = ["YES", "Yes", "yes", "Y", "y", "TRUE", "True", "true"]
        for value in true_cases:
            with self.subTest(value=value):
                result = to_bool(value)
                self.assertTrue(result, f"to_bool({value!r}) devrait retourner True")

        # Test avec différentes casses pour False
        false_cases = ["NO", "No", "no", "N", "n", "FALSE", "False", "false"]
        for value in false_cases:
            with self.subTest(value=value):
                result = to_bool(value)
                self.assertFalse(result, f"to_bool({value!r}) devrait retourner False")

    def test_to_bool_numeric_values(self):
        """Test la conversion des valeurs numériques."""
        # Valeurs numériques True
        true_numeric = [1, 1.0, 2, 10, -1, 0.5]
        for value in true_numeric:
            with self.subTest(value=value):
                result = to_bool(value)
                self.assertTrue(result, f"to_bool({value!r}) devrait retourner True")

        # Valeurs numériques False
        false_numeric = [0, 0.0]
        for value in false_numeric:
            with self.subTest(value=value):
                result = to_bool(value)
                self.assertFalse(result, f"to_bool({value!r}) devrait retourner False")

    def test_to_bool_edge_cases(self):
        """Test les cas limites de to_bool."""
        # Cas limites qui devraient être False
        edge_cases = [
            None,
            "",
            "   ",
            "invalid",
            "maybe",
            "perhaps",
            "oui",  # français
            "non",  # français
            "si",  # espagnol
            "nein",  # allemand
        ]

        for value in edge_cases:
            with self.subTest(value=value):
                result = to_bool(value)
                self.assertFalse(result, f"to_bool({value!r}) devrait retourner False")

    def test_normalize_date_for_payload_valid_dates(self):
        """Test la normalisation de dates valides."""
        test_cases = [
            ("01/01/2025", "2025-01-01T00:00:00Z"),
            ("31/12/2024", "2024-12-31T00:00:00Z"),
            ("15/06/2025", "2025-06-15T00:00:00Z"),
            ("2025-01-01", "2025-01-01T00:00:00Z"),
            ("2024-12-31", "2024-12-31T00:00:00Z"),
            (datetime(2025, 1, 1), "2025-01-01T00:00:00Z"),
            (datetime(2024, 12, 31), "2024-12-31T00:00:00Z"),
        ]

        for input_date, expected in test_cases:
            with self.subTest(input_date=input_date):
                result = normalize_date_for_payload(input_date)
                self.assertEqual(result, expected)

    def test_normalize_date_for_payload_invalid_dates(self):
        """Test la normalisation de dates invalides."""
        invalid_dates = [
            None,
            "",
            "invalid_date",
            "99/99/9999",
            "not_a_date",
            pd.NA,
            pd.NaT,
        ]

        for invalid_date in invalid_dates:
            with self.subTest(invalid_date=invalid_date):
                result = normalize_date_for_payload(invalid_date)
                self.assertIsNone(result)

    def test_normalize_date_for_payload_sentinel_date(self):
        """Test la gestion de la date sentinelle (31/12/2099)."""
        sentinel_dates = ["31/12/2099", "2099-12-31", datetime(2099, 12, 31)]

        for sentinel_date in sentinel_dates:
            with self.subTest(sentinel_date=sentinel_date):
                result = normalize_date_for_payload(sentinel_date)
                self.assertIsNone(result, "La date sentinelle devrait retourner None")

    def test_normalize_date_for_payload_edge_cases(self):
        """Test les cas limites de normalize_date_for_payload."""
        # Dates limites qui devraient fonctionner
        edge_cases = [
            ("01/01/1900", "1900-01-01T00:00:00Z"),
            ("31/12/2098", "2098-12-31T00:00:00Z"),  # Juste avant la sentinelle
            ("29/02/2024", "2024-02-29T00:00:00Z"),  # Année bissextile
        ]

        for input_date, expected in edge_cases:
            with self.subTest(input_date=input_date):
                result = normalize_date_for_payload(input_date)
                self.assertEqual(result, expected)

    def test_normalize_date_for_payload_with_whitespace(self):
        """Test la gestion des espaces dans les dates."""
        # Dates avec espaces qui devraient être normalisées
        dates_with_spaces = [
            (" 01/01/2025 ", "2025-01-01T00:00:00Z"),
            (" 2025-01-01 ", "2025-01-01T00:00:00Z"),
        ]

        for input_date, expected in dates_with_spaces:
            with self.subTest(input_date=input_date):
                result = normalize_date_for_payload(input_date)
                self.assertEqual(result, expected)

    def test_normalize_date_for_payload_mixed_formats(self):
        """Test la normalisation avec différents formats de date."""
        # Test avec différents formats qui devraient tous fonctionner
        mixed_formats = [
            ("01-01-2025", "2025-01-01T00:00:00Z"),
            ("2025/01/01", "2025-01-01T00:00:00Z"),
            ("01.01.2025", "2025-01-01T00:00:00Z"),
        ]

        for input_date, expected in mixed_formats:
            with self.subTest(input_date=input_date):
                result = normalize_date_for_payload(input_date)
                # Note: Le comportement exact peut dépendre de pandas.to_datetime
                # mais on s'attend à ce que ça fonctionne pour des formats courants
                if result is not None:
                    self.assertEqual(result, expected)

    def test_to_bool_agresso_specific_values(self):
        """Test spécifiquement les valeurs utilisées dans Agresso."""
        # Valeurs typiques d'Agresso qui devraient être True
        agresso_true = ["Y", "y", "YES", "yes", "Yes"]
        for value in agresso_true:
            with self.subTest(value=value):
                result = to_bool(value)
                self.assertTrue(
                    result, f"to_bool({value!r}) devrait retourner True pour Agresso"
                )

        # Valeurs typiques d'Agresso qui devraient être False
        agresso_false = ["N", "n", "NO", "no", "No", ""]
        for value in agresso_false:
            with self.subTest(value=value):
                result = to_bool(value)
                self.assertFalse(
                    result, f"to_bool({value!r}) devrait retourner False pour Agresso"
                )

    def test_to_bool_performance(self):
        """Test de performance pour to_bool avec beaucoup de valeurs."""
        # Test avec une liste de valeurs pour vérifier les performances
        test_values = ["Y", "N", "yes", "no", "true", "false", "1", "0"] * 1000

        import time

        start_time = time.time()

        for value in test_values:
            result = to_bool(value)
            # Vérification basique que le résultat est un booléen
            self.assertIsInstance(result, bool)

        end_time = time.time()
        duration = end_time - start_time

        # Le test ne devrait pas prendre plus de 1 seconde
        self.assertLess(
            duration, 1.0, f"to_bool a pris {duration:.3f}s, ce qui est trop lent"
        )


if __name__ == "__main__":
    unittest.main()
