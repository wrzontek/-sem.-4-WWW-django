from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login_page/', views.login_page, name='login'),
    path('new_file/', views.new_file, name='new_file'),
    path('create_file/', views.create_file, name='create_file'),
    path('new_directory/', views.new_directory, name='new_directory'),
    path('create_directory/', views.create_directory, name='create_directory')
]