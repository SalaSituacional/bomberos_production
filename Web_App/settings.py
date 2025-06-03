import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.

# Esto lo estoy probando
# BASE_DIR = Path(__file__).resolve().parent.parent / Esta es la original
# Esto es para el render
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-usf!gyb)c_93(yhk-ab2gm%&_(hlk1ough81m110qhhrn4$cvy'

# SECURITY WARNING: don't run with debug turned on in production!
# Debug true significa desarrollo modo de pruebas
DEBUG = True

#------------- modo producción-----------------
# Debug false significa producción, listo para usarse
# DEBUG = False

# ALLOWED_HOSTS = []

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'cuerpobomberossc.com', 'www.cuerpobomberossc.com', 'bomberos-production.onrender.com']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "web",
    "ven911",
    "seguridad_prevencion"
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'web.middleware.LogoutIfAuthenticatedMiddleware',  # Tu middleware existente
    'web.middleware.NoCacheMiddleware',  # Ajusta esto según tu estructura
    'web.middleware.LoadingScreenMiddleware',
    'web.middleware.RegistroPeticionesMiddleware',
]

LOGIN_URL = 'home'  # Cambia esto al nombre de tu URL de inicio de sesión
LOGIN_REDIRECT_URL = '/dashboard/'  # Cambia esto a la vista a la que quieres redirigir después del inicio de sesión

SESSION_COOKIE_AGE = 18000  # Tiempo en segundos
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Cierra sesión al cerrar el navegador

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = 'Web_App.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Web_App.wsgi.application'

# Conexión base de datos del Render (Sala Situacional) 2
DATABASES = {
    'default': dj_database_url.config(default="postgresql://bomberos_dbs_user:sB0cG00nvzS11aSYoROt2wNSWPnSIDyR@dpg-ctct69btq21c7380aogg-a.oregon-postgres.render.com/bomberos_dbs")
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
USE_I18N = True

SESSION_COOKIE_SECURE = False  # Usar cookies seguras solo en HTTPS
CSRF_COOKIE_SECURE = False  # Usar cookies seguras para CSRF

USE_TZ = True
TIME_ZONE = 'America/Caracas'  # Usa la zona horaria de tu región

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

HANDLER404 = 'web.views.custom_404_view'
HANDLER500 = 'web.views.custom_500_view'