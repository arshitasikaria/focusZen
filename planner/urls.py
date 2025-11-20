from django.urls import path
from . import views
from .views import upload_syllabus, syllabus_list, syllabus_plan
from .views import add_todo, todo_list
from .views import complete_todo, delete_todo
from .views import generate_goal_roadmap
from .views import wellness_timer
from .views import custom_login, register
from django.views.generic.base import RedirectView
from django.urls import reverse_lazy




urlpatterns = [
    path('', views.home, name='home'),
    path('syllabus/upload/', upload_syllabus, name='upload_syllabus'),
    path('syllabus/add/', views.add_syllabus, name='add_syllabus'),
    path('syllabus/', syllabus_list, name='syllabus_list'),
    path('syllabus/<int:syllabus_id>/plan/', syllabus_plan, name='syllabus_plan'),
    path('syllabus/<int:syllabus_id>/complete/', views.complete_syllabus, name='complete_syllabus'),
    path('roadmap/<int:roadmap_id>/complete/', views.complete_roadmap_day, name='complete_roadmap_day'),
    path('todo/add/', add_todo, name='add_todo'),
    path('todo/', todo_list, name='todo_list'),

    path('todo/complete/<int:id>/', complete_todo, name='complete_todo'),
    path('todo/delete/<int:id>/', delete_todo, name='delete_todo'),
    path('goal-roadmap/', generate_goal_roadmap, name='generate_goal_roadmap'),
    path('roadmap/', RedirectView.as_view(url='/goal-roadmap/', permanent=False), name='roadmap_redirect'),
    path('wellness/timer/', wellness_timer, name='wellness_timer'),
     path('wellness/', RedirectView.as_view(url=reverse_lazy('wellness_timer'), permanent=False), name='wellness_redirect'),
    path('login/', custom_login, name='login'),
    path('register/', register, name='register'),

]

