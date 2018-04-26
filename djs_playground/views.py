# -*- coding: utf-8 -*-
from django import forms
from django.shortcuts import render
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget


class SampleForm(forms.Form):
    desc1 = forms.CharField(
        label='iframe',
        widget=SummernoteWidget(attrs={'summernote': {'toolbar': [['font', ['italic']]]}})
    )
    desc2 = forms.CharField(
        label='in place',
        widget=SummernoteInplaceWidget(attrs={'data-user-id': 123456, 'data-device': 'iphone'})
    )


def index(request):
    return render(request, 'index.html', {
        'desc1': request.POST.get('desc1'),
        'desc2': request.POST.get('desc2'),
        'form': SampleForm(),
    })
