from .settings import *


DEBUG = True

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "nations-flow-dev",
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.db"

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
USE_X_FORWARDED_HOST = False
USE_X_FORWARDED_PORT = False
SECURE_PROXY_SSL_HEADER = None

DEFAULT_USER_PASSWORD = os.getenv("DEFAULT_USER_PASSWORD", "change-me")
SYSTEM_HIDDEN_EMAIL = os.getenv("SYSTEM_HIDDEN_EMAIL", "example@example.com")

LOGGING["handlers"].pop("file", None)

for logger_config in LOGGING.get("loggers", {}).values():
    handlers = logger_config.get("handlers", [])
    logger_config["handlers"] = [
        handler for handler in handlers if handler != "file"
    ]
