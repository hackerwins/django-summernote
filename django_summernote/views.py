from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django_summernote.settings import summernote_config, get_attachment_model


def editor(request, id):
    return render(
        request,
        'django_summernote/widget_iframe_editor.html',
        {
            'id_src': id,
            'id': id.replace('-', '_'),
            'css': (
                summernote_config['base_css'] +
                summernote_config['summernote_css'] +
                summernote_config['css']
            ),
            'js': (
                summernote_config['base_js'] +
                summernote_config['summernote_js'] +
                summernote_config['js']
            ),
            'disable_upload': summernote_config['disable_upload'],
        }
    )


def upload_attachment(request):
    if request.method != 'POST':
        return JsonResponse({
            'status': 'false',
            'message': _('Only POST method is allowed'),
        }, status=400)

    if summernote_config['attachment_require_authentication']:
        if not request.user.is_authenticated():
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
