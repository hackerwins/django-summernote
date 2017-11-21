from __future__ import unicode_literals
from django.db import models
from django.core.files.storage import default_storage
from django.core.exceptions import ImproperlyConfigured
from importlib import import_module

from django_summernote.settings import summernote_config


__all__ = ['AbstractAttachment', 'Attachment', ]


def _get_attachment_storage():
    # module importer code comes from
    # https://github.com/django-debug-toolbar/django-debug-toolbar/
    if summernote_config['attachment_storage_class']:
        storage_path = summernote_config['attachment_storage_class']
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


class AbstractAttachment(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True, help_text="Defaults to filename, if left blank")
    file = models.FileField(
        upload_to=summernote_config['attachment_upload_to'],
        storage=_get_attachment_storage()
    )
    uploaded = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        abstract = True


class Attachment(AbstractAttachment):
    pass
