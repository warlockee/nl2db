#!/bin/bash
################################################################################
# Redshift Natural Language Agent - Demo Launcher
# Single entry point for running the interactive CLI
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${CYAN}"
echo "================================================================================"
echo "  Redshift Natural Language Agent - Demo Launcher"
echo "================================================================================"
echo -e "${NC}"

################################################################################
# Function: Check if command exists
################################################################################
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

################################################################################
# Function: Check environment variables
################################################################################
check_env_vars() {
    local missing_vars=()

    if [ -z "$REDSHIFT_USER" ]; then
        missing_vars+=("REDSHIFT_USER")
    fi

    if [ -z "$REDSHIFT_PASSWORD" ]; then
        missing_vars+=("REDSHIFT_PASSWORD")
    fi

    if [ ${#missing_vars[@]} -ne 0 ]; then
        return 1
    fi

    return 0
}

################################################################################
# Function: Load .env file
################################################################################
load_env_file() {
    if [ -f ".env" ]; then
        echo -e "${GREEN}✓${NC} Found .env file, loading environment variables..."
        set -a
        source .env
        set +a
        return 0
    fi
    return 1
}

################################################################################
# Function: Check Python installation
################################################################################
check_python() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        echo -e "${GREEN}✓${NC} Python 3 found: ${PYTHON_VERSION}"
        return 0
    else
        echo -e "${RED}✗${NC} Python 3 not found"
        return 1
    fi
}

################################################################################
# Function: Check Docker installation
################################################################################
check_docker() {
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version 2>&1 | awk '{print $3}' | tr -d ',')
        echo -e "${GREEN}✓${NC} Docker found: ${DOCKER_VERSION}"

        # Check if docker compose is available
        if docker compose version >/dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} Docker Compose available"
            return 0
        fi
    fi
    return 1
}

################################################################################
# Function: Start with Python
################################################################################
start_python() {
    echo ""
    echo -e "${CYAN}Starting with Python method...${NC}"
    echo ""

    # Check if package is installed
    if python3 -c "import redshift_nl_agent" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Package already installed"
    else
        echo -e "${YELLOW}Package not installed. Installing in development mode...${NC}"
        pip install -e . >/dev/null 2>&1 || {
            echo -e "${RED}✗${NC} Failed to install package"
            echo "Try: pip install -e ."
            exit 1
        }
        echo -e "${GREEN}✓${NC} Package installed successfully"
    fi

    echo ""
    echo -e "${GREEN}Launching Interactive CLI...${NC}"
    echo ""

    # Set PYTHONPATH and run
    export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
    python3 -m redshift_nl_agent
}

################################################################################
# Function: Start with Docker
################################################################################
start_docker() {
    echo ""
    echo -e "${CYAN}Starting with Docker method...${NC}"
    echo ""

    # Check if image exists
    if docker images | grep -q "redshift-nl-agent"; then
        echo -e "${GREEN}✓${NC} Docker image exists"
    else
        echo -e "${YELLOW}Docker image not found. Building...${NC}"
        echo "This may take 2-5 minutes..."
        docker build -t redshift-nl-agent:latest -f docker/Dockerfile . || {
            echo -e "${RED}✗${NC} Failed to build Docker image"
            exit 1
        }
        echo -e "${GREEN}✓${NC} Docker image built successfully"
    fi

    echo ""
    echo -e "${GREEN}Launching container...${NC}"
    echo ""

    # Run container (conditionally use -it based on TTY availability)
    if [ -t 0 ]; then
        docker run -it --rm --env-file .env redshift-nl-agent:latest
    else
        docker run -i --rm --env-file .env redshift-nl-agent:latest
    fi
}

################################################################################
# Function: Show usage
################################################################################
show_usage() {
    cat << EOF
${CYAN}Usage:${NC}
  ./start.sh [OPTIONS]

${CYAN}Options:${NC}
  --python          Force use of Python method
  --docker          Force use of Docker method
  --help            Show this help message

${CYAN}Description:${NC}
  This script automatically detects the best way to run the Redshift Natural
  Language Agent and launches the interactive CLI.

  ${YELLOW}Detection Priority:${NC}
  1. If --python or --docker flag is provided, use that method
  2. If Docker is available and .env exists, use Docker (recommended)
  3. Otherwise, use Python method

${CYAN}Prerequisites:${NC}
  - Environment variables (via .env file or exported):
    - REDSHIFT_USER (required)
    - REDSHIFT_PASSWORD (required)
    - REDSHIFT_HOST (optional, has default)
    - REDSHIFT_PORT (optional, has default)
    - REDSHIFT_DATABASE (optional, has default)
    - GEMINI_API_KEY (optional but recommended)

${CYAN}Examples:${NC}
  # Auto-detect and run
  ./start.sh

  # Force Python method
  ./start.sh --python

  # Force Docker method
  ./start.sh --docker

${CYAN}First Time Setup:${NC}
  1. Copy environment template:
     cp config/.env.template .env

  2. Edit .env with your credentials:
     nano .env

  3. Run this script:
     ./start.sh

${CYAN}Interactive Commands:${NC}
  Once running, you can use:
  - Type natural language queries: "Show me the top 10 cameras"
  - /help          - Show available commands
  - /schema        - Display database schema
  - /history       - Show recent queries
  - /explain       - Show SQL for last query
  - /quit          - Exit

EOF
}

################################################################################
# Main Script
################################################################################

# Parse command line arguments
METHOD=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --python)
            METHOD="python"
            shift
            ;;
        --docker)
            METHOD="docker"
            shift
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "Checking prerequisites..."
echo ""

# Check for .env file or environment variables
if load_env_file; then
    ENV_SOURCE=".env file"
elif check_env_vars; then
    ENV_SOURCE="environment variables"
    echo -e "${GREEN}✓${NC} Environment variables are set"
else
    echo -e "${RED}✗${NC} Missing required environment variables"
    echo ""
    echo -e "${YELLOW}Required:${NC}"
    echo "  - REDSHIFT_USER"
    echo "  - REDSHIFT_PASSWORD"
    echo ""
    echo -e "${YELLOW}Setup:${NC}"
    echo "  1. Copy the template: cp config/.env.template .env"
    echo "  2. Edit .env with your credentials"
    echo "  3. Run this script again"
    echo ""
    echo "OR export environment variables:"
    echo "  export REDSHIFT_USER=your_user"
    echo "  export REDSHIFT_PASSWORD=your_password"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓${NC} Credentials loaded from: ${ENV_SOURCE}"
echo ""

# Check Python
PYTHON_AVAILABLE=false
if check_python; then
    PYTHON_AVAILABLE=true
fi

# Check Docker
DOCKER_AVAILABLE=false
if check_docker; then
    DOCKER_AVAILABLE=true
fi

echo ""

# Decide which method to use
if [ -n "$METHOD" ]; then
    # User specified method
    echo -e "${CYAN}Using ${METHOD} method (user specified)${NC}"
    if [ "$METHOD" = "python" ]; then
        if [ "$PYTHON_AVAILABLE" = true ]; then
            start_python
        else
            echo -e "${RED}✗${NC} Python 3 is not available"
            exit 1
        fi
    elif [ "$METHOD" = "docker" ]; then
        if [ "$DOCKER_AVAILABLE" = true ]; then
            start_docker
        else
            echo -e "${RED}✗${NC} Docker is not available"
            exit 1
        fi
    fi
else
    # Auto-detect best method
    if [ "$DOCKER_AVAILABLE" = true ] && [ -f ".env" ]; then
        echo -e "${CYAN}Auto-detected: Using Docker method (recommended)${NC}"
        echo -e "${YELLOW}Tip: Use --python flag to force Python method${NC}"
        start_docker
    elif [ "$PYTHON_AVAILABLE" = true ]; then
        echo -e "${CYAN}Auto-detected: Using Python method${NC}"
        echo -e "${YELLOW}Tip: Use --docker flag to force Docker method${NC}"
        start_python
    else
        echo -e "${RED}✗${NC} Neither Python nor Docker is available"
        echo ""
        echo "Please install either:"
        echo "  - Python 3.8+ (pip install -e .)"
        echo "  - Docker (for containerized deployment)"
        exit 1
    fi
fi
