from django.conf import settings
from django.contrib import admin
from django.forms.widgets import Media
from django_summernote.admin import SummernoteModelAdmin, SummernoteModelAdminMixin
from django_summernote.utils import get_theme_files
from .models import Post, Book, Author

class BookAdmin(admin.ModelAdmin):
    model = Book
    pass


class PostAdmin(SummernoteModelAdmin):
    pass


class BookInline(SummernoteModelAdminMixin, admin.StackedInline):
    model = Book
    extra = 1


class AuthorAdmin(SummernoteModelAdminMixin, admin.ModelAdmin):
    # For non-bootstrapped admin site,
    # JavaScript and CSS files should be imported manually like below.
    @property
    def media(self):
        media = super().media + Media(
            js = get_theme_files(settings.SUMMERNOTE_THEME, 'base_js'),
            css = {
            'all': get_theme_files(settings.SUMMERNOTE_THEME, 'base_css'),
        })
        return media

    model = Author
    inlines = [
        BookInline,
    ]


admin.site.register(Book, BookAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Author, AuthorAdmin)
