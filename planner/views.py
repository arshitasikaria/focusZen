from django.shortcuts import render, redirect, get_object_or_404
from .forms import SyllabusForm
from .models import Syllabus, Todo
import math
import datetime 
import difflib
import math
from django.shortcuts import render, redirect
from .roadmap_forms import GoalRoadmapForm


# ===========================================
#   SKILL DATABASE FOR GOALS (GOAL → SKILLS)
# ===========================================
GOAL_SKILLS = {
    "data science": [
        "Python Basics",
        "NumPy & Pandas",
        "EDA (Exploratory Data Analysis)",
        "Data Visualization (Matplotlib/Seaborn)",
        "Statistics & Probability",
        "Machine Learning (Supervised/Unsupervised)",
        "Model Deployment",
        "Projects & Portfolio"
    ],

    "ai engineer": [
        "Python + Math Basics",
        "Linear Algebra & Calculus",
        "Machine Learning Algorithms",
        "Deep Learning (Neural Networks)",
        "TensorFlow / PyTorch",
        "NLP / Computer Vision",
        "MLOps Basics",
        "Final Projects"
    ],

    "web development": [
        "HTML, CSS, JavaScript",
        "Frontend Framework (React)",
        "Backend (Django or Node)",
        "Databases (SQL)",
        "API Development",
        "Authentication & Security",
        "Full-Stack Project"
    ],

    "android development": [
        "Java / Kotlin Basics",
        "Android Studio & SDK",
        "UI Layouts & Navigation",
        "API Integration",
        "Local DB (Room)",
        "Firebase",
        "Complete App Project"
    ],

    "cyber security": [
        "Networking Basics",
        "Linux & Shell",
        "Ethical Hacking Fundamentals",
        "Web Vulnerabilities (OWASP)",
        "Tools: Burp Suite, Wireshark",
        "Pentesting Methodology",
        "Reports & Portfolio"
    ],

    "cloud computing": [
        "Cloud Fundamentals",
        "AWS / GCP / Azure Core Services",
        "Compute, Storage & Networking",
        "IAM & Security",
        "Serverless & Containers",
        "DevOps Basics (CI/CD)",
        "Cloud Deployment Project"
    ],

    "python developer": [
        "Python Syntax & Basics",
        "OOP & Modules",
        "File Handling & I/O",
        "Testing & Debugging",
        "Django / Flask",
        "Build Projects"
    ],

    "java developer": [
        "Core Java & OOP",
        "Collections & Generics",
        "JDBC & Database",
        "Spring Boot",
        "RESTful APIs",
        "Project + Deployment"
    ],

    "ui ux designer": [
        "Design Principles",
        "Figma / Sketch",
        "Wireframing & Prototyping",
        "User Research",
        "Design Systems",
        "Portfolio Projects"
    ],

    "default": [
        "Foundational Concepts",
        "Plan Projects",
        "Build Portfolio"
    ]
}




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


def generate_goal_roadmap(request):
    """
    Generate a monthly + weekly roadmap from a user-entered goal (using GOAL_SKILLS).
    This does not use the DB — it builds the roadmap in memory and renders a result page.
    """
    if request.method == 'POST':
        form = GoalRoadmapForm(request.POST)
        if form.is_valid():
            user_goal = form.cleaned_data['goal_text'].strip().lower()
            months = form.cleaned_data['months']

            # 1) Match user goal to the known GOAL_SKILLS keys
            all_goals = [k for k in GOAL_SKILLS.keys() if k != "default"]
            match = difflib.get_close_matches(user_goal, all_goals, n=1, cutoff=0.2)
            if match:
                matched_goal = match[0]
            else:
                # Try simple substring match
                matched_goal = None
                for g in all_goals:
                    if user_goal in g or g in user_goal:
                        matched_goal = g
                        break
                if not matched_goal:
                    matched_goal = "default"

            # 2) Get skills list
            skills = GOAL_SKILLS.get(matched_goal, GOAL_SKILLS.get("default", []))

            # 3) Distribute skills across months
            total_skills = len(skills)
            if total_skills == 0:
                # nothing to show — return empty result
                roadmap_months = [{"month": m, "skills": [], "weeks": [[], [], [], []]} for m in range(1, months + 1)]
            else:
                skills_per_month = max(1, math.ceil(total_skills / months))
                roadmap_months = []
                idx = 0
                for m in range(1, months + 1):
                    month_skills = skills[idx: idx + skills_per_month]
                    idx += skills_per_month

                    # split month_skills into 4 weekly buckets
                    weeks = []
                    if month_skills:
                        wk_size = max(1, math.ceil(len(month_skills) / 4))
                        for w in range(4):
                            week_slice = month_skills[w*wk_size : (w+1)*wk_size]
                            weeks.append(week_slice)
                    else:
                        weeks = [[], [], [], []]

                    roadmap_months.append({
                        "month": m,
                        "skills": month_skills,
                        "weeks": weeks
                    })

            # Prepare a friendly goal title for display
            display_goal = matched_goal.title() if matched_goal != "default" else form.cleaned_data['goal_text'].title()

            return render(request, 'planner/goal_roadmap_result.html', {
                "goal": display_goal,
                "months": months,
                "roadmap": roadmap_months
            })
    else:
        form = GoalRoadmapForm()

    return render(request, 'planner/goal_roadmap_form.html', {"form": form})
