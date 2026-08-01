import os
import secrets


def build_config():
    return {
        "SECRET_KEY": os.getenv("SECRET_KEY") or secrets.token_hex(32),
        "DEBUG": os.getenv("FLASK_DEBUG", "false").lower() == "true",
        "DATABASE_PATH": os.getenv("DATABASE_PATH", "loja.db"),
        "ALLOW_ADMIN_ACTIONS": os.getenv("ALLOW_ADMIN_ACTIONS", "false").lower() == "true",
    }
