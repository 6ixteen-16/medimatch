from .base import *
import os
import dj_database_url

DEBUG = False

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True,
    )
}

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# Static files — use plain storage so admin CSS is served without a
# freshly-built manifest file, which is required on PythonAnywhere.
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

# Email — console for now, swap to SES when ready
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable allauth email verification entirely so users are never shown a
# "verification email sent" page.  Staff accounts are still gated by
# is_active=False (admin approval) — that is the only barrier for them.
ACCOUNT_EMAIL_VERIFICATION = 'none'