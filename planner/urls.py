from django.urls import path
from . import views
from .views import add_syllabus, syllabus_list
from .views import add_todo, todo_list
from .views import complete_todo, delete_todo
from .views import generate_goal_roadmap
from .views import wellness_timer 
from django.urls import path
from django.views.generic.base import RedirectView
from django.urls import reverse_lazy

from django.views.generic.base import RedirectView




urlpatterns = [
    path('', views.home, name='home'),
    path('syllabus/add/', add_syllabus, name='add_syllabus'),
    path('syllabus/', syllabus_list, name='syllabus_list'),
    path('todo/add/', add_todo, name='add_todo'),
    path('todo/', todo_list, name='todo_list'),

    path('todo/complete/<int:id>/', complete_todo, name='complete_todo'),
    path('todo/delete/<int:id>/', delete_todo, name='delete_todo'),
    path('goal-roadmap/', generate_goal_roadmap, name='generate_goal_roadmap'),
    path('roadmap/', RedirectView.as_view(url='/goal-roadmap/', permanent=False), name='roadmap_redirect'),
    path('wellness/timer/', wellness_timer, name='wellness_timer'),
     path('wellness/', RedirectView.as_view(url=reverse_lazy('wellness_timer'), permanent=False)),
    path('wellness/timer/', views.wellness_timer, name='wellness_timer'),

]

