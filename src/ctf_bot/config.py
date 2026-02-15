"""Configuration settings for the CTF bot."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .secret/.env
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".secret" / ".env"
load_dotenv(env_path)

# ----------------------------
# Config via environment vars
# ----------------------------
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

# Instead of a fixed doc id, we find the doc in a folder by name.
FOLDER_ID = os.environ["GOOGLE_FOLDER_ID"]  # the folder you shared with the service account
TARGET_DOC_NAME = os.environ.get("GOOGLE_DOC_NAME", "meeting draft")
TEMPLATE_DOC_NAME = os.environ.get("TEMPLATE_DOC_NAME", "meeting template")

# Handle relative paths by resolving them relative to project root
_service_account_path = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
if not os.path.isabs(_service_account_path):
    SERVICE_ACCOUNT_FILE = str(project_root / _service_account_path)
else:
    SERVICE_ACCOUNT_FILE = _service_account_path

# Need Docs API (edit doc) + Drive API (search in folder and copy files)
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
