# Enhanced N2F API Simulation System

## Overview

The enhanced simulation system allows you to test the N2F API integration with realistic
data without making actual HTTP calls. This is particularly useful for:

- **Testing with large datasets** without impacting real users
- **Avoiding email notifications** that N2F sends when creating users
- **Validating business logic** with comprehensive data scenarios
- **Testing error handling** with configurable error rates

## Quick Start

### Basic Usage

```python
from core import SyncContext
from n2f.client import N2fApiClient
from n2f.simulation_config import apply_simulation_scenario

# Setup basic simulation
apply_simulation_scenario("basic")

# Create client with simulation enabled
context = SyncContext(...)  # with simulate=True in config
client = N2fApiClient(context)

# All operations now use realistic simulated data
users_df = client.get_users()  # Returns 200 realistic users
companies_df = client.get_companies()  # Returns 200 realistic companies
```

### Available Scenarios

```python
# Basic simulation (minimal data, fast)
apply_simulation_scenario("basic")

# Stress testing (large datasets)
apply_simulation_scenario("stress_test", data_multiplier=100.0)

# Error testing (simulate API errors)
apply_simulation_scenario("error_testing", error_rate=0.3)

# Realistic simulation (mimics real API behavior)
apply_simulation_scenario("realistic")
```

## Configuration Options

### SimulationConfig Parameters

```python
from n2f.simulation import SimulationConfig, configure_simulation

config = SimulationConfig(
    simulate_errors=False,      # Enable/disable error simulation
    error_rate=0.1,            # Probability of errors (0.0-1.0)
    response_delay_ms=50.0,    # Network delay simulation
    data_size_multiplier=5.0   # Multiply data size (1.0 = normal)
)

configure_simulation(config)
```

## Generated Data

### Users

- Realistic email addresses (`test.user.1@example.com`)
- Proper names and profiles
- Company associations
- Creation/update timestamps

### Companies

- Unique UUIDs and codes
- Realistic company names
- Proper metadata

### Roles & Profiles

- Standard role types (Admin, User, Manager, etc.)
- Profile hierarchies
- Permission structures

### Custom Axes

- Multiple axis types (PROJECT, PLATE, SUBPOST, CUSTOM)
- Company-specific data
- Hierarchical relationships

## Error Simulation

The system can simulate various HTTP error scenarios:

```python
# Enable error simulation
config = SimulationConfig(
    simulate_errors=True,
    error_rate=0.2  # 20% chance of error
)

# Simulated errors include:
# - 400 Bad Request
# - 401 Unauthorized
# - 403 Forbidden
# - 404 Not Found
# - 409 Conflict
# - 422 Unprocessable Entity
# - 500 Internal Server Error
```

## Performance Testing

### Large Dataset Simulation

```python
# Generate 10x more data for stress testing
apply_simulation_scenario("stress_test", data_multiplier=10.0)

# This will generate:
# - 2000 users instead of 200
# - 2000 companies instead of 200
# - 20000 custom axes instead of 2000
```

### Network Delay Simulation

```python
# Simulate realistic network delays
config = SimulationConfig(
    response_delay_ms=100.0  # 100ms delay per request
)
```

## Logging and Monitoring

The simulation system provides detailed logging:

```text
2025-09-05 11:53:26,373 - INFO - SIMULATION: GET users - {'start': 0, 'limit': 200, 'returned_count': 200, 'total_available': 200}
2025-09-05 11:53:26,589 - INFO - SIMULATION: UPSERT /users - {'action_type': 'create', 'object_type': 'user', 'object_id': 'new.user@example.com', 'scope': 'users'}
```

### Accessing Simulation Log

```python
from n2f.simulation import get_simulator

simulator = get_simulator()
log = simulator.get_simulation_log()

for entry in log:
    print(f"{entry['timestamp']}: {entry['operation']} {entry['endpoint']}")
```

## Integration with Existing Code

The enhanced simulation is **fully backward compatible**. Existing code will
automatically benefit from:

- Realistic data instead of empty responses
- Proper error handling simulation
- Full business logic execution
- Cache and payload processing

### No Code Changes Required

```python
# This code works exactly the same, but now with realistic data
def sync_users():
    client = N2fApiClient(context)
    users = client.get_users()  # Now returns realistic data
    for user in users.itertuples():
        result = client.create_user(user_payload)  # Now simulates realistic responses
        # All business logic executes normally
```

## Examples

### Complete Test Scenario

```python
from n2f.simulation_config import apply_simulation_scenario
from n2f.client import N2fApiClient

# Setup realistic simulation
apply_simulation_scenario("realistic")

# Test with large dataset
client = N2fApiClient(context)

# Get all data (now with realistic simulation)
users_df = client.get_users()        # 1000 realistic users
companies_df = client.get_companies() # 1000 realistic companies
roles_df = client.get_roles()        # 500 realistic roles

# Test user operations
for user in users_df.head(10).itertuples():
    payload = {
        "mail": user.mail,
        "firstName": user.firstName,
        "lastName": user.lastName
    }

    result = client.create_user(payload)
    print(f"User {user.mail}: {result.success} - {result.message}")

    if result.response_data:
        print(f"  Created with ID: {result.response_data['id']}")
```

### Error Testing

```python
# Test error handling
apply_simulation_scenario("error_testing", error_rate=0.5)

client = N2fApiClient(context)

success_count = 0
error_count = 0

for i in range(20):
    result = client.create_user({"mail": f"test{i}@example.com"})
    if result.success:
        success_count += 1
    else:
        error_count += 1
        print(f"Error: {result.message} (Status: {result.status_code})")

print(f"Success: {success_count}, Errors: {error_count}")
```

## Benefits

1. **No Side Effects**: No emails sent to real users
1. **Comprehensive Testing**: Test with realistic data volumes
1. **Error Scenarios**: Validate error handling logic
1. **Performance Testing**: Simulate large datasets and network delays
1. **Full Logic Execution**: All business logic runs normally
1. **Easy Configuration**: Predefined scenarios for common use cases
1. **Backward Compatible**: No changes to existing code required

## Files

- `src/n2f/simulation.py` - Core simulation system
- `src/n2f/simulation_config.py` - Configuration utilities
- `src/n2f/simulation_example.py` - Complete usage examples
- `tests/test_enhanced_simulation.py` - Test suite
