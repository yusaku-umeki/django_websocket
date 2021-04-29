from .base import *  # noqa: F401,F403

DEBUG = True

SECRET_KEY = "django-insecure-xii=$-zom8#x#p$=id2@k%jps@%s)8x_$mb)gs_ijozgt0)izp"

ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
