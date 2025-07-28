import sys
from pathlib import Path
from datetime import timedelta
import os
import dj_database_url
from corsheaders.defaults import default_headers

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'key_de_dev_pour_local')
DEBUG = False

ALLOWED_HOSTS = [
    "plateforme-creche.onrender.com",
    "stage-backend-c4pz.onrender.com",
    "plateform-2bjr.onrender.com",
    "shiny-queijadas-52b27c.netlify.app",  # Ajout Netlify ici
]

CSRF_TRUSTED_ORIGINS = [
    "https://plateforme-creche.onrender.com",
    "https://stage-backend-c4pz.onrender.com",
    "https://*.onrender.com",
    "https://shiny-queijadas-52b27c.netlify.app",
    "https://shiny-queijadas-52b27c.netlify.app/",
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_extensions',
    'django_filters',
    'apps.core',
    'apps.users',
    'apps.nurseries',
    'apps.classrooms',
    'apps.children',
    'apps.subscriptions',
    'apps.activities',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Doit être tout en haut
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'stage.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'stage.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR/'dbown.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://plateforme-creche.onrender.com",
    "https://stage-backend-c4pz.onrender.com",
    "https://shiny-queijadas-52b27c.netlify.app",  # Ajout Netlify
]

CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
    "content-type",
    "x-csrftoken",
    "accept",
    "origin",
    "user-agent",
    "x-requested-with",
]

# DRF
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=1440),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Ajoutez ces paramètres à votre settings.py existant

# Upload settings
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024  # 20MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024  # 20MB
FILE_UPLOAD_PERMISSIONS = 0o644

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Extensions autorisées
ALLOWED_FILE_EXTENSIONS = {
    'document': ['.pdf'],
    'image': ['.jpg', '.jpeg', '.png']
}

# Taille maximale des fichiers (en bytes)
MAX_FILE_SIZES = {
    'document': 10 * 1024 * 1024,  # 10MB
    'image': 5 * 1024 * 1024       # 5MB
}



LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,  # ou stderr si tu préfères
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',  # ou INFO pour moins de détails
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
