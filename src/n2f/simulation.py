"""
Enhanced simulation system for N2F API operations.

This module provides realistic simulation capabilities for testing the N2F API
without making actual HTTP calls. It generates credible responses that allow
the full business logic to be executed while avoiding side effects like
sending emails to real users.
"""

import time
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from n2f.api_result import ApiResult


class SimulationDataGenerator:
    """Generates realistic test data for N2F API simulation."""

    def __init__(self):
        self._user_counter = 1
        self._company_counter = 1
        self._role_counter = 1
        self._profile_counter = 1
        self._axe_counter = 1

    def generate_user_data(self, count: int = 1) -> List[Dict[str, Any]]:
        """Generate realistic user data for testing."""
        users = []
        for i in range(count):
            user_id = f"user_{self._user_counter:04d}"
            email = f"test.user.{self._user_counter}@example.com"
            users.append(
                {
                    "id": user_id,
                    "mail": email,
                    "firstName": f"Test{self._user_counter}",
                    "lastName": f"User{self._user_counter}",
                    "profile": "Standard",
                    "role": "User",
                    "company": f"COMP_{self._company_counter:03d}",
                    "active": True,
                    "createdAt": (datetime.now() - timedelta(days=30)).isoformat(),
                    "updatedAt": datetime.now().isoformat(),
                }
            )
            self._user_counter += 1
        return users

    def generate_company_data(self, count: int = 1) -> List[Dict[str, Any]]:
        """Generate realistic company data for testing."""
        companies = []
        for i in range(count):
            company_id = f"comp_{self._company_counter:04d}"
            companies.append(
                {
                    "id": company_id,
                    "uuid": str(uuid.uuid4()),
                    "name": f"Test Company {self._company_counter}",
                    "code": f"COMP_{self._company_counter:03d}",
                    "active": True,
                    "createdAt": (datetime.now() - timedelta(days=60)).isoformat(),
                    "updatedAt": datetime.now().isoformat(),
                }
            )
            self._company_counter += 1
        return companies

    def generate_role_data(self, count: int = 1) -> List[Dict[str, Any]]:
        """Generate realistic role data for testing."""
        roles = []
        role_names = ["Admin", "User", "Manager", "Viewer", "Editor"]
        for i in range(count):
            role_name = role_names[i % len(role_names)]
            roles.append(
                {
                    "id": f"role_{self._role_counter:04d}",
                    "name": role_name,
                    "description": f"{role_name} role for testing",
                    "permissions": (
                        ["read"] if role_name == "Viewer" else ["read", "write"]
                    ),
                    "active": True,
                    "createdAt": (datetime.now() - timedelta(days=90)).isoformat(),
                }
            )
            self._role_counter += 1
        return roles

    def generate_profile_data(self, count: int = 1) -> List[Dict[str, Any]]:
        """Generate realistic user profile data for testing."""
        profiles = []
        profile_names = ["Standard", "Premium", "Admin", "Basic", "Enterprise"]
        for i in range(count):
            profile_name = profile_names[i % len(profile_names)]
            profiles.append(
                {
                    "id": f"profile_{self._profile_counter:04d}",
                    "name": profile_name,
                    "description": f"{profile_name} user profile",
                    "features": (
                        ["basic"] if profile_name == "Basic" else ["basic", "advanced"]
                    ),
                    "active": True,
                    "createdAt": (datetime.now() - timedelta(days=120)).isoformat(),
                }
            )
            self._profile_counter += 1
        return profiles

    def generate_axe_data(
        self, company_id: str, count: int = 1
    ) -> List[Dict[str, Any]]:
        """Generate realistic axe data for testing."""
        axes = []
        axe_types = ["PROJECT", "PLATE", "SUBPOST", "CUSTOM"]
        for i in range(count):
            axe_type = axe_types[i % len(axe_types)]
            axes.append(
                {
                    "id": f"axe_{self._axe_counter:04d}",
                    "uuid": str(uuid.uuid4()),
                    "code": f"AXE_{self._axe_counter:03d}",
                    "name": f"Test {axe_type} {self._axe_counter}",
                    "type": axe_type,
                    "companyId": company_id,
                    "active": True,
                    "createdAt": (datetime.now() - timedelta(days=45)).isoformat(),
                    "updatedAt": datetime.now().isoformat(),
                }
            )
            self._axe_counter += 1
        return axes


class SimulationConfig:
    """Configuration for simulation behavior."""

    def __init__(
        self,
        simulate_errors: bool = False,
        error_rate: float = 0.1,  # 10% chance of error
        response_delay_ms: float = 50.0,  # Simulate network delay
        data_size_multiplier: float = 1.0,  # Multiply data size for stress testing
    ):
        self.simulate_errors = simulate_errors
        self.error_rate = error_rate
        self.response_delay_ms = response_delay_ms
        self.data_size_multiplier = data_size_multiplier


class EnhancedSimulator:
    """Enhanced simulation system for N2F API operations."""

    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config = config or SimulationConfig()
        self.data_generator = SimulationDataGenerator()
        self._simulation_log: List[Dict[str, Any]] = []

    def simulate_get_response(
        self, entity: str, start: int = 0, limit: int = 200, **kwargs
    ) -> List[Dict[str, Any]]:
        """Simulate a GET response with realistic data."""
        # Simulate network delay
        if self.config.response_delay_ms > 0:
            time.sleep(self.config.response_delay_ms / 1000.0)

        # Calculate actual data size
        actual_limit = int(limit * self.config.data_size_multiplier)
        actual_start = start

        # Generate realistic data based on entity type
        if entity == "users":
            data = self.data_generator.generate_user_data(actual_limit)
        elif entity == "companies":
            data = self.data_generator.generate_company_data(actual_limit)
        elif entity == "roles":
            data = self.data_generator.generate_role_data(actual_limit)
        elif entity == "userprofiles":
            data = self.data_generator.generate_profile_data(actual_limit)
        elif entity.startswith("companies/") and "/axes" in entity:
            # Extract company_id from entity path
            parts = entity.split("/")
            if len(parts) >= 2:
                company_id = parts[1]
                data = self.data_generator.generate_axe_data(company_id, actual_limit)
            else:
                data = []
        else:
            data = []

        # Apply pagination
        paginated_data = data[actual_start : actual_start + actual_limit]

        # Log the simulation
        self._log_simulation(
            "GET",
            entity,
            {
                "start": actual_start,
                "limit": actual_limit,
                "returned_count": len(paginated_data),
                "total_available": len(data),
            },
        )

        return paginated_data

    def simulate_upsert_response(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        action_type: str = "upsert",
        object_type: Optional[str] = None,
        object_id: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> ApiResult:
        """Simulate an upsert (POST/PUT) response with realistic data."""
        # Simulate network delay
        if self.config.response_delay_ms > 0:
            time.sleep(self.config.response_delay_ms / 1000.0)

        # Check if we should simulate an error
        if self.config.simulate_errors and self._should_simulate_error():
            return self._simulate_error_response(
                action_type, object_type, object_id, scope
            )

        # Generate realistic response data
        response_data = self._generate_upsert_response_data(payload, object_type)

        # Log the simulation
        self._log_simulation(
            "UPSERT",
            endpoint,
            {
                "action_type": action_type,
                "object_type": object_type,
                "object_id": object_id,
                "scope": scope,
                "payload_keys": list(payload.keys()) if payload else [],
            },
        )

        return ApiResult.success_result(
            message=f"Simulated {action_type} successful",
            status_code=200,
            duration_ms=self.config.response_delay_ms,
            response_data=response_data,
            action_type=action_type,
            object_type=object_type,
            object_id=object_id,
            scope=scope,
        )

    def simulate_delete_response(
        self,
        endpoint: str,
        object_id: str,
        action_type: str = "delete",
        object_type: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> ApiResult:
        """Simulate a delete response with realistic data."""
        # Simulate network delay
        if self.config.response_delay_ms > 0:
            time.sleep(self.config.response_delay_ms / 1000.0)

        # Check if we should simulate an error
        if self.config.simulate_errors and self._should_simulate_error():
            return self._simulate_error_response(
                action_type, object_type, object_id, scope
            )

        # Log the simulation
        self._log_simulation(
            "DELETE",
            endpoint,
            {
                "action_type": action_type,
                "object_type": object_type,
                "object_id": object_id,
                "scope": scope,
            },
        )

        return ApiResult.success_result(
            message=f"Simulated {action_type} successful",
            status_code=200,
            duration_ms=self.config.response_delay_ms,
            action_type=action_type,
            object_type=object_type,
            object_id=object_id,
            scope=scope,
        )

    def _should_simulate_error(self) -> bool:
        """Determine if we should simulate an error based on error rate."""
        import random

        return random.random() < self.config.error_rate

    def _simulate_error_response(
        self,
        action_type: str,
        object_type: Optional[str],
        object_id: Optional[str],
        scope: Optional[str],
    ) -> ApiResult:
        """Simulate an error response."""
        error_codes = [400, 401, 403, 404, 409, 422, 500]
        error_messages = [
            "Bad Request",
            "Unauthorized",
            "Forbidden",
            "Not Found",
            "Conflict",
            "Unprocessable Entity",
            "Internal Server Error",
        ]

        import random

        error_index = random.randint(0, len(error_codes) - 1)
        status_code = error_codes[error_index]
        message = error_messages[error_index]

        return ApiResult.error_result(
            message=f"Simulated error: {message}",
            status_code=status_code,
            duration_ms=self.config.response_delay_ms,
            error_details=(
                f"Simulated {action_type} error for {object_type} {object_id}"
            ),
            action_type=action_type,
            object_type=object_type,
            object_id=object_id,
            scope=scope,
        )

    def _generate_upsert_response_data(
        self, payload: Dict[str, Any], object_type: Optional[str]
    ) -> Dict[str, Any]:
        """Generate realistic response data for upsert operations."""
        response_data: Dict[str, Any] = {
            "id": str(uuid.uuid4()),
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "status": "success",
        }

        # Add object-specific data
        if object_type == "user" and "mail" in payload:
            response_data.update(
                {
                    "mail": payload["mail"],
                    "firstName": payload.get("firstName", ""),
                    "lastName": payload.get("lastName", ""),
                    "active": True,
                }
            )
        elif object_type == "axe" and "code" in payload:
            response_data.update(
                {
                    "code": payload["code"],
                    "name": payload.get("name", ""),
                    "type": payload.get("type", ""),
                    "active": True,
                }
            )

        return response_data

    def _log_simulation(
        self, operation: str, endpoint: str, details: Dict[str, Any]
    ) -> None:
        """Log simulation activity for debugging and analysis."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "endpoint": endpoint,
            "details": details,
        }
        self._simulation_log.append(log_entry)

        logging.info("SIMULATION: %s %s - %s", operation, endpoint, details)

    def get_simulation_log(self) -> List[Dict[str, Any]]:
        """Get the complete simulation log."""
        return self._simulation_log.copy()

    def clear_simulation_log(self) -> None:
        """Clear the simulation log."""
        self._simulation_log.clear()


# Global simulator instance
_global_simulator: Optional[EnhancedSimulator] = None


def get_simulator() -> EnhancedSimulator:
    """Get the global simulator instance."""
    global _global_simulator
    if _global_simulator is None:
        _global_simulator = EnhancedSimulator()
    return _global_simulator


def configure_simulation(config: SimulationConfig) -> None:
    """Configure the global simulator."""
    global _global_simulator
    _global_simulator = EnhancedSimulator(config)
