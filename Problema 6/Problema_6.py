import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")

    # KeyDB
    KEYDB_HOST = os.getenv("KEYDB_HOST", "localhost")
    KEYDB_PORT = int(os.getenv("KEYDB_PORT", 6379))
    KEYDB_PASSWORD = os.getenv("KEYDB_PASSWORD") or None

    # Nombres de claves/conjuntos auxiliares
    PREFIX = "libro:"           # cada libro se guarda como libro:<uuid>
    SCAN_PATTERN = "libro:*"    # para listados/búsquedas

settings = Settings()