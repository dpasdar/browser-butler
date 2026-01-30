#!/bin/bash
set -e

# Browser Butler Setup Script
# Run this once to set up the application

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SERVICE_NAME="browser-butler"

echo "=== Browser Butler Setup ==="
echo "Project directory: $PROJECT_DIR"

# Detect OS and systemd availability
IS_LINUX=false
HAS_SYSTEMD=false

if [[ "$(uname)" == "Linux" ]]; then
    IS_LINUX=true
    if command -v systemctl >/dev/null 2>&1 && pidof systemd >/dev/null 2>&1; then
        HAS_SYSTEMD=true
    fi
fi

echo "Platform: $(uname)"
echo "Systemd available: $HAS_SYSTEMD"

# Check if running as root for systemd setup
if [ "$EUID" -eq 0 ]; then
    echo "Please run without sudo. The script will ask for sudo when needed."
    exit 1
fi

# Check for required tools
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed."; exit 1; }

# Node.js version management
REQUIRED_NODE_MAJOR=18

setup_node() {
    # Try to load nvm if available
    export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
    if [ -s "$NVM_DIR/nvm.sh" ]; then
        echo "Found nvm, loading..."
        \. "$NVM_DIR/nvm.sh"

        # Use version from .nvmrc if it exists
        if [ -f "$PROJECT_DIR/frontend/.nvmrc" ]; then
            echo "Installing/using Node version from .nvmrc..."
            cd "$PROJECT_DIR/frontend"
            nvm install
            nvm use
            cd "$PROJECT_DIR"
        fi
        return 0
    fi

    # Try fnm if available
    if command -v fnm >/dev/null 2>&1; then
        echo "Found fnm, setting up Node..."
        eval "$(fnm env)"
        if [ -f "$PROJECT_DIR/frontend/.nvmrc" ]; then
            cd "$PROJECT_DIR/frontend"
            fnm install
            fnm use
            cd "$PROJECT_DIR"
        fi
        return 0
    fi

    # Check system Node version
    if command -v node >/dev/null 2>&1; then
        NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$NODE_VERSION" -ge "$REQUIRED_NODE_MAJOR" ]; then
            echo "Using system Node.js $(node -v)"
            return 0
        else
            echo "WARNING: Node.js $(node -v) is older than required (v$REQUIRED_NODE_MAJOR+)"
            echo "Please install nvm and run: nvm install 20"
            echo "  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash"
            exit 1
        fi
    fi

    echo "Node.js is required but not installed."
    echo "Please install nvm:"
    echo "  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash"
    echo "Then run this setup script again."
    exit 1
}

setup_node

# Check for uv or install it
if ! command -v uv >/dev/null 2>&1; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

cd "$PROJECT_DIR"

# Setup Python environment
echo ""
echo "=== Setting up Python environment ==="
uv sync

# Initialize database
echo ""
echo "=== Initializing database ==="
PYTHONPATH= uv run python scripts/init_db.py

# Build frontend
echo ""
echo "=== Building frontend ==="
cd frontend
npm install
npm run build
cd ..

# Check for .env file
if [ ! -f .env ]; then
    echo ""
    echo "=== Creating .env file ==="
    cp .env.example .env
    echo "IMPORTANT: Edit .env file with your API keys:"
    echo "  $PROJECT_DIR/.env"
fi

# Create systemd service file (Linux only)
if [ "$HAS_SYSTEMD" = true ]; then
    echo ""
    echo "=== Creating systemd service ==="

    SERVICE_FILE="/tmp/${SERVICE_NAME}.service"
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Browser Butler Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$HOME/.local/bin:$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH="
ExecStart=$HOME/.cargo/bin/uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    echo "Installing systemd service (requires sudo)..."
    sudo cp "$SERVICE_FILE" /etc/systemd/system/${SERVICE_NAME}.service
    sudo systemctl daemon-reload

    echo ""
    echo "=== Setup Complete ==="
    echo ""
    echo "Next steps:"
    echo "  1. Edit your configuration: nano $PROJECT_DIR/.env"
    echo "  2. Start the service:       sudo systemctl start $SERVICE_NAME"
    echo "  3. Enable on boot:          sudo systemctl enable $SERVICE_NAME"
    echo "  4. View logs:               journalctl -u $SERVICE_NAME -f"
    echo "  5. Access the UI:           http://localhost:8000"
    echo ""
else
    echo ""
    echo "=== Setup Complete ==="
    echo ""
    echo "Systemd not available. To run manually:"
    echo ""
    echo "  1. Edit your configuration: nano $PROJECT_DIR/.env"
    echo "  2. Start the server:"
    echo "     cd $PROJECT_DIR"
    echo "     PYTHONPATH= uv run uvicorn src.main:app --host 0.0.0.0 --port 8000"
    echo "  3. Access the UI: http://localhost:8000"
    echo ""
fi
