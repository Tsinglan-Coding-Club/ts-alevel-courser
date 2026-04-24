import os
from pathlib import Path


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def env_list(name, default=''):
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(',') if item.strip()]


def env_path(name, default):
    value = os.getenv(name)
    if not value:
        return Path(default)
    path = Path(value)
    if path.is_absolute():
        return path
    return BASE_DIR / path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = env_path('DATA_DIR', BASE_DIR / 'data')
DATA_DIR.mkdir(parents=True, exist_ok=True)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-!*972fdn8(kxr%n8_55rgj#(1&^emepykmut)yfg^gw=7w5)i_')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_bool('DEBUG', True)

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', '*' if DEBUG else '')

# CSRF settings
CSRF_TRUSTED_ORIGINS = env_list(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost:8000,http://127.0.0.1:8000',
)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Local apps
    'accounts',
    'pastpaper',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'pastpaper.context_processors.permissions',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

SQLITE_PATH = env_path('SQLITE_PATH', DATA_DIR / 'db.sqlite3')
SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': SQLITE_PATH,
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = os.getenv('STATIC_URL', '/static/')
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = env_path('STATIC_ROOT', BASE_DIR / 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT.mkdir(parents=True, exist_ok=True)

# Media files (User uploads)
MEDIA_URL = os.getenv('MEDIA_URL', '/media/')
MEDIA_ROOT = env_path('MEDIA_ROOT', DATA_DIR / 'media')
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

# Login URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'pastpaper:home'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

X_FRAME_OPTIONS = "SAMEORIGIN"  # Allow embedding in iframes from the same origin
USE_X_FORWARDED_HOST = env_bool('USE_X_FORWARDED_HOST', True)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', False)
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '0'))

if not DEBUG:
    SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', True)
    CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', True)
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
