import logging
from django.contrib.auth.mixins import UserPassesTestMixin
from django.templatetags.static import static
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.views.generic import TemplateView, View
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_sameorigin

from django_summernote.forms import UploadForm
from django_summernote.utils import get_attachment_model, get_config, \
    has_codemirror_config

logger = logging.getLogger(__name__)


class SummernoteEditor(TemplateView):
    template_name = 'django_summernote/widget_iframe_editor.html'

    def __init__(self):
        super().__init__()
        config = get_config()

        static_default_css = tuple(static(x) for x in config['default_css'])
        static_default_js = tuple(static(x) for x in config['default_js'])
        self.css = \
            config['base_css'] \
            + (config['codemirror_css'] if has_codemirror_config() else ()) \
            + static_default_css \
            + config['css']

        self.js = \
            config['base_js'] \
            + (config['codemirror_js'] if has_codemirror_config() else ()) \
            + static_default_js \
            + config['js']

        self.config = config

    @method_decorator(xframe_options_sameorigin)
    def dispatch(self, *args, **kwargs):
        return super(SummernoteEditor, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['id'] = self.kwargs['id']
        context['id_safe'] = self.kwargs['id'].replace('-', '_')
        context['css'] = self.css
        context['js'] = self.js
        context['config'] = get_config()

        return context


class SummernoteUploadAttachment(UserPassesTestMixin, View):
    def test_func(self):
        return get_config()['test_func_upload_view'](self.request)

    def __init__(self):
        super().__init__()
        self.config = get_config()

    @method_decorator(xframe_options_sameorigin)
    def dispatch(self, *args, **kwargs):
        return super(SummernoteUploadAttachment, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return JsonResponse({
            'status': 'false',
            'message': _('Only POST method is allowed'),
        }, status=400)

    def post(self, request, *args, **kwargs):
        authenticated = request.user.is_authenticated
        if get_config()['attachment_authentication_func']:
            authenticated = get_config()['attachment_authentication_func'](self.request)

        if self.config['disable_attachment']:
            logger.error(
                'User<%s:%s> tried to use disabled attachment module.',
                getattr(request.user, 'pk', None),
                request.user
            )
            return JsonResponse({
                'status': 'false',
                'message': _('Attachment module is disabled'),
            }, status=403)

        if self.config['attachment_require_authentication'] and \
                not authenticated:
            return JsonResponse({
                'status': 'false',
                'message': _('Only authenticated users are allowed'),
            }, status=403)

        if not request.FILES.getlist('files'):
            return JsonResponse({
                'status': 'false',
                'message': _('No files were requested'),
            }, status=400)

        # remove unnecessary CSRF token, if found
        kwargs = request.POST.copy()
        kwargs.pop('csrfmiddlewaretoken', None)

        for file in request.FILES.getlist('files'):
            form = UploadForm(
                files={
                    'file': file,
                }
            )
            if not form.is_valid():
                logger.error(
                    'User<%s:%s> tried to upload non-image file.',
                    getattr(request.user, 'pk', None),
                    request.user
                )

                return JsonResponse(
                    {
                        'status': 'false',
                        'message': ''.join(form.errors['file']),
                    },
                    status=400
                )

        try:
            attachments = []

            for file in request.FILES.getlist('files'):

                # create instance of appropriate attachment class
                klass = get_attachment_model()
                attachment = klass()
                attachment.file = file

                if file.size > self.config['attachment_filesize_limit']:
                    return JsonResponse({
                        'status': 'false',
                        'message': _('File size exceeds the limit allowed and cannot be saved'),
                    }, status=400)

                # calling save method with attachment parameters as kwargs
                attachment.save(**kwargs)

                # choose relative/absolute url by config
                attachment.url = attachment.file.url

                if self.config['attachment_absolute_uri']:
                    attachment.url = request.build_absolute_uri(attachment.url)

                attachments.append(attachment)

            return HttpResponse(render_to_string('django_summernote/upload_attachment.json', {
                'attachments': attachments,
            }), content_type='application/json')
        except IOError:
            return JsonResponse({
                'status': 'false',
                'message': _('Failed to save attachment'),
            }, status=500)
