import json
from django import forms
from django.conf import settings as django_settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.forms.utils import flatatt
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from django_summernote.settings import summernote_config
try:
    from django.urls import reverse  # Django >= 2.0
except ImportError:
    from django.core.urlresolvers import reverse

__all__ = ['SummernoteWidget', 'SummernoteInplaceWidget']


def _get_proper_language():
    # Detect language automatically by get_language()
    lang = summernote_config['summernote'].get('lang')
    if not lang:
        return summernote_config['lang_matches'].get(get_language(), 'en-US')

    return lang


class SummernoteWidgetBase(forms.Textarea):
    def summernote_settings(self):
        lang = _get_proper_language()

        summernote_settings = summernote_config.get('summernote', {}).copy()
        summernote_settings.update({
            'lang': lang,
            'url': {
                'language': static('summernote/lang/summernote-' + lang + '.min.js'),
                'upload_attachment': reverse('django_summernote-upload_attachment'),
            },
        })
        return summernote_settings

    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)

        if value in summernote_config['empty']:
            return None

        return value


class SummernoteWidget(SummernoteWidgetBase):
    def render(self, name, value, attrs=None, renderer=None):
        summernote_settings = self.summernote_settings()
        summernote_settings.update(self.attrs.pop('summernote', {}))

        attrs_for_textarea = attrs.copy()
        attrs_for_textarea['hidden'] = 'true'
        html = super(SummernoteWidget, self).render(name,
                                                    value,
                                                    attrs_for_textarea)

        final_attrs = self.build_attrs(attrs)
        del final_attrs['id']  # Use original attributes without id.

        context = {
            'id': attrs['id'].replace('-', '_'),
            'id_src': attrs['id'],
            'attrs': flatatt(final_attrs),
            'settings': json.dumps(summernote_settings),
            'src': reverse('django_summernote-editor', kwargs={'id': attrs['id']}),

            # Width and height have to be pulled out to create an iframe with correct size
            'width': summernote_settings['width'],
            'height': summernote_settings['height'],
        }

        html += render_to_string('django_summernote/widget_iframe.html', context)
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
        summernote_settings = self.summernote_settings()
        summernote_settings.update(self.attrs.pop('summernote', {}))

        attrs_for_textarea = attrs.copy()
        attrs_for_textarea['hidden'] = 'true'
        attrs_for_textarea['id'] += '-textarea'
        html = super(SummernoteInplaceWidget, self).render(name,
                                                           value,
                                                           attrs_for_textarea)
        final_attrs = self.build_attrs(attrs)
        del final_attrs['id']  # Use original attributes without id.

        context = {
            'id': attrs['id'].replace('-', '_'),
            'id_src': attrs['id'],
            'attrs': flatatt(final_attrs),
            'config': summernote_config,
            'settings': json.dumps(summernote_settings),
            'CSRF_COOKIE_NAME': django_settings.CSRF_COOKIE_NAME,
        }

        html += render_to_string('django_summernote/widget_inplace.html', context)
        return mark_safe(html)
