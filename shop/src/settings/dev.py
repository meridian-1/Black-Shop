from .base import *

DEBUG = config("DEBUG", default=False, cast=bool)

if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    INTERNAL_IPS = ['127.0.0.1']
