import django
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django_summernote.settings import summernote_config, get_attachment_model
if django.VERSION <= (1, 9):
    from django.views.generic import View
else:
    from django.views import View


class SummernoteEditor(TemplateView):
    template_name = 'django_summernote/widget_iframe_editor.html'

    def __init__(self):
        super(SummernoteEditor, self).__init__()

        static_default_css = tuple(static(x) for x in summernote_config['default_css'])
        static_default_js = tuple(static(x) for x in summernote_config['default_js'])

        self.css = \
            summernote_config['base_css'] \
            + (summernote_config['codemirror_css'] if 'codemirror' in summernote_config else ()) \
            + static_default_css \
            + summernote_config['css']

        self.js = \
            summernote_config['base_js'] \
            + (summernote_config['codemirror_js'] if 'codemirror' in summernote_config else ()) \
            + static_default_js \
            + summernote_config['js']

    def get_context_data(self, **kwargs):
        context = super(SummernoteEditor, self).get_context_data(**kwargs)

        context['id_src'] = self.kwargs['id']
        context['id'] = self.kwargs['id'].replace('-', '_')
        context['css'] = self.css
        context['js'] = self.js
        context['config'] = summernote_config

        return context


class SummernoteUploadAttachment(View):
    def __init__(self):
        super(SummernoteUploadAttachment, self).__init__()

    def get(self, request, *args, **kwargs):
        return JsonResponse({
            'status': 'false',
            'message': _('Only POST method is allowed'),
        }, status=400)

    def post(self, request, *args, **kwargs):
        authenticated = \
            request.user.is_authenticated if django.VERSION >= (1, 10) \
            else request.user.is_authenticated()

        if summernote_config['attachment_require_authentication'] and \
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
        kwargs.pop("csrfmiddlewaretoken", None)

        try:
            attachments = []

            for file in request.FILES.getlist('files'):

                # create instance of appropriate attachment class
                klass = get_attachment_model()
                attachment = klass()

                attachment.file = file
                attachment.name = file.name

                if file.size > summernote_config['attachment_filesize_limit']:
                    return JsonResponse({
                        'status': 'false',
                        'message': _('File size exceeds the limit allowed and cannot be saved'),
                    }, status=400)

                # calling save method with attachment parameters as kwargs
                attachment.save(**kwargs)
                attachments.append(attachment)

            return HttpResponse(render_to_string('django_summernote/upload_attachment.json', {
                'attachments': attachments,
            }), content_type='application/json')
        except IOError:
            return JsonResponse({
                'status': 'false',
                'message': _('Failed to save attachment'),
            }, status=500)
