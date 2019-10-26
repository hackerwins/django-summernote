import os
import uuid
from datetime import datetime
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage
from django.utils.translation import get_language
from functools import wraps
from importlib import import_module

# A conversion table from language to locale
LANG_TO_LOCALE = {
    'ar': 'ar-AR',
    'bg': 'bg-BG',
    'ca': 'ca-ES',
    'cs': 'cs-CZ',
    'da': 'da-DK',
    'de': 'de-DE',
    'el': 'el-GR',
    'en': 'en-US',
    'es': 'es-ES',
    'fa': 'fa-IR',
    'fi': 'fi-FI',
    'fr': 'fr-FR',
    'gl': 'gl-ES',
    'he': 'he-IL',
    'hr': 'hr-HR',
    'hu': 'hu-HU',
    'id': 'id-ID',
    'it': 'it-IT',
    'ja': 'ja-JP',
    'ko': 'ko-KR',
    'lt': 'lt-LT',
    'mn': 'mn-MN',
    'nb': 'nb-NO',
    'nl': 'nl-NL',
    'pl': 'pl-PL',
    'pt': 'pt-BR',
    'ro': 'ro-RO',
    'ru': 'ru-RU',
    'sk': 'sk-SK',
    'sl': 'sl-SI',
    'sr': 'sr-RS',
    'sv': 'sv-SE',
    'ta': 'ta-IN',
    'th': 'th-TH',
    'tr': 'tr-TR',
    'uk': 'uk-UA',
    'uz': 'uz-UZ',
    'vi': 'vi-VN',
    'zh': 'zh-CN',
}

# Theme files dictionary
SUMMERNOTE_THEME_FILES = {
    'bs3': {
        'base_css': (
            '//stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css',
        ),
        'base_js': (
            '//code.jquery.com/jquery-3.3.1.min.js',
            '//stackpath.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js',
        ),
        'default_css': (
            'summernote/summernote.css',
            'summernote/django_summernote.css',
        ),
        'default_js': (
            'summernote/jquery.ui.widget.js',
            'summernote/jquery.iframe-transport.js',
            'summernote/jquery.fileupload.js',
            'summernote/summernote.min.js',
            'summernote/ResizeSensor.js',
        ),
    },
    'bs4': {
        'base_css': (
            '//stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css',
        ),
        'base_js': (
            '//code.jquery.com/jquery-3.3.1.min.js',
            '//stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.bundle.min.js',
        ),
        'default_css': (
            'summernote/summernote-bs4.css',
            'summernote/django_summernote.css',
        ),
        'default_js': (
            'summernote/jquery.ui.widget.js',
            'summernote/jquery.iframe-transport.js',
            'summernote/jquery.fileupload.js',
            'summernote/summernote-bs4.min.js',
            'summernote/ResizeSensor.js',
        ),
    },
    'lite': {
        'base_css': (),
        'base_js': (
            '//code.jquery.com/jquery-3.3.1.min.js',
        ),
        'default_css': (
            'summernote/summernote-lite.css',
            'summernote/django_summernote.css',
        ),
        'default_js': (
            'summernote/jquery.ui.widget.js',
            'summernote/jquery.iframe-transport.js',
            'summernote/jquery.fileupload.js',
            'summernote/summernote-lite.min.js',
            'summernote/ResizeSensor.js',
        ),
    },
}


def using_config(_func=None):
    """
    This allows a function to use Summernote configuration
    as a global variable, temporarily.
    """

    def decorator(func):
        @wraps(func)
        def inner_dec(*args, **kwargs):
            g = func.__globals__
            var_name = 'config'
            sentinel = object()

            oldvalue = g.get(var_name, sentinel)
            g[var_name] = apps.get_app_config('django_summernote').config

            try:
                res = func(*args, **kwargs)
            finally:
                if oldvalue is sentinel:
                    del g[var_name]
                else:
                    g[var_name] = oldvalue

            return res

        return inner_dec

    if _func is None:
        return decorator
    else:
        return decorator(_func)


def uploaded_filepath(instance, filename):
    """
    Returns default filepath for uploaded files.
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    today = datetime.now().strftime('%Y-%m-%d')
    return os.path.join('django-summernote', today, filename)


def get_theme_files(theme, part):
    """
    Return selected theme files
    """
    return SUMMERNOTE_THEME_FILES[theme][part]


def example_test_func(request):
    return True


@using_config
def get_proper_language():
    """
    Return the proper language by get_language()
    """
    lang = config['summernote'].get('lang')

    if not lang:
        return config['lang_matches'].get(get_language(), 'en-US')

    return lang


@using_config
def get_attachment_model():
    """
    Returns the Attachment model that is active in this project.
    """

    try:
        from .models import AbstractAttachment
        klass = apps.get_model(config["attachment_model"])
        if not issubclass(klass, AbstractAttachment):
            raise ImproperlyConfigured(
                "SUMMERNOTE_CONFIG['attachment_model'] refers to model '%s' that is not "
                "inherited from 'django_summernote.models.AbstractAttachment'" % config["attachment_model"]
            )
        return klass
    except ValueError:
        raise ImproperlyConfigured("SUMMERNOTE_CONFIG['attachment_model'] must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "SUMMERNOTE_CONFIG['attachment_model'] refers to model '%s' that has not been installed" % config[
                "attachment_model"]
        )


@using_config
def get_attachment_upload_to():
    """
    Return 'attachment_upload_to' from configuration
    """
    return config['attachment_upload_to']


@using_config
def get_attachment_storage():
    # module importer code comes from
    # https://github.com/django-debug-toolbar/django-debug-toolbar/
    config = apps.get_app_config('django_summernote').config

    if config['attachment_storage_class']:
        storage_path = config['attachment_storage_class']
        try:
            dot = storage_path.rindex('.')
        except ValueError:
            raise ImproperlyConfigured("%s is not a valid module" %
                                       storage_path)

        storage_module, storage_classname = \
            storage_path[:dot], storage_path[dot + 1:]

        try:
            mod = import_module(storage_module)
        except ImportError as e:
            raise ImproperlyConfigured(
                'Error importing storage module %s: "%s"' %
                (storage_module, e))

        try:
            storage_class = getattr(mod, storage_classname)
        except AttributeError:
            raise ImproperlyConfigured(
                'Storage module "%s" does not define a "%s" class' %
                (storage_module, storage_classname))

        return storage_class()
    else:
        return default_storage

@using_config
def has_codemirror_config():
    return 'summernote' in config and \
        'codemirror' in config['summernote']
