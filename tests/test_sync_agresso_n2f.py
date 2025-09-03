import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import importlib

# Add the python directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

# Dynamically import the module with hyphens in its name
sync_script = importlib.import_module("sync-agresso-n2f")


class TestSyncAgressoN2F(unittest.TestCase):

    @patch.dict(
        os.environ,
        {
            "AGRESSO_DB_USER": "test",
            "AGRESSO_DB_PASSWORD": "test",
            "N2F_CLIENT_ID": "test",
            "N2F_CLIENT_SECRET": "test",
        },
        clear=True,
    )
    def test_validate_environment_variables_success(self):
        """Test that validation passes when all env vars are set."""
        try:
            sync_script.validate_environment_variables()
        except ValueError:
            self.fail(
                "validate_environment_variables() raised ValueError unexpectedly!"
            )

    @patch.dict(
        os.environ,
        {
            "AGRESSO_DB_USER": "test",
            "AGRESSO_DB_PASSWORD": "test",
            "N2F_CLIENT_ID": "test",
            # N2F_CLIENT_SECRET is missing
        },
        clear=True,
    )
    def test_validate_environment_variables_failure(self):
        """Test that validation fails when an env var is missing."""
        with self.assertRaises(ValueError) as cm:
            sync_script.validate_environment_variables()
        self.assertIn("N2F_CLIENT_SECRET", str(cm.exception))

    def test_create_arg_parser(self):
        """Test the argument parser creation and default values."""
        parser = sync_script.create_arg_parser()
        args = parser.parse_args([])  # No arguments provided
        self.assertEqual(args.config, "dev")
        self.assertEqual(args.scope, ["all"])
        self.assertFalse(args.create)
        self.assertFalse(args.delete)
        self.assertFalse(args.update)

    @patch.object(sync_script, "create_arg_parser")
    @patch.object(sync_script, "ConfigLoader")
    @patch.object(sync_script, "validate_environment_variables")
    @patch.object(sync_script, "SyncOrchestrator")
    @patch.object(sync_script, "load_dotenv")
    def test_main_flow_no_action_args(
        self,
        mock_load_dotenv,
        mock_orchestrator,
        mock_validate_env,
        mock_config_loader,
        mock_parser,
    ):
        """
        Test the main function flow with no action arguments, defaulting to
        create/update.
        """
        # Setup mocks
        mock_args = MagicMock()
        mock_args.create = False
        mock_args.delete = False
        mock_args.update = False
        mock_args.config = "dev"
        mock_parser.return_value.parse_args.return_value = mock_args

        mock_config = MagicMock()
        mock_config.api.sandbox = True
        mock_config_loader.return_value.load.return_value = mock_config

        # Call main
        sync_script.main()

        # Assertions
        mock_validate_env.assert_called_once()
        mock_load_dotenv.assert_called_once()
        mock_orchestrator.assert_called_once()

        # Check that create and update were defaulted to True
        final_args = mock_orchestrator.call_args[0][1]
        self.assertTrue(final_args.create)
        self.assertTrue(final_args.update)
        self.assertFalse(final_args.delete)


if __name__ == "__main__":
    unittest.main()
