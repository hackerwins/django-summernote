import json
import os
from django import forms
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from django.forms.util import flatatt
from django_summernote.settings import summernote_config
from django.conf import settings

__all__ = ['SummernoteWidget', 'SummernoteInplaceWidget']


def _static_url(url):
    return os.path.join(settings.STATIC_URL, url)


def _get_proper_language():
    # Detect language automatically by get_language()
    if not summernote_config['lang']:
        return summernote_config['lang_matches'].get(get_language(), 'en-US')

    return summernote_config['lang']


class SummernoteWidgetBase(forms.Textarea):
    def template_contexts(self):
        return {
            'toolbar': self.attrs.get('toolbar', summernote_config['toolbar']),
            'lang': self.attrs.get('lang',_get_proper_language()),
            'airMode': self.attrs.get('airMode', summernote_config['airMode']),
            'styleWithSpan': self.attrs.get('styleWithSpan', summernote_config['styleWithSpan']),
            'height': self.attrs.get('height', summernote_config['height']),
            'url': {
                'upload_attachment':
                reverse('django_summernote-upload_attachment'),
            },
        }

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

        url = reverse('django_summernote-editor',
                      kwargs={'id': attrs['id']})
        html += render_to_string(
            'django_summernote/widget_iframe.html',
            {
                'id': attrs['id'].replace('-', '_'),
                'id_src': attrs['id'],
                'src': url,
                'attrs': flatatt(final_attrs),
                'width': summernote_config['width'],
                'height': summernote_config['height'],
                'settings': json.dumps(self.template_contexts()),
            }
        )
        return mark_safe(html)


class SummernoteInplaceWidget(SummernoteWidgetBase):
    class Media:
        css = {'all': (summernote_config['inplacewidget_external_css']) + (
            _static_url('django_summernote/summernote.css'),
        )}

        js = (summernote_config['inplacewidget_external_js']) + (
            _static_url('django_summernote/jquery.ui.widget.js'),
            _static_url('django_summernote/jquery.iframe-transport.js'),
            _static_url('django_summernote/jquery.fileupload.js'),
            _static_url('django_summernote/summernote.min.js'),
        )

    def render(self, name, value, attrs=None):
        attrs_for_textarea = attrs.copy()
        attrs_for_textarea['hidden'] = 'true'
        attrs_for_textarea['id'] += '-textarea'
        html = super(SummernoteInplaceWidget, self).render(name,
                                                           value,
                                                           attrs_for_textarea)
        html += render_to_string(
            'django_summernote/widget_inplace.html',
            Context(dict({
                'id': attrs['id'].replace('-', '_'),
                'id_src': attrs['id'],
                'value': value if value else '',
                'settings': json.dumps(self.template_contexts()),
                'STATIC_URL': settings.STATIC_URL,
            }))
        )
        return mark_safe(html)
