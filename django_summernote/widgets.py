import json
from django import forms
from django.conf import settings as django_settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.forms.utils import flatatt
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django_summernote.utils import get_proper_language, using_config
try:
    from django.urls import reverse  # Django >= 2.0
except ImportError:
    from django.core.urlresolvers import reverse

__all__ = ['SummernoteWidget', 'SummernoteInplaceWidget']


class SummernoteWidgetBase(forms.Textarea):
    @using_config
    def summernote_settings(self):
        lang = get_proper_language()

        summernote_settings = config.get('summernote', {}).copy()
        summernote_settings.update({
            'lang': lang,
            'url': {
                'language': static('summernote/lang/summernote-' + lang + '.min.js'),
                'upload_attachment': reverse('django_summernote-upload_attachment'),
            },
        })
        return summernote_settings

    @using_config
    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)

        if value in config['empty']:
            return None

        return value

    def use_required_attribute(self, initial):
        # Contenteditable widget cannot use HTML5 validation
        return False

    def render(self, name, value, attrs=None, **kwargs):
        # Original field should be hidden
        attrs_for_textarea = attrs.copy()
        attrs_for_textarea['hidden'] = 'true'
        return super(SummernoteWidgetBase, self).render(
            name, value, attrs=attrs_for_textarea, **kwargs
        )

    def final_attr(self, attrs):
        attrs_for_final = attrs.copy()
        attrs_for_final.update(self.attrs)
        attrs_for_final.pop('id', None)
        return attrs_for_final


class SummernoteWidget(SummernoteWidgetBase):
    def render(self, name, value, attrs=None, **kwargs):
        summernote_settings = self.summernote_settings()
        summernote_settings.update(self.attrs.get('summernote', {}))

        html = super(SummernoteWidget, self).render(
            name, value, attrs=attrs, **kwargs
        )
        context = {
            'id': attrs['id'].replace('-', '_'),
            'id_src': attrs['id'],
            'flat_attrs': flatatt(self.final_attr(attrs)),
            'settings': json.dumps(summernote_settings),
            'src': reverse('django_summernote-editor', kwargs={'id': attrs['id']}),

            # Width and height have to be pulled out to create an iframe with correct size
            'width': summernote_settings['width'],
            'height': summernote_settings['height'],
        }

        html += render_to_string('django_summernote/widget_iframe.html', context)
        return mark_safe(html)


class SummernoteInplaceWidget(SummernoteWidgetBase):
    @using_config
    def _media(self):
        return forms.Media(
            css={
                'all': (
                    (config['codemirror_css'] if 'codemirror' in config else ()) +
                    config['default_css'] +
                    config['css_for_inplace']
                )
            },
            js=(
                (config['codemirror_js'] if 'codemirror' in config else ()) +
                config['default_js'] +
                config['js_for_inplace']
            ))

    media = property(_media)

    @using_config
    def render(self, name, value, attrs=None, **kwargs):
        summernote_settings = self.summernote_settings()
        summernote_settings.update(self.attrs.get('summernote', {}))

        html = super(SummernoteInplaceWidget, self).render(
            name, value, attrs=attrs, **kwargs
        )
        context = {
            'id': attrs['id'].replace('-', '_'),
            'id_src': attrs['id'],
            'attrs': self.final_attr(attrs),
            'config': config,
            'settings': json.dumps(summernote_settings),
            'CSRF_COOKIE_NAME': django_settings.CSRF_COOKIE_NAME,
        }

        html += render_to_string('django_summernote/widget_inplace.html', context)
        return mark_safe(html)
