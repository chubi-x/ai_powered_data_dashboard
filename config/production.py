import os
from .base import *

ALLOWED_HOSTS = ["dash.chubi.dev"]
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "dashboard"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "HOST": "ai_dash_postgres",
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "level": "DEBUG",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
        },
        "dashboard": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "raster": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "chatbot": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
