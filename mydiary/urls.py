from django.urls import path
from pyreadline.release import url

from . import views

# 달력테스트
from django.contrib import admin
from django.urls import path
#

app_name = 'mydiary'

urlpatterns = [
    path(r'^profile_update/$', views.ProfileUpdateView.as_view(), name='profile_update'),
    path(r'^profile/(?P<pk>[0-9]+)/$', views.ProfileView.as_view(), name='profile'),
    path('', views.startup, name='startup'),
    path('main/', views.main, name='main'),
    path('write/', views.write, name='write'),
    path('movie/', views.movierecom, name='movierecom'),
    # path('mypage/', views.mypage, name='mypage'),
    path('mydiary/<int:question_id>/', views.detail, name='detail'),
    path('mydiary/delete/<int:question_id>/', views.diary_delete, name='diary_delete'),
    path('about/',views.about, name='about'),


]