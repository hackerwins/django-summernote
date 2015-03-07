import os
import uuid
from datetime import datetime
from django.conf import settings


def uploaded_filepath(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    today = datetime.now().strftime('%Y-%m-%d')
    return os.path.join('django-summernote', today, filename)


SETTINGS_USER = getattr(settings, 'SUMMERNOTE_CONFIG', {})
SETTINGS_DEFAULT = {
    'iframe': True,
    'airMode': False,
    'styleWithSpan': True,
    'direction': 'ltr',
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
        'ca': 'ca-ES',
        'cs': 'cs-CZ',
        'da': 'da-DK',
        'de': 'de-DE',
        'es': 'es-ES',
        'fa': 'fa-IR',
        'fi': 'fi-FI',
        'fr': 'fr-FR',
        'he': 'he-IL',
        'hu': 'hu-HU',
        'id': 'id-ID',
        'it': 'it-IT',
        'ja': 'ja-JP',
        'ko': 'ko-KR',
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
        'th': 'th-TH',
        'tr': 'tr-TR',
        'uk': 'uk-UA',
        'vi': 'vi-VN',
        'zh': 'zh-CN',
    },

    'colors': [
        ['#000000', '#424242', '#636363', '#9C9C94', '#CEC6CE', '#EFEFEF', '#F7F7F7', '#FFFFFF'],
        ['#FF0000', '#FF9C00', '#FFFF00', '#00FF00', '#00FFFF', '#0000FF', '#9C00FF', '#FF00FF'],
        ['#F7C6CE', '#FFE7CE', '#FFEFC6', '#D6EFD6', '#CEDEE7', '#CEE7F7', '#D6D6E7', '#E7D6DE'],
        ['#E79C9C', '#FFC69C', '#FFE79C', '#B5D6A5', '#A5C6CE', '#9CC6EF', '#B5A5D6', '#D6A5BD'],
        ['#E76363', '#F7AD6B', '#FFD663', '#94BD7B', '#73A5AD', '#6BADDE', '#8C7BC6', '#C67BA5'],
        ['#CE0000', '#E79439', '#EFC631', '#6BA54A', '#4A7B8C', '#3984C6', '#634AA5', '#A54A7B'],
        ['#9C0000', '#B56308', '#BD9400', '#397B21', '#104A5A', '#085294', '#311873', '#731842'],
        ['#630000', '#7B3900', '#846300', '#295218', '#083139', '#003163', '#21104A', '#4A1031']
      ],

    'attachment_upload_to': uploaded_filepath,
    'attachment_storage_class': None,
    'attachment_filesize_limit': 1024 * 1024,
    'attachment_require_authentication': False,

    'inplacewidget_external_css': (
        '//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css',
        '//netdna.bootstrapcdn.com/font-awesome/4.0.3/css/font-awesome.min.css',
    ),
    'inplacewidget_external_js': (
        '//code.jquery.com/jquery-1.9.1.min.js',
        '//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js',
    ),
}

summernote_config = SETTINGS_DEFAULT.copy()
summernote_config.update(SETTINGS_USER)
