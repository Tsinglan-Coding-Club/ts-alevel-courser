from django.urls import path
from . import views

app_name = 'pastpaper'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('home/', views.home_view, name='home'),
    path('home/<str:subject_code>/', views.home_view, name='home_subject'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('mydetails/', views.mydetails_view, name='mydetails'),
    
    # API endpoints
    path('get_units/', views.get_units, name='get_units'),
    path('get_list/', views.get_list, name='get_list'),
    path('get_past_papers/', views.get_past_papers, name='get_past_papers'),
    path('get_question_info/', views.get_question_info, name='get_question_info'),
    path('get_history/', views.get_history, name='get_history'),
    path('update_user_tags/', views.update_user_tags, name='update_user_tags'),
    path('update_history/', views.update_history, name='update_history'),
]

