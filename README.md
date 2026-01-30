# Browser Butler

AI-powered browser automation with scheduling and Telegram notifications.

## Features

- **Natural Language Tasks**: Describe browser tasks in plain English
- **Scheduled Execution**: Run tasks on a cron schedule
- **Telegram Notifications**: Get notified on task success or failure
- **Web UI**: Manage tasks and view logs through a web interface
- **Real-time Updates**: SSE-based live status updates

## Requirements

- Python 3.11+
- Node.js 18+ (for frontend development)
- OpenAI API key
- Telegram bot token (optional)

## Setup

### 1. Install Python dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 2. Install Playwright browsers

```bash
playwright install chromium
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key

Optional:
- `TELEGRAM_BOT_TOKEN`: Telegram bot token for notifications
- `TELEGRAM_CHAT_ID`: Default chat ID for notifications

### 4. Initialize the database

```bash
PYTHONPATH= uv run python scripts/init_db.py
```

### 5. Start the backend

```bash
uvicorn src.main:app --reload
```

The API will be available at http://localhost:8000

### 6. Start the frontend (development)

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:5173

## Production Build

To build the frontend for production:

```bash
cd frontend
npm run build
```

The built files will be served automatically by the FastAPI backend.

## Linux Deployment (systemd)

For a persistent installation on Linux that starts on boot:

```bash
# Clone and setup
git clone <repo-url> browser-butler
cd browser-butler
./scripts/setup.sh

# Configure your API keys
nano .env

# Start and enable on boot
sudo systemctl start browser-butler
sudo systemctl enable browser-butler
```

The setup script will:
- Install Python dependencies (via uv)
- Build the frontend
- Initialize the database
- Create a systemd service

### Management Commands

```bash
./scripts/ctl.sh start    # Start the service
./scripts/ctl.sh stop     # Stop the service
./scripts/ctl.sh restart  # Restart the service
./scripts/ctl.sh status   # Show service status
./scripts/ctl.sh logs     # Follow service logs
./scripts/ctl.sh update   # Pull latest code and restart
```

Access the UI at http://localhost:8000

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Usage

1. Open the web UI at http://localhost:5173 (dev) or http://localhost:8000 (production)
2. Click "Create Task" to create a new automation task
3. Enter a name and describe the task in natural language
4. Set the cron schedule and notification preferences
5. Save the task

The task will run automatically according to the schedule, or you can click "Run Now" to execute immediately.

## Example Tasks

- "Go to google.com and search for 'weather today'"
- "Navigate to example.com, take a screenshot, and save the page title"
- "Check if the login page at mysite.com is accessible"

## Architecture

- **Backend**: FastAPI + SQLAlchemy + APScheduler
- **Browser Automation**: browser-use + Playwright
- **AI**: OpenAI GPT-4o
- **Frontend**: Vue.js 3 + Vite
- **Real-time**: Server-Sent Events (SSE)
- **Notifications**: Telegram via aiogram

## License

MIT
