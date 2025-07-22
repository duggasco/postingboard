#!/bin/bash

# Citizen Developer Posting Board - Dash Development Script
# Usage: ./start-dash.sh [up|down|logs|build|rebuild|clean]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print colored output
print_color() {
    echo -e "${2}${1}${NC}"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if command_exists lsof; then
        timeout 2 lsof -i :$port >/dev/null 2>&1
    else
        timeout 2 nc -z localhost $port >/dev/null 2>&1
    fi
}

# Function to find process using port
find_port_process() {
    local port=$1
    if command_exists ss; then
        ss -tlnp 2>/dev/null | grep ":$port" | awk '{print $NF}' | grep -o '[0-9]*' | head -1
    elif command_exists lsof; then
        timeout 2 lsof -ti :$port 2>/dev/null | head -1
    fi
}

# Function to start native development
start_native() {
    print_color "Starting Dash app in native mode..." "$GREEN"
    
    # Check Python
    if ! command_exists python3 && ! command_exists python; then
        print_color "Error: Python is not installed" "$RED"
        exit 1
    fi
    
    # Check if port 9094 is in use
    if check_port 9094; then
        print_color "Port 9094 is already in use" "$YELLOW"
        local pid=$(find_port_process 9094)
        if [ ! -z "$pid" ]; then
            print_color "Process $pid is using port 9094" "$YELLOW"
            read -p "Do you want to stop it? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                kill $pid 2>/dev/null || sudo kill $pid
                sleep 2
            else
                exit 1
            fi
        fi
    fi
    
    # Setup virtual environment if it doesn't exist (in root)
    if [ ! -d "venv" ]; then
        print_color "Creating virtual environment with Python 3.12..." "$YELLOW"
        # Check if python3.12 is available
        if command_exists python3.12; then
            python3.12 -m venv venv
        else
            print_color "Python 3.12 not found. Would you like to download and install it? (y/n)" "$YELLOW"
            read -p "" -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                # Detect OS and architecture
                OS=$(uname -s)
                ARCH=$(uname -m)
                
                if [ "$OS" = "Linux" ]; then
                    print_color "Installing Python 3.12 on Linux..." "$GREEN"
                    
                    # Check if we have apt-get (Debian/Ubuntu)
                    if command_exists apt-get; then
                        print_color "Using apt to install Python 3.12..." "$YELLOW"
                        sudo apt update
                        sudo apt install -y software-properties-common
                        sudo add-apt-repository -y ppa:deadsnakes/ppa
                        sudo apt update
                        sudo apt install -y python3.12 python3.12-venv python3.12-dev
                    # Check if we have yum (RHEL/CentOS/Fedora)
                    elif command_exists yum; then
                        print_color "Using yum to install Python 3.12..." "$YELLOW"
                        sudo yum install -y epel-release
                        sudo yum install -y python3.12 python3.12-devel
                    # Build from source as fallback
                    else
                        print_color "Building Python 3.12 from source..." "$YELLOW"
                        cd /tmp
                        wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz
                        tar -xf Python-3.12.0.tgz
                        cd Python-3.12.0
                        ./configure --enable-optimizations
                        make -j $(nproc)
                        sudo make altinstall
                        cd -
                    fi
                elif [ "$OS" = "Darwin" ]; then
                    print_color "Installing Python 3.12 on macOS..." "$GREEN"
                    
                    # Check if homebrew is installed
                    if command_exists brew; then
                        print_color "Using Homebrew to install Python 3.12..." "$YELLOW"
                        brew install python@3.12
                    else
                        print_color "Homebrew not found. Installing Homebrew first..." "$YELLOW"
                        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                        brew install python@3.12
                    fi
                else
                    print_color "Unsupported OS: $OS. Please install Python 3.12 manually." "$RED"
                    exit 1
                fi
                
                # Check if installation was successful
                if command_exists python3.12; then
                    print_color "Python 3.12 installed successfully!" "$GREEN"
                    python3.12 -m venv venv
                else
                    print_color "Python 3.12 installation failed. Using default Python 3..." "$RED"
                    python3 -m venv venv || python -m venv venv
                fi
            else
                print_color "Using default Python 3..." "$YELLOW"
                python3 -m venv venv || python -m venv venv
            fi
        fi
    fi
    
    # Activate virtual environment
    source venv/bin/activate || source venv/Scripts/activate
    
    # Configure pip for proxy if environment variables are set
    if [ ! -z "$HTTP_PROXY" ] || [ ! -z "$http_proxy" ]; then
        PROXY="${HTTP_PROXY:-$http_proxy}"
        print_color "Configuring pip for HTTP proxy: $PROXY" "$YELLOW"
        pip config set global.proxy "$PROXY"
    fi
    
    if [ ! -z "$HTTPS_PROXY" ] || [ ! -z "$https_proxy" ]; then
        PROXY="${HTTPS_PROXY:-$https_proxy}"
        print_color "Configuring pip for HTTPS proxy: $PROXY" "$YELLOW"
        pip config set global.proxy "$PROXY"
    fi
    
    # Install dependencies from root requirements.txt
    print_color "Installing dependencies..." "$YELLOW"
    pip install -r requirements.txt
    
    # Now change to backend directory for running the app
    cd backend
    
    # Initialize database if needed
    if [ ! -f "posting_board.db" ]; then
        print_color "Initializing database..." "$YELLOW"
        python database.py
    fi
    
    # Start Dash app
    print_color "Starting Dash app on http://localhost:9094" "$GREEN"
    python dash_app.py
}

# Function to start Docker development
start_docker() {
    print_color "Starting Dash app with Docker..." "$GREEN"
    
    # Check Docker
    if ! command_exists docker; then
        print_color "Error: Docker is not installed" "$RED"
        exit 1
    fi
    
    # Check if port 9094 is in use
    if check_port 9094; then
        print_color "Port 9094 is already in use" "$YELLOW"
        local pid=$(find_port_process 9094)
        if [ ! -z "$pid" ]; then
            print_color "Process $pid is using port 9094" "$YELLOW"
            read -p "Do you want to stop it? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                kill $pid 2>/dev/null || sudo kill $pid
                sleep 2
            else
                exit 1
            fi
        fi
    fi
    
    # Start containers
    docker compose -f docker-compose-dash.yml up -d
    
    # Wait and show status
    sleep 2
    print_color "\nContainer status:" "$GREEN"
    docker compose -f docker-compose-dash.yml ps
    
    print_color "\nDash app is starting on http://localhost:9094" "$GREEN"
    print_color "View logs with: ./start-dash.sh logs" "$YELLOW"
}

# Function to stop services
stop_services() {
    print_color "Stopping services..." "$YELLOW"
    
    # Stop Docker if running
    if command_exists docker && docker compose -f docker-compose-dash.yml ps -q 2>/dev/null | grep -q .; then
        print_color "Stopping Docker containers..." "$YELLOW"
        docker compose -f docker-compose-dash.yml down
    fi
    
    # Stop native processes
    if check_port 9094; then
        local pid=$(find_port_process 9094)
        if [ ! -z "$pid" ]; then
            print_color "Stopping process on port 9094 (PID: $pid)..." "$YELLOW"
            kill $pid 2>/dev/null || sudo kill $pid
        fi
    fi
    
    print_color "Services stopped" "$GREEN"
}

# Main script logic
case "${1:-native}" in
    native)
        start_native
        ;;
    up)
        start_docker
        ;;
    down)
        stop_services
        ;;
    logs)
        docker compose -f docker-compose-dash.yml logs -f
        ;;
    build)
        print_color "Building Docker images..." "$YELLOW"
        docker compose -f docker-compose-dash.yml build
        ;;
    rebuild)
        print_color "Rebuilding Docker images without cache..." "$YELLOW"
        docker compose -f docker-compose-dash.yml build --no-cache
        ;;
    clean)
        print_color "Cleaning up Docker resources..." "$YELLOW"
        docker compose -f docker-compose-dash.yml down -v --rmi all
        ;;
    *)
        print_color "Usage: $0 [native|up|down|logs|build|rebuild|clean]" "$YELLOW"
        echo "  native  - Start Dash app natively (default)"
        echo "  up      - Start services with Docker"
        echo "  down    - Stop all services"
        echo "  logs    - View Docker logs"
        echo "  build   - Build Docker images"
        echo "  rebuild - Rebuild images without cache"
        echo "  clean   - Remove all Docker resources"
        exit 1
        ;;
esac