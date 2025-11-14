from django.shortcuts import render, redirect, get_object_or_404
from .forms import SyllabusForm
from .models import Syllabus, Todo

# Homepage
def home(request):
    return render(request, 'planner/home.html')

# Syllabus: add form view
def add_syllabus(request):
    if request.method == 'POST':
        form = SyllabusForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('syllabus_list')
    else:
        form = SyllabusForm()
    return render(request, 'planner/add_syllabus.html', {'form': form})

# Syllabus: list view
def syllabus_list(request):
    items = Syllabus.objects.all()
    return render(request, 'planner/syllabus_list.html', {'items': items})

# Todo: add task view
def add_todo(request):
    if request.method == "POST":
        task = request.POST.get("task")
        if task:
            Todo.objects.create(task=task)
            return redirect('todo_list')
    return render(request, 'planner/add_todo.html')

# Todo: list view
def todo_list(request):
    todos = Todo.objects.all().order_by('-created_at')
    return render(request, 'planner/todo_list.html', {'todos': todos})

# Todo: mark complete
def complete_todo(request, id):
    todo = get_object_or_404(Todo, id=id)
    todo.completed = True
    todo.save()
    return redirect('todo_list')

# Todo: delete
def delete_todo(request, id):
    todo = get_object_or_404(Todo, id=id)
    todo.delete()
    return redirect('todo_list')
