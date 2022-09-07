"""
Django settings for aurora project.

Generated by 'django-admin startproject' using Django 1.11.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

from aurora import config
from aurora.fips_monkey_patch import monkey_patch_md5

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.DJANGO_SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.DJANGO_DEBUG

ALLOWED_HOSTS = config.DJANGO_ALLOWED_HOSTS

BASE_URL = config.DJANGO_BASE_URL

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_cron",
    "rest_framework",
    "bag_transfer",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "bag_transfer.middleware.cognito.CognitoAppMiddleware",
    "bag_transfer.middleware.cognito.CognitoUserMiddleware",
    # "bag_transfer.middleware.jwt.AuthenticationMiddlewareJWT",
]

ROOT_URLCONF = "aurora.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "bag_transfer", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "bag_transfer.context_processors.gtm_id",
            ],
        },
    },
]

LOGIN_REDIRECT_URL = "app_home"

WSGI_APPLICATION = "aurora.wsgi.application"

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # "rest_framework_jwt.authentication.JSONWebTokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
}

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": config.SQL_ENGINE,
        "NAME": config.SQL_DATABASE,
        "USER": config.SQL_USER,
        "PASSWORD": config.SQL_PASSWORD,
        "HOST": config.SQL_HOST,
        "PORT": config.SQL_PORT,
        "OPTIONS": {"charset": "utf8mb4"}
    }
}

AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

# Amazon Cognito
COGNITO_USE = config.COGNITO_USE
COGNITO_USER_POOL = config.COGNITO_USER_POOL
COGNITO_REGION = config.COGNITO_REGION
COGNITO_ACCESS_KEY = config.COGNITO_ACCESS_KEY
COGNITO_SECRET_KEY = config.COGNITO_SECRET_KEY

# COGNITO_CLIENT
COGNITO_CLIENT = {
    'client_id': config.COGNITO_CLIENT_ID,
    'client_secret': config.COGNITO_CLIENT_SECRET_KEY,
    'access_token_url': f"{config.COGNITO_CLIENT_BASE_URL}/oauth2/token",
    'authorize_url': f"{config.COGNITO_CLIENT_BASE_URL}/oauth2/authorize",
    'api_base_url': config.COGNITO_CLIENT_BASE_URL,
    'redirect_uri': config.COGNITO_CLIENT_CALLBACK_URL,
    'client_kwargs': {
        'token_endpoint_auth_method': 'client_secret_basic',
    },
    'userinfo_endpoint': '/oauth2/userInfo',
    'jwks_url': f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL}/.well-known/jwks.json",
}

COGNITO_CLIENT_CALLBACK_URL = config.COGNITO_CLIENT_CALLBACK_URL

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator", },
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator", },
]

AUTH_USER_MODEL = "bag_transfer.User"
LOGIN_REDIRECT_URL = "/app"

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = config.DJANGO_TIME_ZONE
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Transfer settings
STORAGE_ROOT_DIR = config.TRANSFER_STORAGE_ROOT_DIR
DELIVERY_QUEUE_DIR = config.TRANSFER_DELIVERY_QUEUE_DIR
TRANSFER_FILESIZE_MAX = config.TRANSFER_FILESIZE_MAX
TRANSFER_UPLOADS_ROOT = config.TRANSFER_UPLOADS_ROOT
TRANSFER_EXTRACT_TMP = config.TRANSFER_EXTRACT_TMP
UPLOAD_LOG_FILE = config.TRANSFER_UPLOAD_LOG_FILE


# Django Cron
CRON_CLASSES = [
    "bag_transfer.lib.cron.DiscoverTransfers",
    "bag_transfer.lib.cron.DeliverTransfers",
]

# Django Cron Lock
DJANGO_CRON_LOCK_BACKEND = "django_cron.backends.lock.file.FileLock"
DJANGO_CRON_LOCKFILE_PATH = config.DJANGO_CRON_LOCKFILE_PATH

# Email
EMAIL_HOST = config.EMAIL_HOST
EMAIL_PORT = config.EMAIL_PORT
EMAIL_HOST_USER = config.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = config.EMAIL_HOST_PASSWORD
EMAIL_USE_TLS = config.EMAIL_USE_TLS
EMAIL_USE_SSL = config.EMAIL_USE_SSL
DEFAULT_FROM_EMAIL = config.EMAIL_DEFAULT_FROM_EMAIL
PASSWORD_RESET_TIMEOUT_DAYS = config.EMAIL_PASSWORD_RESET_TIMEOUT_DAYS

# Unit Test configs
TEST_BAGS_DIR = config.TEST_BAGS_DIR
TEST_USER = {'USERNAME': config.TEST_USER_USERNAME, 'PASSWORD': config.TEST_USER_PASSWORD}

# Post-accession callbacks
DELIVERY_URL = getattr(config, "DELIVERY_URL", None)
DELIVERY_API_KEY = getattr(config, "DELIVERY_API_KEY", None)

# ArchivesSpace configs
ASPACE = {
    "baseurl": config.ASPACE_BASEURL,
    "username": config.ASPACE_USERNAME,
    "password": config.ASPACE_PASSWORD,
    "repo_id": config.ASPACE_REPO_ID,
}

# Google Analytics configs
GTM_ID = config.GTM_ID

# List of colors used in dashboard for record types
RECORD_TYPE_COLORS = [
    "#f56954",
    "#00a65a",
    "#f39c12",
    "#00c0ef",
    "#3c8dbc",
    "#d2d6de",
    "#f56954",
    "#00a65a",
    "#f39c12",
    "#00c0ef",
    "#3c8dbc",
    "#d2d6de",
    "#f56954",
    "#00a65a",
    "#f39c12",
    "#00c0ef",
    "#3c8dbc",
    "#d2d6de",
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Addresses FIPS error caused by Django using MD5 to generate cache keys and database object names
modules_to_patch = [
    'django.contrib.staticfiles.storage',
    'django.core.cache.backends.filebased',
    'django.core.cache.utils',
    'django.db.backends.utils',
    'django.utils.cache',
]
try:
    import hashlib
    hashlib.md5()
except ValueError:
    monkey_patch_md5(modules_to_patch)
