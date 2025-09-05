"""
Tests unitaires pour le module src/n2f/process/axe.py.

Ce module teste les fonctions de traitement des axes N2F.
"""

import unittest
from unittest.mock import Mock, patch
import pandas as pd

from n2f.process.axe import (
    get_axes,
    build_axe_payload,
    create_axes,
    update_axes,
    delete_axes,
)
from n2f.api_result import ApiResult
from core.exceptions import SyncException


class TestGetAxes(unittest.TestCase):
    """Tests pour la fonction get_axes."""

    def test_get_axes_success(self):
        """Test de récupération réussie des axes."""
        mock_client = Mock()
        mock_df = pd.DataFrame(
            {"code": ["PROJ1", "PROJ2"], "name": ["Project 1", "Project 2"]}
        )
        mock_client.get_axe_values.return_value = mock_df

        result = get_axes(mock_client, "axe_id_123", "company_id_456")

        mock_client.get_axe_values.assert_called_once_with(
            "company_id_456", "axe_id_123"
        )
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)


class TestBuildAxePayload(unittest.TestCase):
    """Tests pour la fonction build_axe_payload."""

    def test_build_axe_payload_sandbox_true(self):
        """Test de construction du payload avec sandbox=True."""
        project = pd.Series(
            {
                "code": "PROJ1",
                "name": "Test Project",
                "client": "CLIENT1",
                "description": "Test Description",
            }
        )

        with patch(
            "n2f.process.axe.create_project_upsert_payload"
        ) as mock_create_payload:
            mock_payload = {"code": "PROJ1", "name": "Test Project", "sandbox": True}
            mock_create_payload.return_value = mock_payload

            result = build_axe_payload(project, True)

            mock_create_payload.assert_called_once_with(project.to_dict(), True)
            self.assertEqual(result, mock_payload)

    def test_build_axe_payload_sandbox_false(self):
        """Test de construction du payload avec sandbox=False."""
        project = pd.Series(
            {
                "code": "PROJ2",
                "name": "Production Project",
                "client": "CLIENT2",
                "description": "Production Description",
            }
        )

        with patch(
            "n2f.process.axe.create_project_upsert_payload"
        ) as mock_create_payload:
            mock_payload = {
                "code": "PROJ2",
                "name": "Production Project",
                "sandbox": False,
            }
            mock_create_payload.return_value = mock_payload

            result = build_axe_payload(project, False)

            mock_create_payload.assert_called_once_with(project.to_dict(), False)
            self.assertEqual(result, mock_payload)


class TestCreateAxes(unittest.TestCase):
    """Tests pour la fonction create_axes."""

    def setUp(self):
        """Configuration initiale pour chaque test."""
        self.mock_client = Mock()
        self.df_agresso_projects = pd.DataFrame(
            {
                "code": ["PROJ1", "PROJ2", "PROJ3"],
                "name": ["Project 1", "Project 2", "Project 3"],
                "client": ["CLIENT1", "CLIENT2", "CLIENT3"],
                "description": ["Desc 1", "Desc 2", "Desc 3"],
            }
        )
        self.df_n2f_projects = pd.DataFrame(
            {"code": ["PROJ1"], "name": ["Project 1"], "uuid": ["uuid1"]}
        )
        self.df_n2f_companies = pd.DataFrame(
            {
                "code": ["CLIENT1", "CLIENT2", "CLIENT3"],
                "uuid": ["company_uuid1", "company_uuid2", "company_uuid3"],
            }
        )

    def test_create_axes_empty_agresso_projects(self):
        """Test de création avec DataFrame Agresso vide."""
        empty_df = pd.DataFrame()
        result_df, status_col = create_axes(
            self.mock_client,
            "axe_id",
            empty_df,
            self.df_n2f_projects,
            self.df_n2f_companies,
            True,
        )

        self.assertTrue(result_df.empty)
        self.assertEqual(status_col, "created")

    def test_create_axes_all_projects_exist(self):
        """Test de création quand tous les projets existent déjà."""
        result_df, status_col = create_axes(
            self.mock_client,
            "axe_id",
            self.df_agresso_projects,
            self.df_agresso_projects,
            self.df_n2f_companies,
            True,
        )

        self.assertTrue(result_df.empty)
        self.assertEqual(status_col, "created")

    def test_create_axes_success(self):
        """Test de création réussie d'axes."""
        # Mock build_axe_payload
        with patch("n2f.process.axe.build_axe_payload") as mock_build_payload:
            mock_payload = {"code": "PROJ2", "name": "Project 2"}
            mock_build_payload.return_value = mock_payload

            # Mock upsert_axe_value
            mock_result = ApiResult.success_result(
                "Created", 200, 100.0, "create", "axe", "PROJ2", "projects"
            )
            self.mock_client.upsert_axe_value.return_value = mock_result

            # Mock l'import dynamique de lookup_company_id
            with patch("n2f.process.company.lookup_company_id") as mock_lookup:
                mock_lookup.return_value = "company_uuid2"

                result_df, status_col = create_axes(
                    self.mock_client,
                    "axe_id",
                    self.df_agresso_projects,
                    self.df_n2f_projects,
                    self.df_n2f_companies,
                    True,
                )

                self.assertFalse(result_df.empty)
                self.assertEqual(status_col, "created")
                self.assertEqual(len(result_df), 2)  # PROJ2 et PROJ3
                self.assertTrue(all(result_df[status_col]))

    def test_create_axes_company_not_found(self):
        """Test de création avec entreprise non trouvée."""
        with patch("n2f.process.axe.logging.error") as mock_log_error:
            # Mock l'import dynamique de lookup_company_id
            with patch("n2f.process.axe.lookup_company_id") as mock_lookup:
                mock_lookup.return_value = None

                result_df, status_col = create_axes(
                    self.mock_client,
                    "axe_id",
                    self.df_agresso_projects,
                    self.df_n2f_projects,
                    self.df_n2f_companies,
                    True,
                )

                self.assertFalse(result_df.empty)
                self.assertEqual(status_col, "created")
                # Vérifier que log_error a été appelé
                mock_log_error.assert_called()

    def test_create_axes_api_exception(self):
        """Test de création avec exception API."""
        with patch("n2f.process.axe.build_axe_payload") as mock_build_payload:
            mock_payload = {"code": "PROJ2", "name": "Project 2"}
            mock_build_payload.return_value = mock_payload

            # Mock upsert_axe_value pour lever une exception
            self.mock_client.upsert_axe_value.side_effect = SyncException("API Error")

            with patch("logging.error") as mock_log_error:
                # Mock l'import dynamique de lookup_company_id
                with patch("n2f.process.company.lookup_company_id") as mock_lookup:
                    mock_lookup.return_value = "company_uuid2"

                    result_df, status_col = create_axes(
                        self.mock_client,
                        "axe_id",
                        self.df_agresso_projects,
                        self.df_n2f_projects,
                        self.df_n2f_companies,
                        True,
                    )

                    self.assertFalse(result_df.empty)
                    self.assertEqual(status_col, "created")
                    # Vérifier que log_error a été appelé
                    mock_log_error.assert_called()


class TestUpdateAxes(unittest.TestCase):
    """Tests pour la fonction update_axes."""

    def setUp(self):
        """Configuration initiale pour chaque test."""
        self.mock_client = Mock()
        self.df_agresso_projects = pd.DataFrame(
            {
                "code": ["PROJ1", "PROJ2"],
                "name": ["Project 1 Updated", "Project 2 Updated"],
                "client": ["CLIENT1", "CLIENT2"],
                "description": ["Desc 1 Updated", "Desc 2 Updated"],
            }
        )
        self.df_n2f_projects = pd.DataFrame(
            {
                "code": ["PROJ1", "PROJ2"],
                "name": ["Project 1", "Project 2"],
                "uuid": ["uuid1", "uuid2"],
            }
        )
        self.df_n2f_companies = pd.DataFrame(
            {"code": ["CLIENT1", "CLIENT2"], "uuid": ["company_uuid1", "company_uuid2"]}
        )

    def test_update_axes_empty_agresso_projects(self):
        """Test de mise à jour avec DataFrame Agresso vide."""
        empty_df = pd.DataFrame()
        result_df, status_col = update_axes(
            self.mock_client,
            "axe_id",
            empty_df,
            self.df_n2f_projects,
            self.df_n2f_companies,
            True,
        )

        self.assertTrue(result_df.empty)
        self.assertEqual(status_col, "updated")

    def test_update_axes_empty_n2f_projects(self):
        """Test de mise à jour avec DataFrame N2F vide."""
        empty_df = pd.DataFrame()
        result_df, status_col = update_axes(
            self.mock_client,
            "axe_id",
            self.df_agresso_projects,
            empty_df,
            self.df_n2f_companies,
            True,
        )

        self.assertTrue(result_df.empty)
        self.assertEqual(status_col, "updated")

    def test_update_axes_no_changes(self):
        """Test de mise à jour sans changements."""
        # Créer des projets identiques
        df_agresso_identical = pd.DataFrame(
            {
                "code": ["PROJ1"],
                "name": ["Project 1"],  # Même nom
                "client": ["CLIENT1"],
                "description": ["Desc 1"],
            }
        )

        with patch("n2f.process.axe.has_payload_changes") as mock_has_changes:
            mock_has_changes.return_value = False

            result_df, status_col = update_axes(
                self.mock_client,
                "axe_id",
                df_agresso_identical,
                self.df_n2f_projects,
                self.df_n2f_companies,
                True,
            )

            self.assertTrue(result_df.empty)
            self.assertEqual(status_col, "updated")

    def test_update_axes_success(self):
        """Test de mise à jour réussie."""
        with patch("n2f.process.axe.has_payload_changes") as mock_has_changes:
            mock_has_changes.return_value = True

            with patch("n2f.process.axe.build_axe_payload") as mock_build_payload:
                mock_payload = {"code": "PROJ1", "name": "Project 1 Updated"}
                mock_build_payload.return_value = mock_payload

                mock_result = ApiResult.success_result(
                    "Updated", 200, 100.0, "update", "axe", "PROJ1", "projects"
                )
                self.mock_client.upsert_axe_value.return_value = mock_result

                # Mock l'import dynamique de lookup_company_id
                with patch("n2f.process.company.lookup_company_id") as mock_lookup:
                    mock_lookup.return_value = "company_uuid1"

                    result_df, status_col = update_axes(
                        self.mock_client,
                        "axe_id",
                        self.df_agresso_projects,
                        self.df_n2f_projects,
                        self.df_n2f_companies,
                        True,
                    )

                    self.assertFalse(result_df.empty)
                    self.assertEqual(status_col, "updated")
                    self.assertEqual(len(result_df), 2)
                    self.assertTrue(all(result_df[status_col]))

    def test_update_axes_company_not_found(self):
        """Test de mise à jour avec entreprise non trouvée."""
        with patch("n2f.process.axe.has_payload_changes") as mock_has_changes:
            mock_has_changes.return_value = True

            with patch("n2f.process.axe.logging.error") as mock_log_error:
                # Mock l'import dynamique de lookup_company_id
                with patch("n2f.process.axe.lookup_company_id") as mock_lookup:
                    mock_lookup.return_value = None

                    result_df, status_col = update_axes(
                        self.mock_client,
                        "axe_id",
                        self.df_agresso_projects,
                        self.df_n2f_projects,
                        self.df_n2f_companies,
                        True,
                    )

                    self.assertFalse(result_df.empty)
                    self.assertEqual(status_col, "updated")
                    mock_log_error.assert_called()

    def test_update_axes_api_exception(self):
        """Test de mise à jour avec exception API."""
        with patch("n2f.process.axe.has_payload_changes") as mock_has_changes:
            mock_has_changes.return_value = True

            with patch("n2f.process.axe.build_axe_payload") as mock_build_payload:
                mock_payload = {"code": "PROJ1", "name": "Project 1 Updated"}
                mock_build_payload.return_value = mock_payload

                self.mock_client.upsert_axe_value.side_effect = SyncException(
                    "API Error"
                )

                with patch("logging.error") as mock_log_error:
                    # Mock l'import dynamique de lookup_company_id
                    with patch("n2f.process.company.lookup_company_id") as mock_lookup:
                        mock_lookup.return_value = "company_uuid1"

                        result_df, status_col = update_axes(
                            self.mock_client,
                            "axe_id",
                            self.df_agresso_projects,
                            self.df_n2f_projects,
                            self.df_n2f_companies,
                            True,
                        )

                        self.assertFalse(result_df.empty)
                        self.assertEqual(status_col, "updated")
                        mock_log_error.assert_called()


class TestDeleteAxes(unittest.TestCase):
    """Tests pour la fonction delete_axes."""

    def setUp(self):
        """Configuration initiale pour chaque test."""
        self.mock_client = Mock()
        self.df_agresso_projects = pd.DataFrame(
            {
                "code": ["PROJ1"],
                "name": ["Project 1"],
                "client": ["CLIENT1"],
                "description": ["Desc 1"],
            }
        )
        self.df_n2f_projects = pd.DataFrame(
            {
                "code": ["PROJ1", "PROJ2", "PROJ3"],
                "name": ["Project 1", "Project 2", "Project 3"],
                "uuid": ["uuid1", "uuid2", "uuid3"],
                "company_id": ["company_uuid1", "company_uuid2", "company_uuid3"],
            }
        )

    def test_delete_axes_empty_n2f_projects(self):
        """Test de suppression avec DataFrame N2F vide."""
        empty_df = pd.DataFrame()
        result_df, status_col = delete_axes(
            self.mock_client,
            "axe_id",
            self.df_agresso_projects,
            empty_df,
            pd.DataFrame(),
            True,
        )

        self.assertTrue(result_df.empty)
        self.assertEqual(status_col, "deleted")

    def test_delete_axes_no_projects_to_delete(self):
        """Test de suppression quand aucun projet à supprimer."""
        result_df, status_col = delete_axes(
            self.mock_client,
            "axe_id",
            self.df_agresso_projects,
            self.df_agresso_projects,
            pd.DataFrame(),
            True,
        )

        self.assertTrue(result_df.empty)
        self.assertEqual(status_col, "deleted")

    def test_delete_axes_success(self):
        """Test de suppression réussie."""
        mock_result = ApiResult.success_result(
            "Deleted", 200, 100.0, "delete", "axe", "PROJ2", "projects"
        )
        self.mock_client.delete_axe_value.return_value = mock_result

        result_df, status_col = delete_axes(
            self.mock_client,
            "axe_id",
            self.df_agresso_projects,
            self.df_n2f_projects,
            pd.DataFrame(),
            True,
        )

        self.assertFalse(result_df.empty)
        self.assertEqual(status_col, "deleted")
        self.assertEqual(len(result_df), 2)  # PROJ2 et PROJ3
        self.assertTrue(all(result_df[status_col]))

    def test_delete_axes_missing_company_id(self):
        """Test de suppression avec company_id manquant."""
        df_n2f_projects_no_company = pd.DataFrame(
            {
                "code": ["PROJ1", "PROJ2"],
                "name": ["Project 1", "Project 2"],
                "uuid": ["uuid1", "uuid2"],
                # Pas de company_id
            }
        )

        with patch("logging.error") as mock_log_error:
            result_df, status_col = delete_axes(
                self.mock_client,
                "axe_id",
                self.df_agresso_projects,
                df_n2f_projects_no_company,
                pd.DataFrame(),
                True,
            )

            self.assertFalse(result_df.empty)
            self.assertEqual(status_col, "deleted")
            mock_log_error.assert_called()

    def test_delete_axes_api_exception(self):
        """Test de suppression avec exception API."""
        self.mock_client.delete_axe_value.side_effect = SyncException("API Error")

        with patch("logging.error") as mock_log_error:
            result_df, status_col = delete_axes(
                self.mock_client,
                "axe_id",
                self.df_agresso_projects,
                self.df_n2f_projects,
                pd.DataFrame(),
                True,
            )

            self.assertFalse(result_df.empty)
            self.assertEqual(status_col, "deleted")
            mock_log_error.assert_called()


if __name__ == "__main__":
    unittest.main()
