# RecruitConnect - Backend

This document provides a comprehensive guide to the backend of the RecruitConnect application. It is designed to be a single source of truth for developers, covering everything from the initial setup to the architectural design and code quality standards.

## Features

-   **Service-Oriented Architecture**: A modular design that separates concerns into services, resources, models, and schemas.
-   **RESTful API**: A robust, versioned API for managing users, job postings, and applications.
-   **Authentication**: Secure user authentication and authorization using JSON Web Tokens (JWT).
-   **Database**: PostgreSQL for storing all application data.
-   **Code Quality**: Enforced with `ruff` for linting/formatting and `mypy` for static type checking.

## Folder Structure

```
├── app/
│   ├── __init__.py
│   ├── blueprints/
│   │   ├── __init__.py
│   │   └── api_v1.py
│   ├── models/
│   ├── resources/
│   ├── schemas/
│   ├── services/
│   ├── tasks/
│   └── utils/
├── migrations/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_job.py
│   │   └── test_application.py
│   └── services/
│       ├── __init__.py
│       ├── test_auth_service.py
│       ├── test_job_service.py
│       └── test_application_service.py
├── .env
├── .env.example
├── .gitignore
├── app.py
├── config.py
├── database_schema.md
├── Pipfile
├── run.py
└── seed.py
```

---

## Architecture & Design

This project follows the **App Factory Pattern**, a best practice for Flask applications that enhances modularity and testability.

### Core Components

-   **`app.py`**: The main entry point for the Flask application. It imports the `create_app` function and starts the server.
-   **`app/__init__.py` (App Factory)**: Contains the `create_app` function, which is responsible for initializing the Flask application, its extensions (e.g., SQLAlchemy, JWT), and registering the API blueprints.
-   **`config.py`**: Implements a class-based configuration structure with separate classes for `Development`, `Testing`, and `Production` environments.
-   **`app/blueprints/api_v1.py`**: Aggregates all the API resources to create the version 1 of the API. This is crucial for versioning.
-   **`app/resources/`**: Defines the API resources (e.g., using Flask-RESTful). Each file handles the HTTP methods for a specific model.
-   **`app/services/`**: Contains the core business logic. Services are called by the resources and interact with the database models.
-   **`app/models/`**: Defines the database tables as Python classes using SQLAlchemy.
-   **`app/schemas/`**: Defines the data serialization and validation schemas using Marshmallow.

### Database

For a detailed breakdown of the database schema, including table structures, column definitions, and entity relationships, please see the [`database_schema.md`](database_schema.md) file.

---

## Setup and Installation

1.  **Install dependencies from Pipfile:**
    This will create a virtual environment and install all production and development dependencies.
    ```bash
    pipenv install --dev
    ```

3.  **Activate the virtual environment:**
    ```bash
    pipenv shell
    ```

4.  **Set up environment variables:**
    Create a `.env` file by copying the example and update the variables with your configuration.
    ```bash
    cp .env.example .env
    ```

5.  **Set up the PostgreSQL Database:**
    -   Ensure your PostgreSQL server is running.
    -   Create a new database for the project (e.g., `recruitconnect_db`).
    -   Update the `DATABASE_URL` in your `.env` file.

6.  **Run database migrations:**
    ```bash
    pipenv run flask db init
    pipenv run flask db migrate -m "Initial migration"
    pipenv run flask db upgrade
    ```

7.  **Seed the database (optional):**
    ```bash
    pipenv run python seed.py
    ```

8.  **Run the application:**
    The `--debug` flag enables the Flask debugger and reloader.
    ```bash
    pipenv run flask run --debug
    ```

---

## Development Workflow & Collaboration

For detailed information on task assignments, Git branching strategy, and best practices for collaborative development, please refer to the [`docs/workflow.md`](docs/workflow.md) file.

---

## Code Quality & Testing

To maintain a high-quality and reliable codebase, this project uses `ruff` for linting and formatting, and `mypy` for static type checking.

### Running Quality Checks

-   **Lint and format the code:**
    ```bash
    pipenv run ruff check . --fix
    pipenv run ruff format .
    ```

-   **Run static type checking:**
    ```bash
    pipenv run mypy .
    ```

### Running Tests

To run the full test suite:
```bash
pipenv run pytest
```

---

