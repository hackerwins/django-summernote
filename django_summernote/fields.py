from django.db import models
from django.forms import fields

import bleach
from django_summernote.settings import ALLOWED_TAGS, ATTRIBUTES, STYLES
from django_summernote.widgets import SummernoteWidget

# code based on https://github.com/shaunsephton/django-ckeditor


class SummernoteTextFormField(fields.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.update({'widget': SummernoteWidget()})
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        value = super().to_python(value)
        return bleach.clean(
            value, tags=ALLOWED_TAGS, attributes=ATTRIBUTES, styles=STYLES)


class SummernoteTextField(models.TextField):
    def formfield(self, **kwargs):
        kwargs.update({'form_class': SummernoteTextFormField})
        return super().formfield(**kwargs)

    def to_python(self, value):
        value = super().to_python(value)
        return bleach.clean(
            value, tags=ALLOWED_TAGS, attributes=ATTRIBUTES, styles=STYLES)
