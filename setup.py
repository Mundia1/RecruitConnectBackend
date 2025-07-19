from setuptools import setup, find_packages

setup(
    name="recruitconnect",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-Migrate',
        'Flask-JWT-Extended',
        'Flask-Bcrypt',
        'Flask-Cors',
        'Flask-Limiter',
        'psycopg2-binary',
        'python-dotenv',
        'marshmallow',
        'marshmallow-sqlalchemy',
        'redis',
        'Flask-Caching',
        'celery',
        'Flask-Mail',
        'prometheus-flask-exporter',
        'structlog',
        'sentry-sdk[flask]',
        'requests',
        'gunicorn',
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
            'pytest-timeout',
            'pytest-ordering',
            'flask-testing',
        ],
    },
    entry_points={
        'console_scripts': [
            'recruitconnect=app.cli:main',
        ],
    },
)
