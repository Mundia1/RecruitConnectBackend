# RecruitConnect Backend

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.0.1-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

RecruitConnect is a modern recruitment platform that connects job seekers with employers. This repository contains the backend API built with Flask, PostgreSQL, and various modern web technologies.

## ✨ Features

- **User Authentication & Authorization**
  - JWT-based authentication
  - Role-based access control (Job Seeker, Employer, Admin)
  - Secure password hashing with bcrypt

- **Job Management**
  - Create, read, update, and delete job postings
  - Job search and filtering capabilities
  - Application tracking system

- **Application Processing**
  - Application submission and status updates
  - Resume/CV handling
  - Application review workflow

- **Enterprise Features**
  - Email notifications
  - Background task processing with Celery
  - Caching with Redis
  - Monitoring with Prometheus
  - Error tracking with Sentry

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 13+
- Redis
- pipenv (for dependency management)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/RecruitConnectBackend.git
   cd RecruitConnectBackend
   ```

2. **Set up environment variables**
   Copy the example environment file and update the values:
   ```bash
   cp .env.example .env
   ```
   Update the `.env` file with your configuration (database URLs, secrets, etc.).

3. **Install dependencies**
   ```bash
   pipenv install --dev
   pipenv shell
   ```

4. **Set up the database**
   ```bash
   flask db upgrade
   ```

5. **Seed initial data (optional)**
   ```bash
   python seed.py
   ```

6. **Run the development server**
   ```bash
   python run.py
   ```

   The API will be available at `http://localhost:5000`

## 📚 API Documentation

API documentation is available at `/api/docs` when running the development server.

## 🧪 Testing

Run the test suite with:

```bash
pytest
```

## 🛠️ Development

### Project Structure

```
RecruitConnectBackend/
├── app/                    # Application package
│   ├── __init__.py         # Application factory
│   ├── models/             # Database models
│   ├── resources/          # API resources/endpoints
│   ├── services/           # Business logic
│   ├── schemas/            # Marshmallow schemas
│   └── utils/              # Helper functions
├── migrations/             # Database migrations
├── tests/                  # Test files
├── config.py               # Configuration settings
├── run.py                  # Application entry point
├── seed.py                 # Database seeding script
└── Pipfile                # Dependencies
```

### Environment Variables

Key environment variables:

- `FLASK_ENV`: Application environment (development, testing, production)
- `DATABASE_URL`: PostgreSQL connection string
- `TEST_DATABASE_URL`: Test database connection string
- `SECRET_KEY`: Flask secret key
- `JWT_SECRET_KEY`: JWT signing key
- `REDIS_URL`: Redis connection URL
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`: Email server configuration
- `SENTRY_DSN`: Sentry DSN for error tracking

## 🚀 Deployment

### Production

1. Set `FLASK_ENV=production` in your environment
2. Configure a production-ready WSGI server (Gunicorn, uWSGI)
3. Set up a reverse proxy (Nginx, Apache)
4. Configure SSL/TLS

Example with Gunicorn:
```bash
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

### Docker

1. Build the Docker image:
   ```bash
   docker build -t recruitconnect-backend .
   ```

2. Run the container:
   ```bash
   docker run -p 5000:5000 --env-file .env recruitconnect-backend
   ```

## 📚 API Endpoints

### Authentication

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `POST` | `/auth/register` | Register a new user | None |
| `POST` | `/auth/login` | User login | None |
| `POST` | `/auth/refresh` | Refresh access token | Refresh Token |
| `GET`  | `/auth/me` | Get current user info | JWT Token |

### Jobs

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `GET`    | `/jobs` | Get all jobs | None |
| `POST`   | `/jobs` | Create a new job posting | JWT Token (Admin) |
| `GET`    | `/jobs/<int:job_id>` | Get job by ID | None |
| `PATCH`  | `/jobs/<int:job_id>` | Update job | JWT Token (Admin) |
| `DELETE` | `/jobs/<int:job_id>` | Delete job | JWT Token (Admin) |

### Applications

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `GET`    | `/applications` | Get all applications (filter by user_id or job_posting_id) | JWT Token |
| `POST`   | `/applications` | Create new application | JWT Token |
| `GET`    | `/applications/<int:application_id>` | Get application by ID | JWT Token |
| `PATCH`  | `/applications/<int:application_id>` | Update application status | JWT Token (Admin/Recruiter) |
| `DELETE` | `/applications/<int:application_id>` | Delete application | JWT Token (Admin) |

### Messages

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `GET`    | `/messages/between/<int:user1_id>/<int:user2_id>` | Get messages between two users | JWT Token |
| `POST`   | `/messages` | Send a new message | JWT Token |
| `GET`    | `/messages/<int:message_id>` | Get message by ID | JWT Token |
| `PATCH`  | `/messages/<int:message_id>/read` | Mark message as read | JWT Token |
| `DELETE` | `/messages/<int:message_id>` | Delete message | JWT Token |

### Feedback

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `GET`    | `/feedback/application/<int:job_application_id>` | Get feedback for application | JWT Token |
| `POST`   | `/feedback` | Submit new feedback | JWT Token |
| `GET`    | `/feedback/<int:feedback_id>` | Get feedback by ID | JWT Token |
| `PATCH`  | `/feedback/<int:feedback_id>` | Update feedback | JWT Token |
| `DELETE` | `/feedback/<int:feedback_id>` | Delete feedback | JWT Token (Admin) |

### FAQ

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `GET`    | `/faq` | Get all FAQs | None |
| `POST`   | `/faq` | Create new FAQ | JWT Token (Admin) |
| `GET`    | `/faq/<int:faq_id>` | Get FAQ by ID | None |
| `PATCH`  | `/faq/<int:faq_id>` | Update FAQ | JWT Token (Admin) |
| `DELETE` | `/faq/<int:faq_id>` | Delete FAQ | JWT Token (Admin) |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


