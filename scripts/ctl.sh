#!/bin/bash

# Browser Butler Control Script
# Usage: ./scripts/ctl.sh [start|stop|restart|status|logs|update]

SERVICE_NAME="browser-butler"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

case "$1" in
    start)
        sudo systemctl start $SERVICE_NAME
        echo "Started $SERVICE_NAME"
        ;;
    stop)
        sudo systemctl stop $SERVICE_NAME
        echo "Stopped $SERVICE_NAME"
        ;;
    restart)
        sudo systemctl restart $SERVICE_NAME
        echo "Restarted $SERVICE_NAME"
        ;;
    status)
        systemctl status $SERVICE_NAME
        ;;
    logs)
        journalctl -u $SERVICE_NAME -f
        ;;
    update)
        echo "Updating $SERVICE_NAME..."
        cd "$PROJECT_DIR"
        git pull
        uv sync

        # Setup node version if nvm/fnm available
        export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
        if [ -s "$NVM_DIR/nvm.sh" ]; then
            \. "$NVM_DIR/nvm.sh"
            cd frontend && nvm use 2>/dev/null || true
        elif command -v fnm >/dev/null 2>&1; then
            eval "$(fnm env)"
            cd frontend && fnm use 2>/dev/null || true
        else
            cd frontend
        fi

        npm install && npm run build
        cd "$PROJECT_DIR"
        sudo systemctl restart $SERVICE_NAME
        echo "Update complete!"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|update}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the service"
        echo "  stop    - Stop the service"
        echo "  restart - Restart the service"
        echo "  status  - Show service status"
        echo "  logs    - Follow service logs"
        echo "  update  - Pull latest code and restart"
        exit 1
        ;;
esac
