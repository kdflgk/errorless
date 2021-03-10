from django.urls import path
from . import views

# 달력테스트
from django.contrib import admin
from django.urls import path
#

app_name = 'mydiary'

urlpatterns = [

    path('', views.startup, name='startup'),
    path('main/', views.main, name='main'),
    path('write/', views.write, name='write'),
    path('mydiary/<int:question_id>/', views.detail, name='detail'),
    path('mydiary/delete/<int:question_id>/', views.diary_delete, name='diary_delete'),

    # # 달력테스트
    # path('cal/', views.calendar_view, name="calendar"),
    # path('mydiary/new/', views.event, name="new"),
    # path('<int:event_id>', views.event, name="edit"),
    # #
]