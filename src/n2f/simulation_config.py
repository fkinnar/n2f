"""
Configuration utilities for N2F API simulation.

This module provides easy-to-use configuration functions for setting up
different simulation scenarios.
"""

from n2f.simulation import SimulationConfig, configure_simulation


def setup_basic_simulation() -> None:
    """Setup basic simulation with default settings."""
    config = SimulationConfig(
        simulate_errors=False,
        error_rate=0.0,
        response_delay_ms=10.0,
        data_size_multiplier=1.0,
    )
    configure_simulation(config)


def setup_stress_test_simulation(
    data_multiplier: float = 100.0, response_delay_ms: float = 5.0
) -> None:
    """Setup simulation for stress testing with large datasets."""
    config = SimulationConfig(
        simulate_errors=False,
        error_rate=0.0,
        response_delay_ms=response_delay_ms,
        data_size_multiplier=data_multiplier,
    )
    configure_simulation(config)


def setup_error_testing_simulation(
    error_rate: float = 0.2, response_delay_ms: float = 50.0
) -> None:
    """Setup simulation for error scenario testing."""
    config = SimulationConfig(
        simulate_errors=True,
        error_rate=error_rate,
        response_delay_ms=response_delay_ms,
        data_size_multiplier=1.0,
    )
    configure_simulation(config)


def setup_realistic_simulation(
    response_delay_ms: float = 100.0, data_size_multiplier: float = 5.0
) -> None:
    """Setup simulation that mimics real API behavior."""
    config = SimulationConfig(
        simulate_errors=False,
        error_rate=0.0,
        response_delay_ms=response_delay_ms,
        data_size_multiplier=data_size_multiplier,
    )
    configure_simulation(config)


def setup_custom_simulation(
    simulate_errors: bool = False,
    error_rate: float = 0.0,
    response_delay_ms: float = 10.0,
    data_size_multiplier: float = 1.0,
) -> None:
    """Setup custom simulation with user-defined parameters."""
    config = SimulationConfig(
        simulate_errors=simulate_errors,
        error_rate=error_rate,
        response_delay_ms=response_delay_ms,
        data_size_multiplier=data_size_multiplier,
    )
    configure_simulation(config)


# Predefined simulation scenarios
SIMULATION_SCENARIOS = {
    "basic": setup_basic_simulation,
    "stress_test": setup_stress_test_simulation,
    "error_testing": setup_error_testing_simulation,
    "realistic": setup_realistic_simulation,
}


def apply_simulation_scenario(scenario_name: str, **kwargs) -> None:
    """
    Apply a predefined simulation scenario.

    Args:
        scenario_name: Name of the scenario to apply
        **kwargs: Additional parameters for the scenario

    Available scenarios:
        - "basic": Basic simulation with minimal data
        - "stress_test": Large dataset simulation for stress testing
        - "error_testing": Simulation with error scenarios
        - "realistic": Simulation that mimics real API behavior
    """
    if scenario_name not in SIMULATION_SCENARIOS:
        available = ", ".join(SIMULATION_SCENARIOS.keys())
        raise ValueError(f"Unknown scenario '{scenario_name}'. Available: {available}")

    scenario_func = SIMULATION_SCENARIOS[scenario_name]
    scenario_func(**kwargs)
