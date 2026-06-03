from .base import *
import dj_database_url

DEBUG = False
DATABASES = {'default': dj_database_url.config(conn_max_age=600, ssl_require=True)}
EMAIL_BACKEND = 'django_ses.SESBackend'
ALLOWED_HOSTS = [os.environ['ALLOWED_HOST']]
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
