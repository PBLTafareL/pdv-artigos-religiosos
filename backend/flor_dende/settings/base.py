from pathlib import Path
from decouple import config
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY   = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'apps.core',
    'apps.accounts',
    'apps.products',
    'apps.pdv',
    'apps.quotations',
    'apps.invoices',
    'apps.loyalty',
    'apps.dashboard',
    'apps.reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF     = 'flor_dende.urls'
WSGI_APPLICATION = 'flor_dende.wsgi.application'
AUTH_USER_MODEL  = 'accounts.User'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

DATABASES = {'default': {
    'ENGINE':   config('DB_ENGINE', default='django.db.backends.mysql'),
    'NAME':     config('DB_NAME',   default='flor_dende_pdv'),
    'USER':     config('DB_USER',   default='flor_dende_user'),
    'PASSWORD': config('DB_PASSWORD'),
    'HOST':     config('DB_HOST',   default='127.0.0.1'),
    'PORT':     config('DB_PORT',   default='3306'),
    'OPTIONS':  {'charset': 'utf8mb4', 'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"},
}}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE     = 'America/Fortaleza'
USE_I18N      = True
USE_TZ        = True

STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL   = '/media/'
MEDIA_ROOT  = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
    'DEFAULT_PERMISSION_CLASSES':     ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_FILTER_BACKENDS':        ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS':       'apps.core.pagination.StandardPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(minutes=config('JWT_ACCESS_MINUTES', default=480, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_DAYS',     default=7,   cast=int)),
    'ROTATE_REFRESH_TOKENS':  True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

CORS_ALLOWED_ORIGINS = config('CORS_ORIGINS', default='http://localhost:5173').split(',')
CORS_ALLOW_CREDENTIALS = True

PONTOS_POR_REAL       = config('PONTOS_POR_REAL',       default=1,  cast=int)
MINIMO_RESGATE_PONTOS = config('MINIMO_RESGATE_PONTOS', default=100, cast=int)
COMPRAS_PARA_VOUCHER  = config('COMPRAS_PARA_VOUCHER',  default=10,  cast=int)
VALOR_VOUCHER         = config('VALOR_VOUCHER',         default=50,  cast=int)

LOGGING = {
    'version': 1, 'disable_existing_loggers': False,
    'formatters': {'verbose': {'format': '{levelname} {asctime} {module} {message}', 'style': '{'}},
    'handlers': {
        'file':    {'class': 'logging.FileHandler', 'filename': BASE_DIR/'logs'/'errors.log', 'formatter': 'verbose'},
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
    },
    'root': {'handlers': ['file', 'console'], 'level': config('LOG_LEVEL', default='ERROR')},
}
