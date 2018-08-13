import django

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django_summernote.db',
    }
}

__MIDDLEWARE__ = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

if django.VERSION <= (1, 9):
    MIDDLEWARE_CLASSES = __MIDDLEWARE__
else:
    MIDDLEWARE = __MIDDLEWARE__

STATIC_URL = '/'
MEDIA_ROOT = 'test_media'

SECRET_KEY = 'django_summernote'

ROOT_URLCONF = 'django_summernote.urls'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_summernote',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
            ]
        },
    },
]
