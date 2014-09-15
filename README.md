django-summernote
=================
[![Build Status](https://travis-ci.org/lqez/django-summernote.svg?branch=master)](https://travis-ci.org/lqez/django-summernote)
[![Coverage Status](https://img.shields.io/coveralls/lqez/django-summernote.svg)](https://coveralls.io/r/lqez/django-summernote?branch=master)

[Summernote](https://github.com/HackerWins/summernote) is a simple WYSIWYG editor.

`django-summernote` allows you to embed Summernote into Django very handy. Support admin mixins and widgets.

![django-summernote](https://raw.github.com/lqez/pastebin/master/img/django-summernote.png "Screenshot of django-summernote")



SETUP
-----

1. Install `django-summernote` to your python environment.

        pip install django-summernote

2. Add `django_summernote` to `INSTALLED_APP` in `settings.py`.

        INSTALLED_APPS += ('django_summernote', )

3. Add `django_summernote.urls` to `urls.py`.

        urlpatterns = patterns('',
            ...
            (r'^summernote/', include('django_summernote.urls')),
            ...
        )

4. Run `syncdb` for preparing attachment model.

        python manage.py syncdb


USAGE
-----

In `admin.py`,

    from django_summernote.admin import SummernoteModelAdmin

    # Apply summernote to all TextField in model.
    class SomeModelAdmin(SummernoteModelAdmin):  # instead of ModelAdmin
        ...

Or, in `forms`,

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
        # (Firefox, Chrome only)
        'styleWithTags': True,

        # Set text direction : 'left to right' is default.
        'direction': 'ltr',

        # Change editor size
        'width': '100%',
        'height': '480',

        # Use proper language setting automatically (default)
        'lang': None

        # Or, set editor language/locale forcely
        'lang': 'ko-KR',

        # Customize toolbar buttons
        'toolbar': [
            ['style', ['style']],
            ['style', ['bold', 'italic', 'underline', 'clear']],
            ['para', ['ul', 'ol', 'height']],
            ['insert', ['link']],
        ],

        # Set `upload_to` function for attachments.
        'attachment_upload_to': my_custom_upload_to_func(),

        # Set custom storage class for attachments.
        'attachment_storage_class': 'my.custom.storage.class.name',

        # Set external media files for SummernoteInplaceWidget.
        # !!! Be sure to put {{ form.media }} in template before initiate summernote.
        'inplacewidget_external_css': (
            '//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css',
            '//netdna.bootstrapcdn.com/font-awesome/4.0.3/css/font-awesome.min.css',
        ),
        'inplacewidget_external_js': (
            '//code.jquery.com/jquery-1.9.1.min.js',
            '//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js',
        ),
    }

  - About language/locale: [Summernote i18n section](http://hackerwins.github.io/summernote/features.html#i18n-language)
  - About Air-mode, see [Summernote air-mode example page](http://hackerwins.github.io/summernote/example.html#airmode).
  - About toolbar customization, please refer [Summernote toolbar section](http://hackerwins.github.io/summernote/features.html#customtoolbar).

Or, you can styling editor via attributes of the widget. These adhoc styling will override settings from `SUMMERNOTE_CONFIG`.

    # Apply adhoc style via attibutes
    class SomeForm(forms.Form):
        foo = forms.CharField(widget=SummernoteWidget(attrs={'width': '50%', 'height': '400px'}))

(TODO) Document for addtional settings will be added, soon. :^D


HTML WHITELIST SCRUBBING
------------------------

[Scrubber](https://github.com/samuel/python-scrubber/tree/master) is a
white-listing HTML sanitizer. It uses BeautifulSoup to parse an HTML
document and removes any tags and attributes that are not specifically
allowed.

To enable [Scrubber](https://github.com/samuel/python-scrubber/tree/master),
simply install the library:

    pip install scrubber


AUTHOR
------

Park Hyunwoo([@lqez](https://twitter.com/lqez))


THANKS TO
---------

  - [jaeyoung](https://github.com/jeyraof) : Debugging on Django 1.4
  - [kroisse](https://github.com/kroisse) : Fixing problem on importing module


LICENSE
-------

`django-summernote` is distributed under MIT license.

And also uses below libraries.

  - jQuery File Upload : http://blueimp.github.io/jQuery-File-Upload/
