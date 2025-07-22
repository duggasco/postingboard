#!/bin/bash

set -e

PROJECT_NAME="postingboard"
DOCKER_COMPOSE="docker compose"
PID_FILE="/tmp/.${PROJECT_NAME}_pids"

function show_usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  native        Start development servers natively (default)"
    echo "  native-down   Stop native development servers"
    echo "  up            Start services using Docker Compose"
    echo "  build         Build Docker images"
    echo "  rebuild       Force rebuild Docker images"
    echo "  down          Stop and remove containers"
    echo "  clean         Remove containers, images, and volumes"
    echo "  logs          Show logs from Docker containers"
    echo "  help          Show this help message"
    echo ""
}

function start_native() {
    echo "Starting Posting Board Development Environment (Native)..."

    # Start backend
    echo "Starting backend server..."
    cd backend
    source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    python database.py
    python app.py &
    BACKEND_PID=$!

    # Start frontend
    echo "Starting frontend server..."
    cd ../frontend
    npm install
    npm start &
    FRONTEND_PID=$!

    # Save PIDs to file
    echo "$BACKEND_PID $FRONTEND_PID" > "$PID_FILE"

    echo ""
    echo "Development servers started!"
    echo "Backend running at: http://localhost:5000"
    echo "Frontend running at: http://localhost:3000"
    echo ""
    echo "Press Ctrl+C to stop both servers"

    # Wait for Ctrl+C
    trap "kill $BACKEND_PID $FRONTEND_PID; rm -f $PID_FILE" INT
    wait
}

function check_port_conflicts() {
    local has_conflict=false
    
    # Check port 5000
    local BACKEND_PIDS=$(ss -tlnp 2>/dev/null | grep :5000 | grep -oP 'pid=\K[0-9]+' | sort -u || true)
    if [ -z "$BACKEND_PIDS" ]; then
        BACKEND_PIDS=$(timeout 2 lsof -ti :5000 2>/dev/null || true)
    fi
    
    # Check port 3000
    local FRONTEND_PIDS=$(ss -tlnp 2>/dev/null | grep :3000 | grep -oP 'pid=\K[0-9]+' | sort -u || true)
    if [ -z "$FRONTEND_PIDS" ]; then
        FRONTEND_PIDS=$(timeout 2 lsof -ti :3000 2>/dev/null || true)
    fi
    
    if [ ! -z "$BACKEND_PIDS" ]; then
        echo "⚠️  Port 5000 is already in use by process(es): $BACKEND_PIDS"
        has_conflict=true
    fi
    
    if [ ! -z "$FRONTEND_PIDS" ]; then
        echo "⚠️  Port 3000 is already in use by process(es): $FRONTEND_PIDS"
        has_conflict=true
    fi
    
    if [ "$has_conflict" = true ]; then
        echo ""
        echo "Would you like to stop these processes? (y/N)"
        read -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if [ ! -z "$BACKEND_PIDS" ]; then
                for PID in $BACKEND_PIDS; do
                    echo "Stopping PID $PID (port 5000)..."
                    kill $PID 2>/dev/null || true
                done
            fi
            if [ ! -z "$FRONTEND_PIDS" ]; then
                for PID in $FRONTEND_PIDS; do
                    echo "Stopping PID $PID (port 3000)..."
                    kill $PID 2>/dev/null || true
                done
            fi
            echo "Processes stopped. Continuing with Docker startup..."
            sleep 1
        else
            echo "Aborting Docker startup due to port conflicts."
            echo "You can run './start-dev.sh native-down' to stop native servers."
            exit 1
        fi
    fi
}

function stop_native() {
    echo "Stopping native development servers..."
    
    if [ -f "$PID_FILE" ]; then
        PIDS=$(cat "$PID_FILE")
        for PID in $PIDS; do
            if kill -0 $PID 2>/dev/null; then
                echo "Stopping process $PID..."
                kill $PID
            else
                echo "Process $PID not found (already stopped?)"
            fi
        done
        rm -f "$PID_FILE"
        echo "Native servers stopped."
    else
        echo "No PID file found. Native servers may not be running."
        echo ""
        echo "Looking for running processes..."
        
        # Try to find processes by port using ss (more robust than lsof)
        # Extract PIDs from ss output
        BACKEND_PIDS=$(ss -tlnp 2>/dev/null | grep :5000 | grep -oP 'pid=\K[0-9]+' | sort -u)
        FRONTEND_PIDS=$(ss -tlnp 2>/dev/null | grep :3000 | grep -oP 'pid=\K[0-9]+' | sort -u)
        
        # Fallback to lsof if ss doesn't work
        if [ -z "$BACKEND_PIDS" ]; then
            BACKEND_PIDS=$(timeout 2 lsof -ti :5000 2>/dev/null || true)
        fi
        if [ -z "$FRONTEND_PIDS" ]; then
            FRONTEND_PIDS=$(timeout 2 lsof -ti :3000 2>/dev/null || true)
        fi
        
        if [ ! -z "$BACKEND_PIDS" ]; then
            echo "Found backend process(es) on port 5000:"
            for PID in $BACKEND_PIDS; do
                echo "  Stopping PID: $PID"
                kill $PID 2>/dev/null || true
            done
            echo "Backend stopped."
        fi
        
        if [ ! -z "$FRONTEND_PIDS" ]; then
            echo "Found frontend process(es) on port 3000:"
            for PID in $FRONTEND_PIDS; do
                echo "  Stopping PID: $PID"
                kill $PID 2>/dev/null || true
            done
            echo "Frontend stopped."
        fi
        
        if [ -z "$BACKEND_PIDS" ] && [ -z "$FRONTEND_PIDS" ]; then
            echo "No running servers found on ports 5000 or 3000."
        fi
    fi
}

function docker_up() {
    echo "Starting Posting Board with Docker Compose..."
    
    # Check for port conflicts before starting
    check_port_conflicts
    
    $DOCKER_COMPOSE up -d
    
    # Wait a moment for containers to start
    sleep 2
    
    # Show container status
    echo ""
    echo "Container status:"
    $DOCKER_COMPOSE ps
    
    echo ""
    echo "Services started!"
    echo "Backend running at: http://localhost:5000"
    echo "Frontend running at: http://localhost:3000"
    echo ""
    echo "Use '$0 logs' to view logs"
    echo "Use '$0 down' to stop services"
}

function docker_build() {
    echo "Building Docker images..."
    $DOCKER_COMPOSE build
    echo "Build complete!"
}

function docker_rebuild() {
    echo "Rebuilding Docker images (no cache)..."
    $DOCKER_COMPOSE build --no-cache
    echo "Rebuild complete!"
}

function docker_down() {
    echo "Stopping Docker containers..."
    $DOCKER_COMPOSE down
    echo "Containers stopped and removed."
}

function docker_clean() {
    echo "Cleaning up Docker resources..."
    echo "This will remove:"
    echo "  - All containers for this project"
    echo "  - All images for this project"
    echo "  - All volumes for this project"
    echo ""
    read -p "Are you sure? (y/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        $DOCKER_COMPOSE down -v --rmi all
        echo "Cleanup complete!"
    else
        echo "Cleanup cancelled."
    fi
}

function docker_logs() {
    echo "Showing logs (press Ctrl+C to exit)..."
    $DOCKER_COMPOSE logs -f
}

# Main script logic
case "${1:-native}" in
    native)
        start_native
        ;;
    native-down)
        stop_native
        ;;
    up)
        docker_up
        ;;
    build)
        docker_build
        ;;
    rebuild)
        docker_rebuild
        ;;
    down)
        docker_down
        ;;
    clean)
        docker_clean
        ;;
    logs)
        docker_logs
        ;;
    help)
        show_usage
        ;;
    *)
        echo "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac