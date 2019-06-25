django-summernote
=================
[![Build Status](https://img.shields.io/travis/summernote/django-summernote.svg)](https://travis-ci.org/summernote/django-summernote)
[![Coverage Status](https://coveralls.io/repos/github/summernote/django-summernote/badge.svg?branch=master)](https://coveralls.io/github/summernote/django-summernote?branch=master)

[Summernote](https://github.com/summernote/summernote) is a simple WYSIWYG editor.

`django-summernote` allows you to embed Summernote into Django very handy. Support admin mixins and widgets.

![django-summernote](https://raw.github.com/lqez/pastebin/master/img/django-summernote.png "Screenshot of django-summernote")


SETUP
-----

1. Install `django-summernote` to your python environment.

        pip install django-summernote

2. Add `django_summernote` to `INSTALLED_APP` in `settings.py`.

        INSTALLED_APPS += ('django_summernote', )

3. Add `django_summernote.urls` to `urls.py`.
     - For Django 1.x

           urlpatterns = [
               ...
               url(r'^summernote/', include('django_summernote.urls')),
               ...
           ]

     - For Django 2.x

           from django.urls import include
           # ...
           urlpatterns = [
               ...
               path('summernote/', include('django_summernote.urls')),
               ...
           ]

4. Be sure to set proper `MEDIA_URL` for attachments.
     - The following is an example test code:
     
           MEDIA_URL = '/media/'
           MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
    
     - When debug option is enabled(```DEBUG=True```), DO NOT forget to add urlpatterns as shown below:
     
            from django.conf import settings
            from django.conf.urls.static import static
            
            if settings.DEBUG:
                urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
            
     - Please, read the official document more in detail: <https://docs.djangoproject.com/en/1.11/topics/files/>

5. Run database migration for preparing attachment model.

        python manage.py migrate

USAGE
-----
## Django models
In `models.py`,

```python
    from django.db import models

    from django_summernote.fields import SummernoteTextField

    class Post(models.Model):
        content = SummernoteTextField()
```

`SummernoteTextField` inherits all of the properties of a regular `TextField`. Using this method, the `SummernoteWidget` will automatically be used in the django admin.


## Django admin site
### Apply summernote to all TextField in model
In `admin.py`,

```python
    from django_summernote.admin import SummernoteModelAdmin
    from .models import SomeModel

    # Apply summernote to all TextField in model.
    class SomeModelAdmin(SummernoteModelAdmin):  # instead of ModelAdmin
        summernote_fields = '__all__'

    admin.site.register(SomeModel, SomeModelAdmin)
```

### Apply summernote to not all TextField in model
Although `Post` model has several TextField, only `content` field will have `SummernoteWidget`.

In `admin.py`,

```python
from django_summernote.admin import SummernoteModelAdmin
from .models import Post

class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)

admin.site.register(Post, PostAdmin)
```

## Form
In `forms`,

```python
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget

# Apply summernote to specific fields.
class SomeForm(forms.Form):
    foo = forms.CharField(widget=SummernoteWidget())  # instead of forms.Textarea

# If you don't like <iframe>, then use inplace widget
# Or if you're using django-crispy-forms, please use this.
class AnotherForm(forms.Form):
    bar = forms.CharField(widget=SummernoteInplaceWidget())
```

And for `ModelForm`,

```python
class FormFromSomeModel(forms.ModelForm):
    class Meta:
        model = SomeModel
        widgets = {
            'foo': SummernoteWidget(),
            'bar': SummernoteInplaceWidget(),
        }
```

Last, please don't forget to use `safe` templatetag while displaying in templates.

    {{ foobar|safe }}


THEMES
------

django-summernote is served with Bootstrap3 by default, but you can choose another options.
You can change the theme by `SUMMERNOTE_THEME = '<theme_name>'` in `settings.py`.

 - Bootstrap3 (`bs3`)
 - Bootstrap4 (`bs4`)
 - Lite UI (Summernote standalone) (`lite`)

In settings.py

```python
SUMMERNOTE_THEME = 'bs4'  # Show summernote with Bootstrap4
```

OPTIONS
-------

Support customization via settings.
Put `SUMMERNOTE_CONFIG` into your settings file.

In settings.py,

```python
SUMMERNOTE_CONFIG = {
    # Using SummernoteWidget - iframe mode, default
    'iframe': True,

    # Or, you can set it as False to use SummernoteInplaceWidget by default - no iframe mode
    # In this case, you have to load Bootstrap/jQuery stuff by manually.
    # Use this when you're already using Bootstraip/jQuery based themes.
    'iframe': False,

    # You can put custom Summernote settings
    'summernote': {
        # As an example, using Summernote Air-mode
        'airMode': False,

        # Change editor size
        'width': '100%',
        'height': '480',

        # Use proper language setting automatically (default)
        'lang': None,

        # Or, set editor language/locale forcely
        'lang': 'ko-KR',
        ...

        # You can also add custom settings for external plugins
        'print': {
            'stylesheetUrl': '/some_static_folder/printable.css',
        },
    },

    # Need authentication while uploading attachments.
    'attachment_require_authentication': True,

    # Set `upload_to` function for attachments.
    'attachment_upload_to': my_custom_upload_to_func(),

    # Set custom storage class for attachments.
    'attachment_storage_class': 'my.custom.storage.class.name',

    # Set custom model for attachments (default: 'django_summernote.Attachment')
    'attachment_model': 'my.custom.attachment.model', # must inherit 'django_summernote.AbstractAttachment'

    # You can disable attachment feature.
    'disable_attachment': False,
    
    # Set `True` to return attachment paths in absolute URIs.
    'attachment_absolute_uri': False,

    # You can add custom css/js for SummernoteWidget.
    'css': (
    ),
    'js': (
    ),

    # You can also add custom css/js for SummernoteInplaceWidget.
    # !!! Be sure to put {{ form.media }} in template before initiate summernote.
    'css_for_inplace': (
    ),
    'js_for_inplace': (
    ),

    # Codemirror as codeview
    # If any codemirror settings are defined, it will include codemirror files automatically.
    'css': (
        '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.29.0/theme/monokai.min.css',
    ),
    'codemirror': {
        'mode': 'htmlmixed',
        'lineNumbers': 'true',

        # You have to include theme file in 'css' or 'css_for_inplace' before using it.
        'theme': 'monokai',
    },

    # Lazy initialize
    # If you want to initialize summernote at the bottom of page, set this as True
    # and call `initSummernote()` on your page.
    'lazy': True,

    # To use external plugins,
    # Include them within `css` and `js`.
    'js': {
        '/some_static_folder/summernote-ext-print.js',
        '//somewhere_in_internet/summernote-plugin-name.js',
    },
}
```

  - There are pre-defined css/js files for widgets.
    - See them at [summernote default settings](https://github.com/summernote/django-summernote/blob/master/django_summernote/settings.py#L106-L133)
  - About language/locale: [Summernote i18n section](http://summernote.org/getting-started/#i18n-support)
  - About Air-mode, see [Summernote air-mode example page](http://summernote.org/examples/#air-mode).
  - About toolbar customization, please refer [Summernote toolbar section](http://summernote.org/deep-dive/#custom-toolbar-popover).

Or, you can styling editor via attributes of the widget. These adhoc styling will override settings from `SUMMERNOTE_CONFIG`.

```python
# Apply adhoc style via attributes
class SomeForm(forms.Form):
    foo = forms.CharField(widget=SummernoteWidget(attrs={'summernote': {'width': '50%', 'height': '400px'}}))
```

You can also pass additional parameters to custom `Attachment` model by adding attributes to SummernoteWidget or SummernoteInplaceWidget, any attribute starting with `data-` will be pass to the `save(...)` method of custom `Attachment` model as `**kwargs`.

```python
# Pass additional parameters to Attachment via attributes
class SomeForm(forms.Form):
    foo = forms.CharField(widget=SummernoteWidget(attrs={'data-user-id': 123456, 'data-device': 'iphone'}))
```

LIMITATIONS
-----------

`django-summernote` does currently not support upload of non-image files.

LICENSE
-------

`django-summernote` is distributed under MIT license and proudly served by great contributors.

