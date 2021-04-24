from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new_file/', views.new_file, name='new_file'),
    path('create_file/', views.create_file, name='create_file')
]