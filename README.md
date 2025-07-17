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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


