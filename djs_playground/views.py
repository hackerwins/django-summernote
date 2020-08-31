from django import forms
from django.shortcuts import render
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from .settings import SUMMERNOTE_THEME


class SampleForm(forms.Form):
    desc1 = forms.CharField(
        label='iframe',
        widget=SummernoteWidget()
    )
    desc2 = forms.CharField(
        label='inplace',
        widget=SummernoteInplaceWidget(),
        required=False
    )
    desc3 = forms.CharField(
        label='normal field',
        widget=forms.Textarea,
    )

    def clean(self):
        data = super().clean()

        if 'summer' not in data.get('desc1', ''):
            self.add_error('desc1', 'You have to put ‘summer’ in desc1')
            self.fields['desc1'].widget.attrs.update({'class': 'invalid'})
        if 'note' not in data.get('desc2', ''):
            self.add_error('desc2', 'You have to put ‘note’ in desc2')
            self.fields['desc2'].widget.attrs.update({'class': 'invalid'})


def index(request):
    passed = False
    form = SampleForm()

    if request.method == "POST":
        form = SampleForm(request.POST)
        if form.is_valid():
            passed = True
            form = SampleForm()

    return render(request, 'index.html', {
        'desc1': request.POST.get('desc1'),
        'desc2': request.POST.get('desc2'),
        'passed': passed,
        'form': form,
        'theme': SUMMERNOTE_THEME,
    })
