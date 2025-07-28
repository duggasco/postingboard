#!/bin/bash

# Ensure data directory exists
mkdir -p /app/data

# Initialize database if it doesn't exist
if [ ! -f "/app/data/posting_board_uuid.db" ]; then
    echo "Database not found. Initializing..."
    # Update database URL to use data directory
    export DATABASE_URL="sqlite:////app/data/posting_board_uuid.db"
    python database.py
    echo "Database initialized successfully."
else
    echo "Database already exists at /app/data/posting_board_uuid.db"
fi

# Ensure the database URL points to the data directory
export DATABASE_URL="sqlite:////app/data/posting_board_uuid.db"

# Start the application
exec "$@"