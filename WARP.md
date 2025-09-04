# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this
repository.

## Project Overview

The N2F synchronization tool is a Python application that synchronizes data between
Agresso ERP and N2F expense management system. It handles users, projects, plates (cost
centers), and subposts in both directions with comprehensive error handling, caching,
and monitoring.

## Key Architecture Concepts

### Core Components

- **SyncOrchestrator** (`src/core/orchestrator.py`): Main orchestration engine that
  coordinates all synchronization workflows
- **EntitySynchronizer** (`src/business/process/base_synchronizer.py`): Abstract base
  class for all entity synchronization (CREATE/UPDATE/DELETE operations)
- **N2fApiClient** (`src/n2f/client.py`): Centralized API client with authentication,
  pagination, caching, and retry logic
- **SyncContext** (`src/core/context.py`): Shared context object containing
  configuration, credentials, and state
- **Registry System** (`src/core/registry.py`): Auto-discovery and registration of
  synchronization scopes

### Synchronization Pattern

All entity synchronizers follow the same pattern:

1. Load data from Agresso (SQL queries)
1. Load data from N2F (API calls with caching)
1. Determine differences (create/update/delete operations)
1. Execute API operations with error handling
1. Log results and metrics

### Configuration System

- **Environment-based**: Dev/prod configurations via `dev.yaml`/`prod.yaml`
- **Dual mode support**: Can work with both object-style and dictionary-style config
  access
- **Environment variables**: Credentials loaded from environment or `.env` file in
  sandbox mode

## Common Development Commands

### Setup and Installation

```bash
# Create virtual environment and install dependencies (recommended)
python -m venv env
env\Scripts\activate  # Windows
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Running Synchronization

```bash
# Basic synchronization (creates and updates by default)
python src/sync-agresso-n2f.py

# Specific scopes
python src/sync-agresso-n2f.py --scope users projects
python src/sync-agresso-n2f.py --scope all

# With specific operations
python src/sync-agresso-n2f.py --create --update --delete --scope users

# Production mode
python src/sync-agresso-n2f.py --config prod --scope users

# Cache management
python src/sync-agresso-n2f.py --clear-cache --scope all
python src/sync-agresso-n2f.py --invalidate-cache get_users get_companies

# Skip .env loading (for testing production behavior)
python src/sync-agresso-n2f.py --skip-dotenv-loading

# Using batch file (Windows)
sync_n2f.bat --scope users,projects
```

### Testing

```bash
# Run all tests
python tests/run_tests.py

# Run specific test module
python tests/run_tests.py --module test_exceptions

# List available tests
python tests/run_tests.py --list

# With pytest (if installed)
python -m pytest --tb=short -v

# Run tests with coverage
python tests/run_coverage_simple.py
```

### Code Quality and Formatting

```bash
# Format code with Black
black src tests scripts

# Run linting with Flake8
flake8 src tests scripts

# Check type hints
python scripts/analyze_type_hints.py

# Run all pre-commit hooks manually
pre-commit run --all-files

# Check markdown files
python scripts/check_markdown.py
```

## Critical Development Guidelines

### Adding New Synchronization Scopes

1. **Create synchronizer class** extending `EntitySynchronizer`:

   ```python
   # src/business/process/new_entity_synchronizer.py
   class NewEntitySynchronizer(EntitySynchronizer):
       def build_payload(self, entity, df_agresso, df_n2f, df_n2f_companies):
           # Build API payload
           pass

       def get_entity_id(self, entity):
           # Return unique identifier
           pass
   ```

1. **Create scope function**:

   ```python
   # src/business/process/new_entity.py
   def synchronize_new_entities(context, sql_filename, sql_column_filter=""):
       # Implementation using the synchronizer
       pass
   ```

1. The registry system will auto-discover new scopes in the `business.process` module.

### Environment Configuration

The application requires these environment variables:

- `AGRESSO_DB_USER`: Database username
- `AGRESSO_DB_PASSWORD`: Database password
- `N2F_CLIENT_ID`: N2F API client ID
- `N2F_CLIENT_SECRET`: N2F API client secret

In sandbox mode, these can be provided via a `.env` file.

### External Dependencies

- **Iris Module**: The project depends on a shared `Iris` module located at
  `D:\Users\kinnar\source\repos\common\Python\Packages`. Set `PYTHONPATH` to include
  this path.
- **Database Access**: Requires connection to Agresso SQL Server databases
- **N2F API**: Connects to N2F REST API (sandbox or production)

### Error Handling Strategy

- **Hierarchical Exceptions**: Custom exception classes in `src/core/exceptions.py`
- **Context-Rich Errors**: All exceptions include detailed context and suggested
  solutions
- **Graceful Degradation**: Failed operations on individual entities don't stop the
  entire sync
- **Comprehensive Logging**: All API calls, errors, and metrics are logged with
  timestamps

### Caching System

- **Intelligent Caching**: API responses cached based on URL, credentials, and
  simulation mode
- **TTL Support**: Configurable time-to-live for cache entries
- **Cache Invalidation**: Selective invalidation by function name or pattern
- **Persistence**: Cache can persist between runs if configured

### Memory Management

- **Scope-based Cleanup**: Memory cleaned up after each scope completion
- **Memory Monitoring**: Track memory usage with configurable limits
- **Large Dataset Handling**: Optimized for processing thousands of records

## Testing Architecture

- **Modular Tests**: Each core component has dedicated test modules
- **Mock Framework**: Extensive use of mocks for API and database interactions
- **Coverage Tracking**: Test coverage monitoring with reporting
- **Integration Tests**: End-to-end workflow testing

## File Structure Context

- `src/`: Main source code
  - `core/`: Core infrastructure (orchestrator, cache, config, etc.)
  - `business/`: Business logic and synchronizers
  - `n2f/`: N2F API client and related utilities
  - `agresso/`: Agresso database access
- `tests/`: Comprehensive test suite
- `sql/`: SQL queries for data extraction (dev/prod versions)
- `scripts/`: Development and maintenance utilities
- `logs/`: Runtime logs (created automatically)

## Key Patterns and Conventions

- **Type Hints**: All functions use type annotations
- **Dataclasses**: Configuration objects use @dataclass
- **Abstract Base Classes**: Common patterns extracted to base classes
- **Dependency Injection**: Context object passed through call chain
- **Functional Decomposition**: Complex operations broken into smaller, testable
  functions
