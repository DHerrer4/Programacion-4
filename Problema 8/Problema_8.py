import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")

    # KeyDB (para datos de libros)
    KEYDB_HOST = os.getenv("KEYDB_HOST", "localhost")
    KEYDB_PORT = int(os.getenv("KEYDB_PORT", 6379))
    KEYDB_PASSWORD = os.getenv("KEYDB_PASSWORD") or None

    # Celery (KeyDB como Redis broker/backend)
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

    # Mail
    MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 25))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "False").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "no-reply@example.com")

    # App
    PREFIX = "libro:"
    SCAN_PATTERN = "libro:*"
    NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL")

settings = Settings()