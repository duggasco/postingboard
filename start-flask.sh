#!/bin/bash

# Start Flask version of Posting Board

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PORT=9094
PROJECT_NAME="postingboard-flask"

# Parse command line arguments
COMMAND="${1:-up}"

# Function to check if port is in use
check_port() {
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}Error: Port $PORT is already in use${NC}"
        echo "Please stop the service using this port or choose a different port"
        exit 1
    fi
}

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
            echo -e "${RED}Error: Python 3.8 or newer is required (found Python $PYTHON_VERSION)${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Error: Python 3 is not installed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Using $PYTHON_CMD (version $(${PYTHON_CMD} --version))${NC}"
}

# Function to run in Docker mode
run_docker() {
    case "$COMMAND" in
        up)
            echo -e "${GREEN}Starting Flask Posting Board with Docker...${NC}"
            check_port
            docker compose -f docker-compose-flask.yml up -d --build
            echo -e "${GREEN}Flask application started on http://localhost:$PORT${NC}"
            ;;
        down)
            echo -e "${YELLOW}Stopping Flask Posting Board...${NC}"
            docker compose -f docker-compose-flask.yml down
            ;;
        logs)
            docker compose -f docker-compose-flask.yml logs -f
            ;;
        restart)
            echo -e "${YELLOW}Restarting Flask Posting Board...${NC}"
            docker compose -f docker-compose-flask.yml restart
            ;;
        *)
            echo "Usage: $0 [up|down|logs|restart]"
            exit 1
            ;;
    esac
}

# Function to run in native mode
run_native() {
    check_python_version
    
    case "$COMMAND" in
        up)
            echo -e "${GREEN}Starting Flask Posting Board in native mode...${NC}"
            check_port
            
            # Set up virtual environment if it doesn't exist
            if [ ! -d "venv" ]; then
                echo -e "${YELLOW}Creating virtual environment...${NC}"
                $PYTHON_CMD -m venv venv
            fi
            
            # Activate virtual environment
            source venv/bin/activate
            
            # Install/update dependencies
            echo -e "${YELLOW}Installing dependencies...${NC}"
            pip install -r requirements.txt
            
            # Change to backend directory
            cd backend
            
            # Initialize database if needed
            if [ ! -f "posting_board.db" ]; then
                echo -e "${YELLOW}Initializing database...${NC}"
                python database.py
            fi
            
            # Start the Flask application
            echo -e "${GREEN}Starting Flask server on http://localhost:$PORT${NC}"
            python app.py
            ;;
        down)
            echo -e "${YELLOW}Please use Ctrl+C to stop the Flask server${NC}"
            ;;
        *)
            echo "Usage: $0 [up|down] - in native mode, only 'up' and 'down' are supported"
            exit 1
            ;;
    esac
}

# Main execution
if command -v docker &> /dev/null && docker compose version &> /dev/null 2>&1; then
    # Docker is available
    if [ "$COMMAND" == "native" ]; then
        # Force native mode
        COMMAND="up"
        run_native
    else
        run_docker
    fi
else
    # No Docker, use native mode
    echo -e "${YELLOW}Docker not found, using native Python mode${NC}"
    run_native
fi