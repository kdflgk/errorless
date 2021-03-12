from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from mydiary.models import Profile


class UserForm(UserCreationForm):
    email = forms.EmailField(label="이메일")

    class Meta:
        model = User
        fields = ("username", "email","password1", "password2")


class ProfileForm(forms.ModelForm):
    profile_photo = forms.ImageField(required=False) # 선택적으로 입력할 수 있음.

    class Meta:
        model = Profile
        fields = ['nickname','profile_photo']