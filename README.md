# CTF Bot Helper

A Discord bot that integrates with Google Docs to manage CTF meeting agendas.

## Project Structure

```
ctf-bot-helper/
├── src/
│   └── ctf_bot/           # Main package
│       ├── __init__.py
│       ├── __main__.py    # Entry point for module execution
│       ├── config.py      # Configuration settings
│       ├── discord_bot.py # Discord bot implementation
│       └── integrations/  # External service integrations
│           ├── __init__.py
│           └── google_docs.py  # Google Docs API integration
├── tests/                 # Test files
├── docs/                  # Documentation
├── bot.py                 # Main entry point script
├── pyproject.toml         # Project configuration
└── README.md             # This file
```

## Installation

### Option 1: Docker (Recommended)

1. **Prerequisites**: Install [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)

2. **Configuration**:
   ```bash
   # Copy the example environment file
   cp .secret/.env.example .secret/.env
   
   # Edit .secret/.env with your actual values
   nano .secret/.env
   ```

3. **Place your Google Service Account JSON file** in `.secret/`

4. **Deploy**:
   ```bash
   # Easy deployment script
   ./deploy.sh
   
   # Or manually with docker-compose
   docker-compose up -d
   ```

### Option 2: Local Development

1. Install dependencies:
   ```bash
   pip install -e .
   ```

2. Set up configuration:
   ```bash
   # Copy the example environment file
   cp .secret/.env.example .secret/.env
   
   # Edit .secret/.env with your actual values
   nano .secret/.env
   ```

   The `.env` file should contain:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   GOOGLE_FOLDER_ID=your_google_drive_folder_id_here
   GOOGLE_DOC_NAME=meeting draft
   GOOGLE_SERVICE_ACCOUNT_JSON=.secret/service-account.json
   ```

3. Place your Google Service Account JSON file in `.secret/service-account.json`

4. **Important**: Share both your Google Drive folder AND template documents with your service account email address:
   - Open your Google Drive folder
   - Click "Share" and add your service account email (found in your JSON file as "client_email") 
   - Give it "Editor" permissions
   - Do the same for any template documents you want to use

## Usage

### Running the Bot

**Docker (Recommended)**:
```bash
# Start the bot
./deploy.sh

# View logs
docker-compose logs -f

# Stop the bot
docker-compose down

# Restart the bot
docker-compose restart

# Check status
docker-compose ps
```

**Local Development**:
Run the bot using any of these methods:

1. Direct script execution:
   ```bash
   python bot.py
   ```

2. Module execution:
   ```bash
   python -m ctf_bot
   ```

3. Installed command (after pip install):
   ```bash
   ctf-bot
   ```

## Commands

- `!add-agenda <text>` - Add an item to the meeting agenda in Google Docs
- `!create-doc <name>` - Create a new document from the configured template

## Development

Install development dependencies:
```bash
pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```

Format code:
```bash
black src/
```