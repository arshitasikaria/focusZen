from django.urls import path
from . import views
from .views import add_syllabus, syllabus_list
from .views import add_todo, todo_list
from .views import complete_todo, delete_todo



urlpatterns = [
    path('', views.home, name='home'),
    path('syllabus/add/', add_syllabus, name='add_syllabus'),
    path('syllabus/', syllabus_list, name='syllabus_list'),
    path('todo/add/', add_todo, name='add_todo'),
    path('todo/', todo_list, name='todo_list'),

    path('todo/complete/<int:id>/', complete_todo, name='complete_todo'),
    path('todo/delete/<int:id>/', delete_todo, name='delete_todo'),



]
