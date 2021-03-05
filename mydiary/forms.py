from django import forms
from mydiary.models import Diary

from django.forms import ModelForm, DateInput
from .models import Event


class DiaryForm(forms.ModelForm):
    class Meta:
        model = Diary
        fields = ['subject', 'content']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }
        labels = {
            'subject': '제목',
            'content': '내용',
        }


# 달력 테스트
class EventForm(ModelForm):
    class Meta:
        model = Event
        widgets = {
            'start_time': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'end_time': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['start_time'].input_formats = ('%Y-%m-%d',)
        self.fields['end_time'].input_formats = ('%Y-%m-%d',)