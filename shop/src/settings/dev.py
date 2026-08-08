from .base import *

DEBUG = env.bool("DEBUG", default=False)

SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Database
DATABASES = {"default": env.db("DATABASE_URL")}

# Static files
STATIC_URL = env("STATIC_URL")

MEDIA_URL = env("MEDIA_URL")
MEDIA_ROOT = BASE_DIR / "media"

if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    INTERNAL_IPS = ["127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
ACCOUNT_EMAIL_VERIFICATION = "optional"
