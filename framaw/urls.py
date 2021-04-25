from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login_page/', views.login_page, name='login'),
    path('new_file/', views.new_file, name='new_file'),
    path('create_file/', views.create_file, name='create_file'),
    path('new_directory/', views.new_directory, name='new_directory'),
    path('create_directory/', views.create_directory, name='create_directory'),
    path('delete_file/', views.delete_file, name='delete_file'),
    path('do_delete_file/', views.do_delete_file, name='do_delete_file'),
    path('delete_dir/', views.delete_dir, name='delete_dir'),
    path('do_delete_dir/', views.do_delete_dir, name='do_delete_dir'),
    path('display_file/', views.display_file, name='display_file'),
]