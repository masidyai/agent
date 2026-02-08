#!/usr/bin/env bash
# Render build script for Masidy Backend

set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations
python -m alembic upgrade head

echo "Build completed successfully!"
