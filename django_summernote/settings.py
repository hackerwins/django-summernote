import os
import uuid
from datetime import datetime

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def uploaded_filepath(instance, filename):
    """
    Returns default filepath for uploaded files.
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    today = datetime.now().strftime('%Y-%m-%d')
    return os.path.join('django-summernote', today, filename)


def get_attachment_model():
    """
    Returns the Attachment model that is active in this project.
    """
    try:
        from .models import AbstractAttachment
        klass = django_apps.get_model(summernote_config["attachment_model"])
        if not issubclass(klass, AbstractAttachment):
            raise ImproperlyConfigured(
                "SUMMERNOTE_CONFIG['attachment_model'] refers to model '%s' that is not "
                "inherited from 'django_summernote.models.AbstractAttachment'" % summernote_config["attachment_model"]
            )
        return klass
    except ValueError:
        raise ImproperlyConfigured("SUMMERNOTE_CONFIG['attachment_model'] must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "SUMMERNOTE_CONFIG['attachment_model'] refers to model '%s' that has not been installed" % summernote_config["attachment_model"]
        )


SETTINGS_USER = getattr(settings, 'SUMMERNOTE_CONFIG', {})
SETTINGS_DEFAULT = {
    'iframe': True,
    'empty': ('<p><br/></p>', '<p><br></p>'),

    'width': 720,
    'height': 480,
    'toolbar': [
        ['style', ['style']],
        ['font', ['bold', 'italic', 'underline', 'superscript', 'subscript',
                  'strikethrough', 'clear']],
        ['fontname', ['fontname']],
        ['fontsize', ['fontsize']],
        ['color', ['color']],
        ['para', ['ul', 'ol', 'paragraph']],
        ['height', ['height']],
        ['table', ['table']],
        ['insert', ['link', 'picture', 'video', 'hr']],
        ['view', ['fullscreen', 'codeview']],
        ['help', ['help']],
    ],
    'lang': None,
    'lang_matches': {
        'ar': 'ar-AR',
        'bg': 'bg-BG',
        'ca': 'ca-ES',
        'cs': 'cs-CZ',
        'da': 'da-DK',
        'de': 'de-DE',
        'el': 'el-GR',
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
        'vi': 'vi-VN',
        'zh': 'zh-CN',
    },

    'attachment_upload_to': uploaded_filepath,
    'attachment_storage_class': None,
    'attachment_filesize_limit': 1024 * 1024,
    'attachment_require_authentication': False,
    'attachment_model': 'django_summernote.Attachment',

    'jquery': '$',

    'base_css': (
        '//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css',
    ),
    'base_js': (
        '//code.jquery.com/jquery-3.2.1.min.js',
        '//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js',
    ),

    'codemirror_css': (
        '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.29.0/codemirror.min.css',
    ),
    'codemirror_js': (
        '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.29.0/codemirror.min.js',
        '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.29.0/mode/xml/xml.min.js',
        '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.29.0/mode/htmlmixed/htmlmixed.min.js',
    ),

    'default_css': (
        'django_summernote/summernote.css',
        'django_summernote/django_summernote.css',
    ),
    'default_js': (
        'django_summernote/jquery.ui.widget.js',
        'django_summernote/jquery.iframe-transport.js',
        'django_summernote/jquery.fileupload.js',
        'django_summernote/summernote.min.js',
        'django_summernote/ResizeSensor.js',
    ),

    'css': (),
    'js': (),

    'css_for_inplace': (),
    'js_for_inplace': (),

    # Disable upload
    'disable_upload': False,

    # For lazy loading (inplace widget only)
    'lazy': False,
}

summernote_config = SETTINGS_DEFAULT.copy()
summernote_config.update(SETTINGS_USER)
