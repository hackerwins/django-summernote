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

        urlpatterns = [
            ...
            url(r'^summernote/', include('django_summernote.urls')),
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
## Django admin site
### Apply summernote to all TextField in model
In `admin.py`,

    from django_summernote.admin import SummernoteModelAdmin
    from .models import SomeModel

    # Apply summernote to all TextField in model.
    class SomeModelAdmin(SummernoteModelAdmin):  # instead of ModelAdmin
        summernote_fields = '__all__'

    admin.site.register(SomeModel, SomeModelAdmin)

### Apply summernote to not all TextField in model
Although `Post` model has several TextField, only `content` field will have `SummernoteWidget`.

In `admin.py`,

    from django_summernote.admin import SummernoteModelAdmin
    from .models import Post
    
    class PostAdmin(SummernoteModelAdmin):
        summernote_fields = ('content',)
    
    admin.site.register(Post, PostAdmin)

## Form
In `forms`,

    from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget

    # Apply summernote to specific fields.
    class SomeForm(forms.Form):
        foo = forms.CharField(widget=SummernoteWidget())  # instead of forms.Textarea

    # If you don't like <iframe>, then use inplace widget
    # Or if you're using django-crispy-forms, please use this.
    class AnotherForm(forms.Form):
        bar = forms.CharField(widget=SummernoteInplaceWidget())

And for `ModelForm`,

    class FormFromSomeModel(forms.ModelForm):
        class Meta:
            model = SomeModel
            widgets = {
                'foo': SummernoteWidget(),
                'bar': SummernoteInplaceWidget(),
            }

Last, please don't forget to use `safe` templatetag while displaying in templates.

    {{ foobar|safe }}


OPTIONS
-------

Support customization via settings.
Put `SUMMERNOTE_CONFIG` into your settings file.

In settings.py,

    SUMMERNOTE_CONFIG = {
        # Using SummernoteWidget - iframe mode
        'iframe': True,  # or set False to use SummernoteInplaceWidget - no iframe mode

        # Using Summernote Air-mode
        'airMode': False,

        # Use native HTML tags (`<b>`, `<i>`, ...) instead of style attributes
        'styleWithSpan': False,

        # Set text direction : 'left to right' is default.
        'direction': 'ltr',

        # Change editor size
        'width': '100%',
        'height': '480',

        # Use proper language setting automatically (default)
        'lang': None,

        # Or, set editor language/locale forcely
        'lang': 'ko-KR',

        # Customize toolbar buttons
        'toolbar': [
            ['style', ['style']],
            ['style', ['bold', 'italic', 'underline', 'clear']],
            ['para', ['ul', 'ol', 'height']],
            ['insert', ['link']],
        ],

        # Need authentication while uploading attachments.
        'attachment_require_authentication': True,

        # Set `upload_to` function for attachments.
        'attachment_upload_to': my_custom_upload_to_func(),

        # Set custom storage class for attachments.
        'attachment_storage_class': 'my.custom.storage.class.name',

        # Set custom model for attachments (default: 'django_summernote.Attachment')
        'attachment_model': 'my.custom.attachment.model', # must inherit 'django_summernote.AbstractAttachment'

        # Set common css/js media files
        'base_css': (
            '//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css',
        ),
        'base_js': (
            '//code.jquery.com/jquery-1.9.1.min.js',
            '//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js',
        ),
        'default_css': (
            os.path.join(STATIC_URL, 'django_summernote/summernote.css'),
            os.path.join(STATIC_URL, 'django_summernote/django_summernote.css'),
        ),
        'default_js': (
            os.path.join(STATIC_URL, 'django_summernote/jquery.ui.widget.js'),
            os.path.join(STATIC_URL, 'django_summernote/jquery.iframe-transport.js'),
            os.path.join(STATIC_URL, 'django_summernote/jquery.fileupload.js'),
            os.path.join(STATIC_URL, 'django_summernote/summernote.min.js'),
        ),

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

        # You can disable file upload feature.
        'disable_upload': False,

        # Codemirror as codeview
        # If any codemirror settings are defined, it will include codemirror files automatically.
        'css': {
            '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.29.0/theme/monokai.min.css',
        },
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
        # You can also add custom Summernote JS settings in `summernote` section.
        'summernote': {
            'disableDragAndDrop': False,
            'print': {
                'stylesheetUrl': '/some_static_folder/printable.css',
            },
        }
    }

  - There are pre-defined css/js files for widgets.
    - See them at [summernote default settings](https://github.com/summernote/django-summernote/blob/master/django_summernote/settings.py#L106-L133)
  - About language/locale: [Summernote i18n section](http://summernote.org/getting-started/#i18n-support)
  - About Air-mode, see [Summernote air-mode example page](http://summernote.org/examples/#air-mode).
  - About toolbar customization, please refer [Summernote toolbar section](http://summernote.org/deep-dive/#custom-toolbar-popover).

Or, you can styling editor via attributes of the widget. These adhoc styling will override settings from `SUMMERNOTE_CONFIG`.

    # Apply adhoc style via attributes
    class SomeForm(forms.Form):
        foo = forms.CharField(widget=SummernoteWidget(attrs={'width': '50%', 'height': '400px'}))

You can also pass additional parameters to custom `Attachment` model by adding attributes to SummernoteWidget or SummernoteInplaceWidget, any attribute starting with `data-` will be pass to the `save(...)` method of custom `Attachment` model as `**kwargs`.

    # Pass additional parameters to Attachment via attributes
    class SomeForm(forms.Form):
        foo = forms.CharField(widget=SummernoteWidget(attrs={'data-user-id': 123456, 'data-device': 'iphone'}))

You can override Summernote JS custom options from `SUMMERNOTE_CONFIG` for each widget as well:

    # Optionally set/override Summernote JS options for each widget
    class SomeForm(forms.Form):
        foo = forms.CharField(widget=SummernoteWidget(attrs={
            'disable_upload': True,
            'summernote': {
                'disableDragAndDrop': True
            }
        }))


LIMITATIONS
-----------

`django-summernote` does currently not support upload of non-image files.

LICENSE
-------

`django-summernote` is distributed under MIT license and proudly served by great contributors.

