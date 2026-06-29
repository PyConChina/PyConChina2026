import os

import dj_database_url

from .base import *

DEBUG = False

SECRET_KEY = os.getenv("SECRET_KEY", "insecure_django_app_key")

ALLOWED_HOSTS = ["127.0.0.1"]

if "SITE_DOMAIN" in os.environ:
    ALLOWED_HOSTS.append(os.environ["SITE_DOMAIN"])
    CSRF_TRUSTED_ORIGINS = [f"https://{os.environ['SITE_DOMAIN']}"]

if "DATABASE_URL" in os.environ:
    DATABASES["default"] = dj_database_url.parse(os.environ["DATABASE_URL"])

if "STATIC_ROOT" in os.environ:
    STATIC_ROOT = os.environ["STATIC_ROOT"]

if "MEDIA_ROOT" in os.environ:
    MEDIA_ROOT = os.environ["MEDIA_ROOT"]

# Loading local settings
try:
    from .local import *
except ImportError:
    pass
