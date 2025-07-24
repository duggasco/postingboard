#!/bin/bash

# Flask Health Monitor Script for Cron
# This script checks the health of the Flask application and restarts it if needed
# Designed to be run hourly via cron

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=9094
APP_NAME="postingboard-flask"
PID_FILE="$SCRIPT_DIR/flask-app.pid"
LOG_FILE="$SCRIPT_DIR/flask-health.log"
LOCK_FILE="$SCRIPT_DIR/flask-health.lock"
HEALTH_URL="http://localhost:$PORT/api/health"
HEALTH_TIMEOUT=10
MAX_LOG_SIZE=10485760  # 10MB
PYTHON_CMD=""

# Function to write log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to rotate log if too large
rotate_log() {
    if [ -f "$LOG_FILE" ]; then
        local file_size=$(stat -c%s "$LOG_FILE" 2>/dev/null || stat -f%z "$LOG_FILE" 2>/dev/null || echo 0)
        if [ "$file_size" -gt $MAX_LOG_SIZE ]; then
            mv "$LOG_FILE" "${LOG_FILE}.old"
            log "Log rotated due to size"
        fi
    fi
}

# Function to check if another instance is running
check_lock() {
    if [ -f "$LOCK_FILE" ]; then
        local lock_pid=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
        if [ -n "$lock_pid" ] && kill -0 "$lock_pid" 2>/dev/null; then
            log "Another health monitor instance is running (PID: $lock_pid). Exiting."
            exit 0
        else
            log "Removing stale lock file"
            rm -f "$LOCK_FILE"
        fi
    fi
    echo $$ > "$LOCK_FILE"
}

# Function to clean up on exit
cleanup() {
    rm -f "$LOCK_FILE"
}
trap cleanup EXIT

# Function to check Python version
check_python_version() {
    # Try Python 3.12 first (preferred)
    if command -v python3.12 &> /dev/null; then
        PYTHON_CMD="python3.12"
    elif command -v python3 &> /dev/null; then
        # Check if python3 is at least 3.8
        PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
            PYTHON_CMD="python3"
        else
            log "Error: Python 3.8 or newer is required (found Python $PYTHON_VERSION)"
            exit 1
        fi
    else
        log "Error: Python 3 is not installed"
        exit 1
    fi
}

# Function to check if Flask process is running
is_process_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE" 2>/dev/null || echo "")
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

# Function to get Flask process PID
get_flask_pid() {
    if [ -f "$PID_FILE" ]; then
        cat "$PID_FILE" 2>/dev/null || echo ""
    else
        # Try to find it by port using various methods
        if command -v lsof &> /dev/null; then
            lsof -ti:$PORT -sTCP:LISTEN 2>/dev/null || echo ""
        elif command -v ss &> /dev/null; then
            ss -tlnp 2>/dev/null | grep ":$PORT" | grep -oP '(?<=pid=)\d+' | head -1 || echo ""
        elif command -v netstat &> /dev/null; then
            netstat -tlnp 2>/dev/null | grep ":$PORT" | grep -oP '\d+(?=/python)' | head -1 || echo ""
        else
            echo ""
        fi
    fi
}

# Function to perform HTTP health check
check_health() {
    local response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout $HEALTH_TIMEOUT --max-time $HEALTH_TIMEOUT "$HEALTH_URL" 2>/dev/null || echo "000")
    
    if [ "$response" = "200" ]; then
        return 0
    else
        log "Health check failed with HTTP status: $response"
        return 1
    fi
}

# Function to stop Flask gracefully
stop_flask() {
    local pid=$(get_flask_pid)
    
    if [ -n "$pid" ]; then
        log "Stopping Flask application (PID: $pid)"
        
        # Try graceful shutdown first
        kill -TERM "$pid" 2>/dev/null || true
        
        # Wait for process to stop
        local count=0
        while kill -0 "$pid" 2>/dev/null && [ $count -lt 30 ]; do
            sleep 1
            count=$((count + 1))
        done
        
        # Force kill if still running
        if kill -0 "$pid" 2>/dev/null; then
            log "Process did not stop gracefully, force killing"
            kill -KILL "$pid" 2>/dev/null || true
            sleep 2
        fi
        
        rm -f "$PID_FILE"
    fi
    
    # Clean up any remaining processes on the port
    local port_pid=""
    if command -v lsof &> /dev/null; then
        port_pid=$(lsof -ti:$PORT -sTCP:LISTEN 2>/dev/null || echo "")
    elif command -v ss &> /dev/null; then
        port_pid=$(ss -tlnp 2>/dev/null | grep ":$PORT" | grep -oP '(?<=pid=)\d+' | head -1 || echo "")
    elif command -v netstat &> /dev/null; then
        port_pid=$(netstat -tlnp 2>/dev/null | grep ":$PORT" | grep -oP '\d+(?=/python)' | head -1 || echo "")
    fi
    
    if [ -n "$port_pid" ]; then
        log "Killing process still using port $PORT (PID: $port_pid)"
        kill -KILL "$port_pid" 2>/dev/null || true
        sleep 2
    fi
}

# Function to start Flask
start_flask() {
    log "Starting Flask application"
    
    # Ensure virtual environment exists
    if [ ! -d "$SCRIPT_DIR/venv" ]; then
        log "Creating virtual environment"
        cd "$SCRIPT_DIR"
        $PYTHON_CMD -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    cd "$SCRIPT_DIR"
    source venv/bin/activate
    
    # Check if requirements need to be installed
    if ! pip show Flask &>/dev/null; then
        log "Installing dependencies"
        pip install -r requirements.txt
    fi
    
    # Change to backend directory
    cd "$SCRIPT_DIR/backend"
    
    # Initialize database if needed
    if [ ! -f "posting_board.db" ]; then
        log "Initializing database"
        python database.py
    fi
    
    # Start Flask in background and save PID
    log "Starting Flask server"
    nohup python app.py > "$SCRIPT_DIR/flask-app.log" 2>&1 &
    local pid=$!
    echo $pid > "$PID_FILE"
    
    # Wait a bit for startup
    sleep 5
    
    # Verify it started successfully
    if kill -0 "$pid" 2>/dev/null; then
        log "Flask application started successfully (PID: $pid)"
        return 0
    else
        log "Flask application failed to start"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Main monitoring logic
main() {
    rotate_log
    log "Starting Flask health monitor"
    
    check_lock
    check_python_version
    
    local restart_needed=false
    local reason=""
    
    # Check if process is running
    if ! is_process_running; then
        reason="Process not running"
        restart_needed=true
    else
        # Process is running, check health
        if ! check_health; then
            reason="Health check failed"
            restart_needed=true
        else
            log "Flask application is healthy"
        fi
    fi
    
    # Restart if needed
    if [ "$restart_needed" = true ]; then
        log "Restart needed: $reason"
        stop_flask
        
        if start_flask; then
            # Verify health after restart
            sleep 10
            if check_health; then
                log "Flask application restarted successfully and is healthy"
                exit 0
            else
                log "Flask application restarted but health check still failing"
                exit 1
            fi
        else
            log "Failed to restart Flask application"
            exit 1
        fi
    fi
    
    log "Health monitor completed successfully"
    exit 0
}

# Run main function
main "$@"