#!/bin/bash
# Script to sync database between native and Docker environments

echo "Database Sync Utility"
echo "===================="

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "Running in Docker container"
    DB_PATH="/app/data/posting_board_uuid.db"
else
    echo "Running in native environment"
    DB_PATH="backend/posting_board_uuid.db"
fi

# For Docker deployment preparation
if [ "$1" == "docker-prep" ]; then
    echo "Preparing database for Docker deployment..."
    if [ -f "backend/posting_board_uuid.db" ]; then
        echo "Database found at backend/posting_board_uuid.db"
        echo "When deploying to Docker, this will be copied to /app/data/"
        echo "Size: $(ls -lh backend/posting_board_uuid.db | awk '{print $5}')"
    else
        echo "Warning: No database found at backend/posting_board_uuid.db"
    fi
fi

# For native deployment preparation
if [ "$1" == "native-prep" ]; then
    echo "Preparing database for native deployment..."
    if [ -f "/app/data/posting_board_uuid.db" ]; then
        echo "Copying Docker database to native location..."
        cp /app/data/posting_board_uuid.db backend/posting_board_uuid.db
        echo "Database copied successfully"
    else
        echo "No Docker database found to copy"
    fi
fi

echo ""
echo "Current database location: $DB_PATH"
if [ -f "$DB_PATH" ]; then
    echo "Database exists - Size: $(ls -lh $DB_PATH | awk '{print $5}')"
else
    echo "Database does not exist at expected location"
fi