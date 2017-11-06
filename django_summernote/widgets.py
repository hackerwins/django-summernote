import json
from django import forms
try:
    # Django >= 2.0
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
try:
    # Django >= 1.7
    from django.forms.utils import flatatt
except ImportError:
    # Django < 1.7
    from django.forms.util import flatatt
from django_summernote.settings import summernote_config
from django.conf import settings

__all__ = ['SummernoteWidget', 'SummernoteInplaceWidget']

__summernote_options__ = [
    'airMode',
    'codemirror',
    'colors',
    'dialogsFade',
    'dialogsInBody',
    'direction',
    'disableLinkTarget',
    'focus',
    'fontNames',
    'fontNamesIgnoreCheck',
    'fontSizes',
    'lineHeights',
    'popover',
    'placeholder',
    'shortcuts',
    'styleWithSpan',
    'tableClassName',
    'tabSize',
    'toolbar',
    'width',
    'height',
]


def _get_proper_language():
    # Detect language automatically by get_language()
    if not summernote_config['lang']:
        return summernote_config['lang_matches'].get(get_language(), 'en-US')

    return summernote_config['lang']


class SummernoteWidgetBase(forms.Textarea):
    def template_contexts(self):
        lang = _get_proper_language()
        contexts = {
            'lang': lang,
            'url': {
                'language':
                    static('summernote/lang/summernote-' + lang + '.min.js'),
                'upload_attachment':
                    reverse('django_summernote-upload_attachment'),
            },
        }

        for option in __summernote_options__:
            v = self.attrs.get(option, summernote_config.get(option))

            if v is not None:
                # Proxy models are not JSON serializable. Values obtained from the Django core via ugettext_lazy will
                # return a __proxy__ type that is not serializble using the default serializers.
                # This quick hack checks to see if the value is a proxy type and if so forces evaluation
                # so that it can be serialized
                if '.__proxy__' in str(type(v)):
                    v = str(v)
                contexts[option] = v

        # Merge 'summernote' dict as it is.
        contexts.update(summernote_config.get('summernote', {}))
        return contexts

    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)

        if value in summernote_config['empty']:
            return None

        return value


class SummernoteWidget(SummernoteWidgetBase):
    def render(self, name, value, attrs=None):
        attrs_for_textarea = attrs.copy()
        attrs_for_textarea['hidden'] = 'true'
        html = super(SummernoteWidget, self).render(name,
                                                    value,
                                                    attrs_for_textarea)

        final_attrs = self.build_attrs(attrs)
        del final_attrs['id']  # Use original attributes without id.

        contexts = self.template_contexts()

        url = reverse('django_summernote-editor',
                      kwargs={'id': attrs['id']})

        html += render_to_string(
            'django_summernote/widget_iframe.html',
            {
                'id': attrs['id'].replace('-', '_'),
                'id_src': attrs['id'],
                'src': url,
                'attrs': flatatt(final_attrs),
                'jquery': summernote_config['jquery'],
                'width': contexts['width'],
                'height': contexts['height'],
                'settings': json.dumps(contexts),
            }
        )
        return mark_safe(html)


class SummernoteInplaceWidget(SummernoteWidgetBase):
    class Media:
        css = {
            'all': (
                (summernote_config['codemirror_css'] if 'codemirror' in summernote_config else ()) +
                summernote_config['default_css'] +
                summernote_config['css_for_inplace']
            )
        }

        js = (
            (summernote_config['codemirror_js'] if 'codemirror' in summernote_config else ()) +
            summernote_config['default_js'] +
            summernote_config['js_for_inplace']
        )

    def render(self, name, value, attrs=None):
        attrs_for_textarea = attrs.copy()
        attrs_for_textarea['hidden'] = 'true'
        attrs_for_textarea['id'] += '-textarea'
        html = super(SummernoteInplaceWidget, self).render(name,
                                                           value,
                                                           attrs_for_textarea)
        final_attrs = self.build_attrs(attrs)
        del final_attrs['id']  # Use original attributes without id.

        html += render_to_string(
            'django_summernote/widget_inplace.html',
            {
                'id': attrs['id'].replace('-', '_'),
                'id_src': attrs['id'],
                'attrs': flatatt(final_attrs),
                'jquery': summernote_config['jquery'],
                'value': value if value else '',
                'settings': json.dumps(self.template_contexts()),
                'disable_upload': summernote_config['disable_upload'],
                'lazy': summernote_config['lazy'],
                'CSRF_COOKIE_NAME': settings.CSRF_COOKIE_NAME,
            }
        )
        return mark_safe(html)
