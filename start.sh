#!/bin/bash
set -e

# Ensure we're using Python 3.8
PYTHON_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [ "$PYTHON_VERSION" != "3.8" ]; then
    echo "Error: Python 3.8 is required but found Python $PYTHON_VERSION"
    exit 1
fi

# Install dependencies using pip with constraints
pip install --no-cache-dir --only-binary :all: -r requirements.txt

# Install the package in development mode
pip install -e .

# Run database migrations if needed
# flask db upgrade

# Start the Gunicorn server
exec gunicorn --config gunicorn_config.py wsgi:app
