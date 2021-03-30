from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse

# Create your models here.


class Diary(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)
    modify_date = models.DateTimeField(null=True, blank=True)
    content = models.CharField(max_length=200)
    moodres = models.CharField(max_length=200)
    create_date = models.DateTimeField()

    def __str__(self):
        return self.subject


class Answer(models.Model):
    question = models.ForeignKey(Diary, on_delete=models.CASCADE)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # 현 계정의 사용자를 가져올 수 있음.
    nickname = models.CharField(max_length=64)
    profile_photo = models.ImageField(upload_to='static/images',blank=True)                 # 값을 채워넣지 않아도 되는 속성.

