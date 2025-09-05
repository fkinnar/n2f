#!/usr/bin/env python3
"""
Example script demonstrating the enhanced simulation system.

This script shows how to use the enhanced simulation features to test
the N2F API integration with realistic data without making actual HTTP calls.
"""

import logging

from core import SyncContext
from n2f.client import N2fApiClient
from n2f.simulation import SimulationConfig, configure_simulation


def setup_logging() -> None:
    """Configure logging for the example."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def create_mock_context() -> SyncContext:
    """Create a mock SyncContext for testing."""
    import argparse
    from pathlib import Path

    # Mock configuration
    mock_config = {
        "n2f": {
            "base_urls": "https://api.n2f.test",
            "simulate": True,  # Enable simulation
        }
    }

    # Create mock args
    mock_args = argparse.Namespace()
    mock_args.simulate = True

    return SyncContext(
        args=mock_args,
        config=mock_config,
        base_dir=Path("test_data"),
        db_user="test_user",
        db_password="test_password",
        client_id="test_client",
        client_secret="test_secret",
    )


def demonstrate_basic_simulation() -> None:
    """Demonstrate basic simulation functionality."""
    print("\n=== Basic Simulation Demo ===")

    # Create client with simulation enabled
    context = create_mock_context()
    client = N2fApiClient(context)

    # Test GET operations with realistic data
    print("Fetching users...")
    users_df = client.get_users()
    print(f"Retrieved {len(users_df)} users")
    if not users_df.empty:
        print("Sample user data:")
        print(users_df.head(2).to_string())

    print("\nFetching companies...")
    companies_df = client.get_companies()
    print(f"Retrieved {len(companies_df)} companies")
    if not companies_df.empty:
        print("Sample company data:")
        print(companies_df.head(2).to_string())

    print("\nFetching roles...")
    roles_df = client.get_roles()
    print(f"Retrieved {len(roles_df)} roles")
    if not roles_df.empty:
        print("Sample role data:")
        print(roles_df.head(2).to_string())


def demonstrate_upsert_simulation() -> None:
    """Demonstrate upsert operations in simulation mode."""
    print("\n=== Upsert Simulation Demo ===")

    context = create_mock_context()
    client = N2fApiClient(context)

    # Test user creation
    user_payload = {
        "mail": "new.user@example.com",
        "firstName": "New",
        "lastName": "User",
        "profile": "Standard",
        "role": "User",
    }

    print("Creating user...")
    result = client.create_user(user_payload)
    print(f"User creation result: {result.success}")
    print(f"Message: {result.message}")
    print(f"Status code: {result.status_code}")
    if result.response_data:
        print(f"Response data: {result.response_data}")

    # Test user update
    print("\nUpdating user...")
    result = client.update_user(user_payload)
    print(f"User update result: {result.success}")
    print(f"Message: {result.message}")


def demonstrate_error_simulation() -> None:
    """Demonstrate error simulation capabilities."""
    print("\n=== Error Simulation Demo ===")

    # Configure simulation with error simulation enabled
    config = SimulationConfig(
        simulate_errors=True,
        error_rate=0.3,  # 30% chance of error
        response_delay_ms=100.0,
    )
    configure_simulation(config)

    context = create_mock_context()
    client = N2fApiClient(context)

    # Try multiple operations to see some errors
    for i in range(5):
        user_payload = {
            "mail": f"test.user.{i}@example.com",
            "firstName": f"Test{i}",
            "lastName": "User",
        }

        result = client.create_user(user_payload)
        status = "SUCCESS" if result.success else "ERROR"
        print(f"Operation {i + 1}: {status} - {result.message}")
        if not result.success:
            print(f"  Error details: {result.error_details}")


def demonstrate_large_dataset_simulation() -> None:
    """Demonstrate simulation with large datasets."""
    print("\n=== Large Dataset Simulation Demo ===")

    # Configure simulation for large datasets
    config = SimulationConfig(
        data_size_multiplier=10.0, response_delay_ms=50.0  # Generate 10x more data
    )
    configure_simulation(config)

    context = create_mock_context()
    client = N2fApiClient(context)

    print("Fetching large user dataset...")
    users_df = client.get_users()
    print(f"Retrieved {len(users_df)} users (simulated large dataset)")

    print("\nFetching large company dataset...")
    companies_df = client.get_companies()
    print(f"Retrieved {len(companies_df)} companies (simulated large dataset)")


def demonstrate_custom_axes_simulation() -> None:
    """Demonstrate custom axes simulation."""
    print("\n=== Custom Axes Simulation Demo ===")

    context = create_mock_context()
    client = N2fApiClient(context)

    # First get companies to have company IDs
    companies_df = client.get_companies()
    if not companies_df.empty:
        company_id = companies_df.iloc[0]["id"]
        print(f"Using company ID: {company_id}")

        # Get custom axes for this company
        print("Fetching custom axes...")
        axes_df = client.get_custom_axes(company_id)
        print(f"Retrieved {len(axes_df)} custom axes")
        if not axes_df.empty:
            print("Sample axes data:")
            print(axes_df.head(2).to_string())

        # Get axe values
        if not axes_df.empty:
            axe_id = axes_df.iloc[0]["id"]
            print(f"\nFetching values for axe: {axe_id}")
            values_df = client.get_axe_values(company_id, axe_id)
            print(f"Retrieved {len(values_df)} axe values")
            if not values_df.empty:
                print("Sample values data:")
                print(values_df.head(2).to_string())


def main() -> None:
    """Main function to run all demonstrations."""
    setup_logging()

    print("Enhanced N2F API Simulation Demo")
    print("=" * 50)

    try:
        # Run all demonstrations
        demonstrate_basic_simulation()
        demonstrate_upsert_simulation()
        demonstrate_error_simulation()
        demonstrate_large_dataset_simulation()
        demonstrate_custom_axes_simulation()

        print("\n" + "=" * 50)
        print("All demonstrations completed successfully!")
        print("\nBenefits of enhanced simulation:")
        print("- Realistic data for comprehensive testing")
        print("- Full business logic execution")
        print("- No side effects (no emails sent)")
        print("- Configurable error scenarios")
        print("- Scalable data generation")
        print("- Network delay simulation")

    except Exception as e:
        print(f"Error during demonstration: {e}")
        logging.exception("Demonstration failed")


if __name__ == "__main__":
    main()
