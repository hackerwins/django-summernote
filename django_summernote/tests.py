# -*- coding: utf-8 -*-
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
try:
    # Django >= 2.0
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

from django.test import TestCase, Client, override_settings
from django_summernote.settings import summernote_config, get_attachment_model
import json
from imp import reload


class DjangoSummernoteTest(TestCase):
    def setUp(self):
        self.username = 'lqez'
        self.password = 'ohmygoddess'
        self.site = AdminSite()

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

    def test_field(self):
        from django import forms
        from django.db import models
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
        import os
        url = reverse('django_summernote-upload_attachment')

        with open(__file__, 'rb') as fp:
            response = self.client.post(url, {'files': [fp]})
            self.assertEqual(response.status_code, 200)
            self.assertContains(
                response, '"name": "%s"' % os.path.basename(__file__))
            self.assertContains(response, '"url": ')
            self.assertContains(response, '"size": ')

    def test_attachment_with_custom_storage(self):
        summernote_config['attachment_storage_class'] = \
            'django.core.files.storage.DefaultStorage'

        from django_summernote.models import _get_attachment_storage
        file_field = get_attachment_model()._meta.get_field('file')
        original_storage = file_field.storage
        file_field.storage = _get_attachment_storage()

        url = reverse('django_summernote-upload_attachment')

        with open(__file__, 'rb') as fp:
            response = self.client.post(url, {'files': [fp]})
            self.assertEqual(response.status_code, 200)

        file_field.storage = original_storage

    def test_attachment_with_bad_storage(self):
        from django.core.exceptions import ImproperlyConfigured

        # ValueError
        summernote_config['attachment_storage_class'] = \
            'wow_no_dot_storage_class_name'
        with self.assertRaises(ImproperlyConfigured):
            from django_summernote import models
            reload(models)

        # ImportError
        summernote_config['attachment_storage_class'] = \
            'wow.such.fake.storage'
        with self.assertRaises(ImproperlyConfigured):
            from django_summernote import models
            reload(models)

        # AttributeError
        summernote_config['attachment_storage_class'] = \
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

        with open(__file__, 'rb') as fp:
            response = self.client.post(url, {'files': [fp]})
            self.assertNotEqual(response.status_code, 200)

        file_field.storage = original_storage

    def test_get_attachment_model(self):
        from django.core.exceptions import ImproperlyConfigured

        # ValueError
        summernote_config['attachment_model'] = \
            'wow_no_dot_model_designation'
        with self.assertRaises(ImproperlyConfigured):
            get_attachment_model()

        # LookupError
        summernote_config['attachment_model'] = \
            'wow.not.installed.app.model'
        with self.assertRaises(ImproperlyConfigured):
            get_attachment_model()

        # Ensures proper inheritance, using built-in User class to test
        summernote_config['attachment_model'] = \
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
        import os

        url = reverse('django_summernote-upload_attachment')
        size = os.path.getsize(__file__)
        old_limit = summernote_config['attachment_filesize_limit']
        summernote_config['attachment_filesize_limit'] = size - 1

        with open(__file__, 'rb') as fp:
            response = self.client.post(url, {'files': [fp]})
            self.assertNotEqual(response.status_code, 200)

        summernote_config['attachment_filesize_limit'] = old_limit

    def test_attachment_require_authentication(self):
        url = reverse('django_summernote-upload_attachment')
        summernote_config['attachment_require_authentication'] = True

        self.user = User.objects.create_user(
            username=self.username, password=self.password)

        with open(__file__, 'rb') as fp:
            response = self.client.post(url, {'files': [fp]})
            self.assertEqual(response.status_code, 403)

        c = Client()
        c.login(username=self.username, password=self.password)

        with open(__file__, 'rb') as fp:
            response = c.post(url, {'files': [fp]})
            self.assertEqual(response.status_code, 200)

        summernote_config['attachment_require_authentication'] = False

    def test_attachment_not_require_authentication(self):
        url = reverse('django_summernote-upload_attachment')
        summernote_config['attachment_require_authentication'] = False

        self.user = User.objects.create_user(
            username=self.username, password=self.password)

        with open(__file__, 'rb') as fp:
            response = self.client.post(url, {'files': [fp]})
            self.assertEqual(response.status_code, 200)

    @override_settings(USE_THOUSAND_SEPARATOR=True)
    def test_attachment_with_thousand_separator_option(self):
        import os
        url = reverse('django_summernote-upload_attachment')
        size = os.path.getsize(__file__)

        with open(__file__, 'rb') as fp:
            response = self.client.post(url, {'files': [fp]})
            self.assertEqual(response.status_code, 200)
            res = json.loads(response.content.decode('utf-8'))
            self.assertEqual(res['files'][0]['size'], size)

    def test_lang_specified(self):
        old_lang = summernote_config['lang']
        summernote_config['lang'] = 'ko-KR'

        from django_summernote import widgets
        widget = widgets.SummernoteInplaceWidget()
        html = widget.render(
            'foobar', 'lorem ipsum', attrs={'id': 'id_foobar'}
        )
        summernote_config['lang'] = old_lang

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
        from django.db import models
        from django_summernote.admin import SummernoteModelAdmin
        from django_summernote.admin import SummernoteInlineModelAdmin
        from django_summernote.widgets import SummernoteWidget

        class SimpleParentModel(models.Model):
            foobar = models.TextField()

        class SimpleModel2(models.Model):
            foobar = models.TextField()
            parent = models.ForeignKey(SimpleParentModel)

        class SimpleModelInline(SummernoteInlineModelAdmin):
            model = SimpleModel2

        class SimpleParentModelAdmin(SummernoteModelAdmin):
            inlines = [SimpleModelInline]

        ma = SimpleParentModelAdmin(SimpleParentModel, self.site)

        assert isinstance(
            ma.get_form(None).base_fields['foobar'].widget,
            SummernoteWidget
        )

    def test_attachment_admin_default_name(self):
        from django_summernote.admin import AttachmentAdmin
        from django_summernote.models import Attachment
        from django.core.files import File
        import os

        aa = AttachmentAdmin(Attachment, self.site)
        attachment = Attachment()
        with open(__file__, 'rb') as fp:
            djangoFile = File(fp)
            djangoFile.name = os.path.basename(djangoFile.name)
            attachment.file = djangoFile
            self.assertEqual(attachment.name, None)
            aa.save_model(None, attachment, None, None)
            self.assertEqual(attachment.name, os.path.basename(__file__))

    def test_config_allow_blank_values(self):
        from django_summernote.widgets import SummernoteWidget

        summernote_config['tableClassName'] = ''

        widget = SummernoteWidget()
        html = widget.render(
            'foobar', 'lorem ipsum', attrs={'id': 'id_foobar'}
        )
        assert '"tableClassName": ""' in html
