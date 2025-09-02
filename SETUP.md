# Project Setup

This project uses `pyproject.toml` to manage dependencies and project settings.

## 1. Create a Virtual Environment

First, you need to create and activate a Python virtual environment. This isolates the project's dependencies from your system.

```bash
# Create the virtual environment
python -m venv env

# Activate it
# On Windows (cmd.exe):
env\Scripts\activate.bat
# On Windows (PowerShell):
.\env\Scripts\Activate.ps1
# On macOS/Linux:
source env/bin/activate
```

## 2. Install Dependencies

Once your virtual environment is activated, you can install the project and its dependencies.

### For Development

This is the recommended setup for developers working on this project. It includes all production dependencies plus tools for testing, linting, and code formatting.

Run the following command:

```bash
pip install -e .[dev]
```
*   **What this does:**
    *   `pip install .`: Installs the project based on `pyproject.toml`.
    *   `-e`: Installs in "editable" mode. Changes you make to the source code in `src/` are immediately available without reinstalling.
    *   `[dev]`: Installs the extra dependencies listed under `[project.optional-dependencies].dev` (like `pytest`, `pyright`, etc.).

### For Production

This setup is for deploying the application. It only installs the packages strictly necessary for the application to run.

Run the following command:

```bash
pip install .
```
*   **What this does:**
    *   Installs the project and only the main dependencies listed under `[project].dependencies`.
    *   This creates a non-editable installation, optimized for production environments.
