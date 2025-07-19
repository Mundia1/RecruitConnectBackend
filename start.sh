#!/bin/bash
set -e

# Install dependencies
pip install -e .

# Run database migrations if needed
# flask db upgrade

# Start the Gunicorn server
exec gunicorn --config gunicorn_config.py wsgi:app
