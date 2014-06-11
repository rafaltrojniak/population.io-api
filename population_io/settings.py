"""
Django settings for population_io project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('POPULATIONIO_SECRET_KEY', '0)c2!1m%#%fg1@k)mq&l5df9c8qdq_fh^25v%_s(*kg=ek*qk*')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('POPULATIONIO_DEBUG', 'true').lower() != 'false'

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['population.io', 'www.population.io', '104.130.5.217']


# Application definition

INSTALLED_APPS = (
    'rest_framework',
    'rest_framework_swagger',
    'corsheaders',
    'django.contrib.staticfiles',
    'api',
)

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',   # needs to come before CommonMiddleware
    'django.middleware.common.CommonMiddleware',
)

ROOT_URLCONF = 'population_io.urls'

WSGI_APPLICATION = 'population_io.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
# Here preconfigured for Heroku: https://devcenter.heroku.com/articles/getting-started-with-django#django-settings
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)


# REST Framework configuration
# http://www.django-rest-framework.org/api-guide/settings

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.JSONPRenderer',
    ),
}


# CORS headers configuration
# https://github.com/ottoyiu/django-cors-headers/#configuration

CORS_ORIGIN_ALLOW_ALL = True


# Settings of the api app

DATA_STORE_PATH = os.path.join(BASE_DIR, 'data', 'datastore.hdf5')
CSV_POPULATION_PATH = os.path.join(BASE_DIR, 'data', 'WPP2012_INT_F3_Population_By_Sex_Annual_Single_100_Medium.csv')
CSV_LIFE_EXPECTANCY_PATH = os.path.join(BASE_DIR, 'data', 'life_expectancy_ages.csv')
CACHE_TABLES_IN_MEMORY = DEBUG   # This should only be enabled during development, when working without pregenerated tables.
                                 # There is no limit to the amount of tables cached, so eventually there'll be a MemoryError.
