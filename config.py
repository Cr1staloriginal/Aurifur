import os
from typing import Optional

def _get_env_str(name: str, required: bool = False, default: Optional[str] = None) -> Optional[str]:
    val = os.getenv(name, default)
    if required and (val is None or val == ""):
        raise RuntimeError(f"Required environment variable {name} is not set.")
    return val

def _get_env_int(name: str, required: bool = False, default: int = 0) -> int:
    s = _get_env_str(name, required=required, default=None)
    if s is None or s == "":
        return default
    try:
        return int(s)
    except ValueError:
        raise RuntimeError(f"Environment variable {name} must be an integer, got: {s!r}")

DISCORD_TOKEN = _get_env_str("DISCORD_TOKEN", required=True)
GUILD_ID = _get_env_int("GUILD_ID", required=True)
OWNER_ID = _get_env_int("OWNER_ID", required=False, default=0)

DATABASE_PATH = _get_env_str("DATABASE_PATH", required=False, default="data/aurifur.db")
STATUS_ROTATE_SECONDS = _get_env_int("STATUS_ROTATE_SECONDS", required=False, default=30)
DAILY_UPDATE_HOUR_UTC = _get_env_int("DAILY_UPDATE_HOUR_UTC", required=False, default=0)
