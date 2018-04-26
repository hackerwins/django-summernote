from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.db import models
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from django_summernote.settings import summernote_config, get_attachment_model


class SummernoteModelAdminMixin(object):
    summernote_fields = '__all__'
    summernote_widget = SummernoteWidget if summernote_config['iframe'] else SummernoteInplaceWidget

    def formfield_for_dbfield(self, db_field, *args, **kwargs):
        if self.summernote_fields == '__all__':
            if isinstance(db_field, models.TextField):
                kwargs['widget'] = self.summernote_widget
        else:
            if db_field.name in self.summernote_fields:
                kwargs['widget'] = self.summernote_widget

        return super(SummernoteModelAdminMixin, self).formfield_for_dbfield(db_field, *args, **kwargs)


class SummernoteInlineModelAdmin(SummernoteModelAdminMixin, InlineModelAdmin):
    pass


class SummernoteModelAdmin(SummernoteModelAdminMixin, admin.ModelAdmin):
    pass


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'file', 'uploaded']
    search_fields = ['name']
    ordering = ('-id',)

    def save_model(self, request, obj, form, change):
        obj.name = obj.file.name if (not obj.name) else obj.name
        super(AttachmentAdmin, self).save_model(request, obj, form, change)


admin.site.register(get_attachment_model(), AttachmentAdmin)
