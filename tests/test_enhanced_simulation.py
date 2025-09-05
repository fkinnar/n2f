#!/usr/bin/env python3
"""
Tests for the enhanced simulation system.
"""

import unittest
from unittest.mock import Mock
import pandas as pd

from core import SyncContext
from n2f.client import N2fApiClient
from n2f.simulation import (
    SimulationDataGenerator,
    SimulationConfig,
    EnhancedSimulator,
    get_simulator,
)
from n2f.simulation_config import apply_simulation_scenario


class TestSimulationDataGenerator(unittest.TestCase):
    """Test the simulation data generator."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = SimulationDataGenerator()

    def test_generate_user_data(self):
        """Test user data generation."""
        users = self.generator.generate_user_data(3)

        self.assertEqual(len(users), 3)
        self.assertIn("id", users[0])
        self.assertIn("mail", users[0])
        self.assertIn("firstName", users[0])
        self.assertIn("lastName", users[0])
        self.assertTrue(users[0]["mail"].endswith("@example.com"))

    def test_generate_company_data(self):
        """Test company data generation."""
        companies = self.generator.generate_company_data(2)

        self.assertEqual(len(companies), 2)
        self.assertIn("id", companies[0])
        self.assertIn("uuid", companies[0])
        self.assertIn("name", companies[0])
        self.assertIn("code", companies[0])
        self.assertTrue(companies[0]["code"].startswith("COMP_"))

    def test_generate_role_data(self):
        """Test role data generation."""
        roles = self.generator.generate_role_data(5)

        self.assertEqual(len(roles), 5)
        self.assertIn("id", roles[0])
        self.assertIn("name", roles[0])
        self.assertIn("description", roles[0])
        self.assertIn("permissions", roles[0])

    def test_generate_profile_data(self):
        """Test profile data generation."""
        profiles = self.generator.generate_profile_data(3)

        self.assertEqual(len(profiles), 3)
        self.assertIn("id", profiles[0])
        self.assertIn("name", profiles[0])
        self.assertIn("description", profiles[0])
        self.assertIn("features", profiles[0])

    def test_generate_axe_data(self):
        """Test axe data generation."""
        company_id = "test_company_123"
        axes = self.generator.generate_axe_data(company_id, 2)

        self.assertEqual(len(axes), 2)
        self.assertIn("id", axes[0])
        self.assertIn("uuid", axes[0])
        self.assertIn("code", axes[0])
        self.assertIn("name", axes[0])
        self.assertEqual(axes[0]["companyId"], company_id)


class TestEnhancedSimulator(unittest.TestCase):
    """Test the enhanced simulator."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = SimulationConfig(
            simulate_errors=False,
            error_rate=0.0,
            response_delay_ms=0.0,
            data_size_multiplier=1.0,
        )
        self.simulator = EnhancedSimulator(self.config)

    def test_simulate_get_response_users(self):
        """Test GET simulation for users."""
        users = self.simulator.simulate_get_response("users", 0, 5)

        self.assertIsInstance(users, list)
        self.assertGreater(len(users), 0)
        self.assertIn("id", users[0])
        self.assertIn("mail", users[0])

    def test_simulate_get_response_companies(self):
        """Test GET simulation for companies."""
        companies = self.simulator.simulate_get_response("companies", 0, 3)

        self.assertIsInstance(companies, list)
        self.assertGreater(len(companies), 0)
        self.assertIn("id", companies[0])
        self.assertIn("name", companies[0])

    def test_simulate_upsert_response(self):
        """Test upsert simulation."""
        payload = {"mail": "test@example.com", "firstName": "Test"}
        result = self.simulator.simulate_upsert_response(
            "/users", payload, "create", "user", "test@example.com", "users"
        )

        self.assertTrue(result.success)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.action_type, "create")
        self.assertEqual(result.object_type, "user")
        self.assertIsNotNone(result.response_data)

    def test_simulate_delete_response(self):
        """Test delete simulation."""
        result = self.simulator.simulate_delete_response(
            "/users", "test@example.com", "delete", "user", "users"
        )

        self.assertTrue(result.success)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.action_type, "delete")
        self.assertEqual(result.object_type, "user")

    def test_simulation_logging(self):
        """Test simulation logging."""
        # Clear log first
        self.simulator.clear_simulation_log()

        # Perform some operations
        self.simulator.simulate_get_response("users", 0, 1)
        self.simulator.simulate_upsert_response("/users", {}, "create")

        # Check log
        log = self.simulator.get_simulation_log()
        self.assertEqual(len(log), 2)
        self.assertEqual(log[0]["operation"], "GET")
        self.assertEqual(log[1]["operation"], "UPSERT")


class TestSimulationConfig(unittest.TestCase):
    """Test simulation configuration scenarios."""

    def test_apply_basic_scenario(self):
        """Test basic simulation scenario."""
        apply_simulation_scenario("basic")
        simulator = get_simulator()

        # Should have basic configuration
        self.assertFalse(simulator.config.simulate_errors)
        self.assertEqual(simulator.config.error_rate, 0.0)
        self.assertEqual(simulator.config.data_size_multiplier, 1.0)

    def test_apply_stress_test_scenario(self):
        """Test stress test simulation scenario."""
        apply_simulation_scenario("stress_test", data_multiplier=50.0)
        simulator = get_simulator()

        # Should have stress test configuration
        self.assertEqual(simulator.config.data_size_multiplier, 50.0)
        self.assertFalse(simulator.config.simulate_errors)

    def test_apply_error_testing_scenario(self):
        """Test error testing simulation scenario."""
        apply_simulation_scenario("error_testing", error_rate=0.5)
        simulator = get_simulator()

        # Should have error testing configuration
        self.assertTrue(simulator.config.simulate_errors)
        self.assertEqual(simulator.config.error_rate, 0.5)

    def test_apply_realistic_scenario(self):
        """Test realistic simulation scenario."""
        apply_simulation_scenario("realistic")
        simulator = get_simulator()

        # Should have realistic configuration
        self.assertFalse(simulator.config.simulate_errors)
        self.assertEqual(simulator.config.response_delay_ms, 100.0)
        self.assertEqual(simulator.config.data_size_multiplier, 5.0)

    def test_unknown_scenario(self):
        """Test error handling for unknown scenario."""
        with self.assertRaises(ValueError):
            apply_simulation_scenario("unknown_scenario")


class TestN2fApiClientWithSimulation(unittest.TestCase):
    """Test N2fApiClient with enhanced simulation."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock context with simulation enabled
        self.mock_context = Mock(spec=SyncContext)
        self.mock_context.client_id = "test_client_id"
        self.mock_context.client_secret = "test_client_secret"

        # Mock N2F config
        self.mock_n2f_config = Mock()
        self.mock_n2f_config.base_urls = "https://api.n2f.test"
        self.mock_n2f_config.simulate = True

        self.mock_context.get_config_value.return_value = self.mock_n2f_config

        # Setup basic simulation
        apply_simulation_scenario("basic")

        # Create client
        self.client = N2fApiClient(self.mock_context)

    def test_get_users_with_simulation(self):
        """Test getting users with enhanced simulation."""
        users_df = self.client.get_users()

        self.assertIsInstance(users_df, pd.DataFrame)
        self.assertGreater(len(users_df), 0)
        self.assertIn("id", users_df.columns)
        self.assertIn("mail", users_df.columns)

    def test_get_companies_with_simulation(self):
        """Test getting companies with enhanced simulation."""
        companies_df = self.client.get_companies()

        self.assertIsInstance(companies_df, pd.DataFrame)
        self.assertGreater(len(companies_df), 0)
        self.assertIn("id", companies_df.columns)
        self.assertIn("name", companies_df.columns)

    def test_create_user_with_simulation(self):
        """Test creating user with enhanced simulation."""
        payload = {
            "mail": "test.user@example.com",
            "firstName": "Test",
            "lastName": "User",
        }

        result = self.client.create_user(payload)

        self.assertTrue(result.success)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.action_type, "create")
        self.assertEqual(result.object_type, "user")
        self.assertIsNotNone(result.response_data)

    def test_update_user_with_simulation(self):
        """Test updating user with enhanced simulation."""
        payload = {
            "mail": "test.user@example.com",
            "firstName": "Updated",
            "lastName": "User",
        }

        result = self.client.update_user(payload)

        self.assertTrue(result.success)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.action_type, "update")
        self.assertEqual(result.object_type, "user")

    def test_delete_user_with_simulation(self):
        """Test deleting user with enhanced simulation."""
        result = self.client.delete_user("test.user@example.com")

        self.assertTrue(result.success)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.action_type, "delete")
        self.assertEqual(result.object_type, "user")

    def test_get_custom_axes_with_simulation(self):
        """Test getting custom axes with enhanced simulation."""
        company_id = "test_company_123"
        axes_df = self.client.get_custom_axes(company_id)

        self.assertIsInstance(axes_df, pd.DataFrame)
        self.assertGreater(len(axes_df), 0)
        self.assertIn("id", axes_df.columns)
        self.assertIn("code", axes_df.columns)


if __name__ == "__main__":
    unittest.main()
