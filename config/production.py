import os
from .base import *

ALLOWED_HOSTS = ["https://dash.chubi.dev"]
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
