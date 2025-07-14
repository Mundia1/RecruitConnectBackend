# RecruitConnect Backend Development Workflow

This document outlines the collaborative development workflow for the RecruitConnect backend, focusing on task assignments, Git branching strategy, and best practices for efficient teamwork.

## 1. Task Assignments

Below is the breakdown of files and responsibilities for each team member. Each student is responsible for implementing the code within their assigned files and ensuring they are well-tested.

### Wekesa Eugene - Core Application Setup (5 files)
*   `app.py`
*   `run.py`
*   `config.py`
*   `app/__init__.py`
*   `app/blueprints/api_v1.py`

### MWORIA, CHRISTINE - User Authentication Module (5 files)
*   `app/models/user.py`
*   `app/schemas/user.py`
*   `app/services/auth_service.py`
*   `app/resources/auth.py`
*   `tests/resources/test_auth.py`

### KARIUKI, REGINA - Job Posting Module (5 files)
*   `app/models/job.py`
*   `app/schemas/job.py`
*   `app/services/job_service.py`
*   `app/resources/job.py`
*   `tests/resources/test_job.py`

### Kaloki, Brian - Job Application Module (5 files)
*   `app/models/application.py`
*   `app/schemas/application.py`
*   `app/services/application_service.py`
*   `app/resources/application.py`
*   `tests/resources/test_application.py`

### Njai, Priscillah - Service-Level Tests & Utilities (4 files)
*   `app/utils/helpers.py`
*   `app/tasks/__init__.py`
*   `tests/services/test_auth_service.py`
*   `tests/services/test_job_service.py`

### Anderson Waithaka - Database Seeding & Test Infrastructure (4 files)
*   `seed.py`
*   `tests/__init__.py`
*   `tests/conftest.py`
*   `tests/services/test_application_service.py`

## 2. Git Branching Strategy

We will follow a simplified Git Flow model to manage our codebase, ensuring a clean history and efficient collaboration.

### Main Branches:
*   `main`: This branch contains the production-ready code. Only stable, fully tested code should be merged here.
*   `develop`: This branch integrates all new features. All feature branches are merged into `develop`.

### Feature Branches:
*   For each task or feature, create a new branch off `develop`.
*   **Naming Convention**: `feature/<your-name>/<short-description-of-feature>` (e.g., `feature/eugene/user-auth-api`, `feature/christine/job-posting-crud`)
*   Work on your assigned files within your feature branch.
*   Commit frequently with clear, descriptive messages.

### Workflow Steps:
1.  **Pull Latest `develop`**: Always start by pulling the latest changes from the `develop` branch to ensure your local `develop` is up-to-date.
    ```bash
    git checkout develop
    git pull origin develop
    ```
2.  **Create Feature Branch**: Create a new feature branch from `develop`.
    ```bash
    git checkout -b feature/<your-name>/<short-description>
    ```
3.  **Develop & Commit**: Implement your assigned tasks. Commit your changes regularly.
    ```bash
    git add .
    git commit -m "feat: Implement user registration endpoint"
    ```
4.  **Push Feature Branch**: Push your feature branch to the remote repository.
    ```bash
    git push origin feature/<your-name>/<short-description>
    ```
5.  **Create Pull Request (PR)**: Once your feature is complete and tested locally, create a Pull Request from your feature branch to the `develop` branch.
    *   Ensure your code passes all local tests (`pipenv run pytest`).
    *   Ensure your code passes linting and type checks (`pipenv run ruff check . --fix`, `pipenv run ruff format .`, `pipenv run mypy .`).
    *   Provide a clear description of the changes in the PR.
6.  **Code Review**: Another team member will review your PR. Address any feedback or requested changes.
7.  **Merge**: Once the PR is approved, it will be merged into the `develop` branch.
8.  **Clean Up**: After your feature branch is merged, you can delete it locally and remotely.
    ```bash
    git branch -d feature/<your-name>/<short-description>
    git push origin --delete feature/<your-name>/<short-description>
    ```

## 3. Collaboration Best Practices

*   **Communicate**: Regularly communicate progress, blockers, or any changes that might affect other team members.
*   **Small, Frequent Commits**: Break down your work into smaller, logical commits. This makes reviews easier.
*   **Test Before Pushing**: Always run tests and quality checks locally before pushing and creating a PR.
*   **Review Others' Code**: Actively participate in code reviews to ensure code quality and share knowledge.
*   **Resolve Conflicts Promptly**: If merge conflicts arise, resolve them as soon as possible.

This workflow aims to streamline our development process and ensure a high-quality, maintainable codebase.