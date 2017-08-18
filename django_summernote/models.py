from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage
from django.db import models
from django.utils.translation import ugettext_lazy as _

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

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
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Defaults to filename, if left blank")
    )
    file = models.FileField(
        verbose_name=_('File'),
        upload_to=summernote_config['attachment_upload_to'],
        storage=_get_attachment_storage()
    )
    uploaded = models.DateTimeField(
        verbose_name=_('Uploaded'),
        auto_now_add=True
    )

    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        abstract = True


class Attachment(AbstractAttachment):
    class Meta:
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')
