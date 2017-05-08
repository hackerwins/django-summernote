from django.http import (
    HttpResponseBadRequest,
    HttpResponseServerError,
    HttpResponseForbidden,
)
from django.shortcuts import render
from django_summernote.settings import summernote_config, get_attachment_model
from django.utils.translation import ugettext_lazy as _

def editor(request, id):
    return render(
        request,
        'django_summernote/widget_iframe_editor.html',
        {
            'id_src': id,
            'id': id.replace('-', '_'),
            'css': (
                summernote_config['default_css'] +
                summernote_config['css']
            ),
            'js': (
                summernote_config['default_js'] +
                summernote_config['js']
            ),
            'disable_upload': summernote_config['disable_upload'],
        }
    )


def upload_attachment(request):
    if request.method != 'POST':
        return HttpResponseBadRequest(_('Only POST method is allowed'))

    if summernote_config['attachment_require_authentication']:
        if not request.user.is_authenticated():
            return HttpResponseForbidden(_('Only authenticated users are allowed'))

    if not request.FILES.getlist('files'):
        return HttpResponseBadRequest(_('No files were requested'))

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
                return HttpResponseBadRequest(
                    _('File size exceeds the limit allowed and cannot be saved')
                )

            # calling save method with attachment parameters as kwargs
            attachment.save(**kwargs)

            attachments.append(attachment)

        return render(request, 'django_summernote/upload_attachment.json', {
            'attachments': attachments,
        })
    except IOError:
        return HttpResponseServerError(_('Failed to save attachment'))
