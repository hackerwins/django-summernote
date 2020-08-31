import json
import os
import sys
from unittest.mock import patch

from django.apps import apps
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.db import models
from django.test import Client, TestCase, override_settings

from django_summernote.utils import (get_attachment_model,
                                     get_attachment_storage)

try:
    # Django >= 2.0
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


if sys.version_info >= (3, 4):
    from importlib import reload
else:
    from imp import reload


IMAGE_FILE = 'django_summernote/static/summernote/summernote.png'


class DjangoSummernoteTest(TestCase):
    def setUp(self):
        self.username = 'lqez'
        self.password = 'ohmygoddess'
        self.site = AdminSite()

        self.app_config = apps.get_app_config('django_summernote')
        self.app_config.update_config()
        self.summernote_config = self.app_config.config

    def test_base(self):
        self.assertTrue(True)

    def test_url(self):
        url = reverse('django_summernote-editor', kwargs={'id': 'foobar'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'summernote.min.js')
        self.assertContains(response, 'summernote.css')

    def test_widget(self):
        from django_summernote.widgets import SummernoteWidget

        widget = SummernoteWidget()
        html = widget.render(
            'foobar', 'lorem ipsum', attrs={'id': 'id_foobar'}
        )
        url = reverse('django_summernote-editor', kwargs={'id': 'id_foobar'})

        assert url in html
        assert 'id="id_foobar"' in html

    def test_widget_inplace(self):
        from django_summernote.widgets import SummernoteInplaceWidget

        widget = SummernoteInplaceWidget()
        html = widget.render(
            'foobar', 'lorem ipsum', attrs={'id': 'id_foobar'}
        )

        assert 'summernote' in html

    def test_form(self):
        from django import forms
        from django_summernote.widgets import SummernoteWidget

        class SimpleForm(forms.Form):
            foobar = forms.CharField(widget=SummernoteWidget())

        f = SimpleForm()
        html = f.as_p()
        url = reverse('django_summernote-editor', kwargs={'id': 'id_foobar'})

        assert url in html
        assert 'id="id_foobar"' in html

    def test_formfield(self):
        from django import forms
        from django_summernote.fields import SummernoteTextFormField

        class SimpleForm(forms.Form):
            foobar = SummernoteTextFormField()

        f = SimpleForm()
        html = f.as_p()
        url = reverse('django_summernote-editor', kwargs={'id': 'id_foobar'})

        assert url in html
        assert 'id="id_foobar"' in html

        illegal_tags = '<script></script>'
        form_field = SummernoteTextFormField()
        cleaned_text = form_field.clean(illegal_tags)
        self.assertEqual(cleaned_text, '&lt;script&gt;&lt;/script&gt;')

    def test_field(self):
        from django import forms
        from django_summernote.fields import SummernoteTextField

        class SimpleModel1(models.Model):
            foobar = SummernoteTextField()

        class SimpleForm(forms.ModelForm):
            class Meta:
                model = SimpleModel1
                fields = "__all__"

        f = SimpleForm()
        html = f.as_p()
        url = reverse('django_summernote-editor', kwargs={'id': 'id_foobar'})

        assert url in html
        assert 'id="id_foobar"' in html

        illegal_tags = '<script></script>'
        model_field = SummernoteTextField()
        model_instance = SimpleModel1()
        cleaned_text = model_field.clean(illegal_tags, model_instance)
        self.assertEqual(cleaned_text, '&lt;script&gt;&lt;/script&gt;')

    def test_empty(self):
        from django import forms
        from django_summernote.widgets import SummernoteWidget

        class SimpleForm(forms.Form):
            foobar = forms.CharField(widget=SummernoteWidget())

        should_be_parsed_as_empty = '<p><br></p>'
        should_not_be_parsed_as_empty = '<p>lorem ipsum</p>'

        f = SimpleForm({'foobar': should_be_parsed_as_empty})
        assert not f.is_valid()
        assert not f.cleaned_data.get('foobar')

        f = SimpleForm({'foobar': should_not_be_parsed_as_empty})
        assert f.is_valid()
        assert f.cleaned_data.get('foobar')

    def test_attachment(self):
        url = reverse('django_summernote-upload_attachment')

        with open(IMAGE_FILE, 'rb') as fp:
            response = self.client.post(url, {'files': [fp]})
            self.assertEqual(response.status_code, 200)
            self.assertContains(
                response, '"name": "%s"' % os.path.basename(IMAGE_FILE))
            self.assertContains(response, '"url": ')
            self.assertContains(response, '"size": ')

    def test_attachment_with_custom_storage(self):
        self.summernote_config['attachment_storage_class'] = \
            'django.core.files.storage.DefaultStorage'

        file_field = get_attachment_model()._meta.get_field('file')
        original_storage = file_field.storage
        file_field.storage = get_attachment_storage()

        url = reverse('django_summernote-upload_attachment')

        with open(IMAGE_FILE, 'rb') as fp:
            response = self.client.post(url, {'files': [fp]})
            self.assertEqual(response.status_code, 200)

        file_field.storage = original_storage

    def test_attachment_with_bad_storage(self):
        from django.core.exceptions import ImproperlyConfigured

        # ValueError
        self.summernote_config['attachment_storage_class'] = \
            'wow_no_dot_storage_class_name'
        with self.assertRaises(ImproperlyConfigured):
            from django_summernote import models
            reload(models)

        # ImportError
        self.summernote_config['attachment_storage_class'] = \
            'wow.such.fake.storage'
        with self.assertRaises(ImproperlyConfigured):
            from django_summernote import models
            reload(models)

        # AttributeError
        self.summernote_config['attachment_storage_class'] = \
            'django.core.files.storage.DogeStorage'

        with self.assertRaises(ImproperlyConfigured):
            from django_summernote import models
            reload(models)

        # IOError with patching storage class
        from dummyplug.storage import IOErrorStorage
        file_field = get_attachment_model()._meta.get_field('file')
        original_storage = file_field.storage
        file_field.storage = IOErrorStorage()

        url = reverse('django_summernote-upload_attachment')

        with open(IMAGE_FILE, 'rb') as fp:
            response = self.client.post(url, {'files': [fp]})
            self.assertNotEqual(response.status_code, 200)

        file_field.storage = original_storage

    def test_get_attachment_model(self):
        from django.core.exceptions import ImproperlyConfigured

        # ValueError
        self.summernote_config['attachment_model'] = \
            'wow_no_dot_model_designation'
        with self.assertRaises(ImproperlyConfigured):
            get_attachment_model()

        # LookupError
        self.summernote_config['attachment_model'] = \
            'wow.not.installed.app.model'
        with self.assertRaises(ImproperlyConfigured):
            get_attachment_model()

        # Ensures proper inheritance, using built-in User class to test
        self.summernote_config['attachment_model'] = \
            'auth.User'
        with self.assertRaises(ImproperlyConfigured):
            get_attachment_model()

    def test_attachment_bad_request(self):
        url = reverse('django_summernote-upload_attachment')
        response = self.client.get(url)

        self.assertNotEqual(response.status_code, 200)

    def test_attachment_no_attachment(self):
        url = reverse('django_summernote-upload_attachment')
        response = self.client.post(url)

        self.assertNotEqual(response.status_code, 200)

    def test_attachment_filesize_exceed(self):
        url = reverse('django_summernote-upload_attachment')
        size = os.path.getsize(IMAGE_FILE)
        old_limit = self.summernote_config['attachment_filesize_limit']
        self.summernote_config['attachment_filesize_limit'] = size - 1

        with open(IMAGE_FILE, 'rb') as fp:
            response = self.client.post(url, {'files': [fp]})
            self.assertNotEqual(response.status_code, 200)
            self.assertEqual(response.json()['message'], 'File size exceeds the limit allowed and cannot be saved')

        self.summernote_config['attachment_filesize_limit'] = old_limit

    def test_attachment_require_authentication(self):
        url = reverse('django_summernote-upload_attachment')
        self.summernote_config['attachment_require_authentication'] = True

        self.user = User.objects.create_user(
            username=self.username, password=self.password)

        with open(IMAGE_FILE, 'rb') as fp:
            response = self.client.post(url, {'files': [fp]})
            self.assertEqual(response.status_code, 403)

        c = Client()
        c.login(username=self.username, password=self.password)

        with open(IMAGE_FILE, 'rb') as fp:
            response = c.post(url, {'files': [fp]})
            self.assertEqual(response.status_code, 200)

        self.summernote_config['attachment_require_authentication'] = False

    @patch('django_summernote.views.logger')
    def test_attachment_disable_attachment(self, mock_logging):
        url = reverse('django_summernote-upload_attachment')
        self.summernote_config['disable_attachment'] = True

        with open(IMAGE_FILE, 'rb') as fp:
            response = self.client.post(url, {'files': [fp]})
            self.assertEqual(response.status_code, 403)
            self.assertDictEqual(response.json(), {"status": "false", "message": "Attachment module is disabled"})
            self.assertTrue(mock_logging.error.called)

        self.summernote_config['disable_attachment'] = False

    @patch('django_summernote.views.logger')
    def test_wrong_attachment(self, mock_logging):
        url = reverse('django_summernote-upload_attachment')

        try:
            from PIL import Image
            with open(IMAGE_FILE, 'rb') as fp:
                response = self.client.post(url, {'files': [fp]})
                self.assertEqual(response.status_code, 200)

            with open(__file__, 'rb') as fp:
                response = self.client.post(url, {'files': [fp]})
                self.assertEqual(response.status_code, 400)
                self.assertDictEqual(
                    response.json(),
                    {
                        "status": "false",
                        "message": "Upload a valid image. The file you uploaded was either not an image or a corrupted image."
                    }
                )
                self.assertTrue(mock_logging.error.called)
        except ImportError:
            # Without PIL, we cannot check the uploaded attachement has image format or not
            with open(IMAGE_FILE, 'rb') as fp:
                response = self.client.post(url, {'files': [fp]})
                self.assertEqual(response.status_code, 200)

    def test_attachment_not_require_authentication(self):
        url = reverse('django_summernote-upload_attachment')
        self.summernote_config['attachment_require_authentication'] = False

        self.user = User.objects.create_user(
            username=self.username, password=self.password)

        with open(IMAGE_FILE, 'rb') as fp:
            response = self.client.post(url, {'files': [fp]})
            self.assertEqual(response.status_code, 200)

    @override_settings(USE_THOUSAND_SEPARATOR=True)
    def test_attachment_with_thousand_separator_option(self):
        url = reverse('django_summernote-upload_attachment')
        size = os.path.getsize(IMAGE_FILE)

        with open(IMAGE_FILE, 'rb') as fp:
            response = self.client.post(url, {'files': [fp]})
            self.assertEqual(response.status_code, 200)
            res = json.loads(response.content.decode('utf-8'))
            self.assertEqual(res['files'][0]['size'], size)

    def test_lang_specified(self):
        old_lang = self.summernote_config['summernote']['lang']
        self.summernote_config['summernote']['lang'] = 'ko-KR'

        from django_summernote import widgets
        widget = widgets.SummernoteInplaceWidget()
        html = widget.render(
            'foobar', 'lorem ipsum', attrs={'id': 'id_foobar'}
        )
        self.summernote_config['summernote']['lang'] = old_lang

        assert '"lang": "ko-KR"' in html

    def test_lang_accept_language(self):
        from django.utils.translation import activate
        activate('fr')

        from django_summernote import widgets
        widget = widgets.SummernoteInplaceWidget()
        html = widget.render(
            'foobar', 'lorem ipsum', attrs={'id': 'id_foobar'}
        )

        assert '"lang": "fr-FR"' in html

    def test_admin_model(self):
        from django_summernote.admin import SummernoteModelAdmin
        from django_summernote.admin import SummernoteInlineModelAdmin
        from django_summernote.widgets import SummernoteWidget

        class SimpleModel(models.Model):
            foobar = models.TextField()

        class SimpleModelAdmin(SummernoteModelAdmin):
            pass

        ma = SimpleModelAdmin(SimpleModel, self.site)

        assert isinstance(
            ma.get_form(None).base_fields['foobar'].widget,
            SummernoteWidget
        )

        class SimpleParentModel(models.Model):
            foobar = models.TextField()

        class SimpleModel2(models.Model):
            foobar = models.TextField()
            parent = models.ForeignKey(SimpleParentModel, on_delete=models.CASCADE)

        class SimpleModelInline(SummernoteInlineModelAdmin):
            model = SimpleModel2

        class SimpleParentModelAdmin(SummernoteModelAdmin):
            inlines = [SimpleModelInline]

        ma = SimpleParentModelAdmin(SimpleParentModel, self.site)

        assert isinstance(
            ma.get_form(None).base_fields['foobar'].widget,
            SummernoteWidget
        )

    def test_admin_model_inplace(self):
        from django_summernote.admin import SummernoteModelAdmin
        from django_summernote.widgets import SummernoteInplaceWidget

        class SimpleModel3(models.Model):
            foobar = models.TextField()

        self.summernote_config['iframe'] = False

        class SimpleModelAdmin(SummernoteModelAdmin):
            pass

        ma = SimpleModelAdmin(SimpleModel3, self.site)

        assert isinstance(
            ma.get_form(None).base_fields['foobar'].widget,
            SummernoteInplaceWidget
        )

        self.summernote_config['iframe'] = True

    def test_admin_summernote_fields(self):
        from django_summernote.admin import SummernoteModelAdmin
        from django_summernote.widgets import SummernoteWidget

        class SimpleModel4(models.Model):
            foo = models.TextField()
            bar = models.TextField()

        class SimpleModelAdmin(SummernoteModelAdmin):
            summernote_fields = ('foo',)

        ma = SimpleModelAdmin(SimpleModel4, self.site)

        assert isinstance(
            ma.get_form(None).base_fields['foo'].widget,
            SummernoteWidget
        )
        assert not isinstance(
            ma.get_form(None).base_fields['bar'].widget,
            SummernoteWidget
        )

    def test_attachment_admin_default_name(self):
        from django_summernote.admin import AttachmentAdmin
        from django_summernote.models import Attachment
        from django.core.files import File
        import os

        aa = AttachmentAdmin(Attachment, self.site)
        attachment = Attachment()
        with open(IMAGE_FILE, 'rb') as fp:
            django_file = File(fp)
            django_file.name = os.path.basename(django_file.name)
            attachment.file = django_file
            self.assertFalse(aa.form().is_valid())
            self.assertEqual(attachment.name, None)
            aa.save_model(None, attachment, None, None)
            self.assertEqual(attachment.name, os.path.basename(IMAGE_FILE))

    def test_attachment_as_string(self):
        from django_summernote.models import Attachment
        from django.core.files import File
        import os

        attachment = Attachment()
        with open(IMAGE_FILE, 'rb') as fp:
            djangoFile = File(fp)
            djangoFile.name = os.path.basename(djangoFile.name)
            attachment.file = djangoFile
            attachment.save()

            self.assertEqual(str(attachment), djangoFile.name)

    def test_config_allow_blank_values(self):
        from django_summernote.widgets import SummernoteWidget

        self.summernote_config['summernote']['tableClassName'] = ''

        widget = SummernoteWidget()
        html = widget.render(
            'foobar', 'lorem ipsum', attrs={'id': 'id_foobar'}
        )
        assert '"tableClassName": ""' in html

    def test_widgets_with_attributes(self):
        from django_summernote.widgets import (SummernoteWidget, SummernoteInplaceWidget)

        widget = SummernoteInplaceWidget(attrs={'class': 'special'})
        html = widget.render(
            'foobar', 'lorem ipsum', attrs={'id': 'id_foobar'}
        )

        assert 'class="special"' in html

        widget = SummernoteWidget(attrs={'class': 'special'})
        html = widget.render(
            'foobar', 'lorem ipsum', attrs={'id': 'id_foobar'}
        )

        assert 'class="special"' in html

    def test_widgets_with_adhoc_settings(self):
        from django_summernote.widgets import (SummernoteWidget, SummernoteInplaceWidget)

        widget = SummernoteInplaceWidget(attrs={'summernote': {'toolbar': [['font', ['bold']]]}})
        html = widget.render(
            'foobar', 'lorem ipsum', attrs={'id': 'id_foobar'}
        )

        assert '"toolbar": [["font", ["bold"]]]' in html

        widget = SummernoteWidget(attrs={'summernote': {'toolbar': [['font', ['italic']]]}})
        html = widget.render(
            'foobar', 'lorem ipsum', attrs={'id': 'id_foobar'}
        )

        assert '"toolbar": [["font", ["italic"]]]' in html

    def test_old_style_configs(self):
        from django_summernote.widgets import (SummernoteWidget, SummernoteInplaceWidget)

        OLD_STYLE_CONFIG = {
            'width': '640px',
            'toolbar': [
                ['font', ['bold']],
            ],
        }
        self.app_config._copy_old_configs(OLD_STYLE_CONFIG, self.app_config.get_default_config())

        widget = SummernoteInplaceWidget()
        html = widget.render(
            'foobar', 'lorem ipsum', attrs={'id': 'id_foobar'}
        )

        assert '"width": "640px"' in html
        assert '"height": 480' in html
        assert '"toolbar": [["font", ["bold"]]]' in html

        widget = SummernoteWidget()
        html = widget.render(
            'foobar', 'lorem ipsum', attrs={'id': 'id_foobar'}
        )

        assert '"width": "640px"' in html
        assert '"height": 480' in html
        assert '"toolbar": [["font", ["bold"]]]' in html

    def test_theme_bootstrap3(self):
        from django_summernote.utils import SUMMERNOTE_THEME_FILES

        url = reverse('django_summernote-editor', kwargs={'id': 'id_foobar'})
        response = self.client.get(url)
        html = response.content.decode('utf-8')

        assert SUMMERNOTE_THEME_FILES['bs3']['base_css'][0] in html

    @override_settings(SUMMERNOTE_THEME='bs4')
    def test_theme_bootstrap4(self):
        from django_summernote.utils import SUMMERNOTE_THEME_FILES

        # Force update summernote config to reset theme files
        self.app_config.update_config()

        url = reverse('django_summernote-editor', kwargs={'id': 'id_foobar'})
        response = self.client.get(url)
        html = response.content.decode('utf-8')

        assert SUMMERNOTE_THEME_FILES['bs4']['base_css'][0] in html
