from django.apps import AppConfig
from django.conf import settings as django_settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django_summernote.utils import (
    LANG_TO_LOCALE, uploaded_filepath, get_theme_files,
    example_test_func)


class DjangoSummernoteConfig(AppConfig):
    name = 'django_summernote'
    verbose_name = 'Django Summernote'

    theme = 'bs3'
    config = {}

    def __init__(self, app_name, app_module):
        super(DjangoSummernoteConfig, self).__init__(app_name, app_module)
        self.update_config()

    def get_default_config(self):
        return {
            # Using SummernoteWidget(iframe widget) for admin pages by default
            'iframe': True,

            # These strings will be assumed as empty.
            'empty': ('<p><br/></p>', '<p><br></p>'),

            # Language-to-locale conversion table
            'lang_matches': LANG_TO_LOCALE,

            # Attachment settings
            'disable_attachment': False,
            'attachment_upload_to': uploaded_filepath,
            'attachment_storage_class': None,
            'attachment_filesize_limit': 1024 * 1024,
            'attachment_require_authentication': False,
            'attachment_model': 'django_summernote.Attachment',
            'attachment_absolute_uri': False,

            # additional test_func, for example you want to check if user is in specific group:
            # https://docs.djangoproject.com/en/2.2/topics/auth/default/#django.contrib.auth.mixins.UserPassesTestMixin
            'test_func_upload_view': example_test_func,

            # Shortcut name for jQuery
            'jquery': '$',

            # Base media files only for SummernoteWidget
            'base_css': '',
            'base_js': '',

            # Media files for CodeMirror
            'codemirror_css': (
                '/static/codemirror-5.58.3/lib/codemirror.css',
                '/static/codemirror-5.58.3/theme/elegant.css',
            ),
            'codemirror_js': (
                '/static/codemirror-5.58.3/lib/codemirror.js',
                '/static/codemirror-5.58.3/mode/xml/xml.js',
                '/static/codemirror-5.58.3/mode/htmlmixed/htmlmixed.js',
                '/static/codemirror-5.58.3/mode/django/django.js',
            ),

            # Media files for all Summernote widgets
            'default_css': '',
            'default_js': '',

            # Additional media files only for SummernoteWidget
            'css': (),
            'js': (),

            # Additional media files only for SummernoteInplacewidget
            'css_for_inplace': (),
            'js_for_inplace': (),

            # For lazy loading (inplace widget only)
            'lazy': False,

            # Summernote settings
            'summernote': {
                'width': 720,
                'height': 480,
                'lang': None,
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
            }
        }

    def _copy_old_configs(self, user, default):
        """
        NOTE: Will be deprecated from 0.9
        Copying old-style settings for backward-compatibility
        """
        DEPRECATED_SUMMERNOTE_CONFIGS = (
            'width',
            'height',
            'lang',
            'toolbar',
        )
        for key in DEPRECATED_SUMMERNOTE_CONFIGS:
            if user.get(key):
                self.config['summernote'][key] = user.get(key)
            if not self.config['summernote'].get(key):
                self.config['summernote'][key] = default['summernote'].get(key)

    def update_config(self):
        self.theme = getattr(django_settings, 'SUMMERNOTE_THEME', 'bs3')
        DEFAULT_CONFIG = self.get_default_config()

        CONFIG = getattr(django_settings, 'SUMMERNOTE_CONFIG', {})
        for key in ('base_css', 'base_js', 'default_css', 'default_js'):
            CONFIG[key] = get_theme_files(self.theme, key)

        self.config = DEFAULT_CONFIG.copy()
        self.config.update(CONFIG)
        self._copy_old_configs(CONFIG, DEFAULT_CONFIG)

    def ready(self):
        pass
