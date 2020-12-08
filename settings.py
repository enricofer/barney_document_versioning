import os
import tempfile
import socket
import datetime


DEBUG = True

SECRET_KEY = 'legaltextexamples'

USE_TZ = True

JWT_ALLOW_REFRESH = True
JWT_EXPIRATION_DELTA = datetime.timedelta(hours=2)

CORS_ORIGIN_ALLOW_ALL = True

if socket.gethostname() == "sit008798":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'BARNEY',
            'USER': 'dev',
            'PASSWORD' : 'devel$',
            'HOST' : 'localhost' ,
            'PORT' : '',
        },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(os.path.dirname(__file__), 'db.sqlite3'),
        }
    }

BARNEY_CONFIG = {
    "title": "BARNEY DOCUMENT VERSIONING SYSTEM",
    #"backend": "https://rapper.comune.padova.it",
    #"link": "https://rapper.comune.padova.it",
    "backend": "http://localhos:8000",
    "link": "http://localhos:8000/version/",
    "lang": "en"
}

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'corsheaders',
    #'markymark',
    'version',
)

ALLOWED_HOSTS = '*'

ROOT_URLCONF = 'urls'

SITE_ID = 1
LANGUAGES = (('en-us', 'en-us'),)

MEDIA_ROOT = tempfile.mkdtemp()
MEDIA_URL = '/media/'

STATIC_ROOT = tempfile.mkdtemp()
STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'corsheaders.middleware.CorsPostCsrfMiddleware',
    #'version.enable_cors.CustomCorsMiddleware',
    'jwt_auth.middleware.JWTAuthenticationMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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
                'django.template.context_processors.static',
            ],
        },
    },
]
