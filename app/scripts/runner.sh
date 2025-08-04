#!/bin/bash

set -e

echo "$(date) - Waiting for MySQL to be ready..."

# Wait for MySQL to be ready
while ! nc -z db 3306; do
  echo "$(date) - Waiting for MySQL start..."
  sleep 5
done

echo "$(date) - MySQL is ready! Starting Flask application..."

# Start the Flask application
python app.py