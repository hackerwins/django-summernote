from django.db import models

from django_summernote.utils import get_attachment_storage, get_attachment_upload_to

__all__ = ['AbstractAttachment', 'Attachment', ]


class AbstractAttachment(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")
    name = models.CharField(max_length=255, null=True, blank=True, help_text="Defaults to filename, if left blank")
    file = models.FileField(
        upload_to=get_attachment_upload_to(),
        storage=get_attachment_storage()
    )
    uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.file.name
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Attachment(AbstractAttachment):
    pass
