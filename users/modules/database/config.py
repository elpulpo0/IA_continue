from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

USERS_DATABASE_PATH = DATABASE_DIR / "users.db"

USERS_DATABASE_URL = f"sqlite:///{USERS_DATABASE_PATH}"

INITIAL_USERS_CONFIG_PATH = BASE_DIR / "modules" / "api" / "users" / "initial_users.yaml"