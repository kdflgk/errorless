from django import forms
from mydiary.models import Diary

# from django.forms import ModelForm, DateInput
# from .models import Event


class DiaryForm(forms.ModelForm):
    class Meta:
        model = Diary
        fields = ['subject', 'content']
        # widgets = {
        #     'subject': forms.TextInput(attrs={'class': 'form-control'}),
        #     'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        # }
        labels = {
            'subject': '제목',
            'content': '내용',
        }
