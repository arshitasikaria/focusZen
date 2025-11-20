from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SyllabusForm, RegisterForm, LoginForm
from .models import Syllabus, Todo, Roadmap
from django.db.models import Count, Q
import math
import datetime
import difflib
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.shortcuts import render, redirect
from .roadmap_forms import GoalRoadmapForm
import PyPDF2
import pytesseract
from PIL import Image
import os


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
@login_required
def add_syllabus(request):
    if request.method == 'POST':
        form = SyllabusForm(request.POST)
        if form.is_valid():
            syllabus = form.save(commit=False)
            syllabus.user = request.user
            syllabus.save()
            return redirect('syllabus_list')
    else:
        form = SyllabusForm()
    return render(request, 'planner/add_syllabus.html', {'form': form})

# Syllabus: list view
@login_required
def syllabus_list(request):
    items = Syllabus.objects.filter(user=request.user).annotate(
        total_count=Count('roadmaps'),
        completed_count=Count('roadmaps', filter=Q(roadmaps__completed=True))
    ).all()
    for item in items:
        if item.total_count > 0:
            item.progress_percent = (item.completed_count / item.total_count) * 100
        else:
            item.progress_percent = 0
    return render(request, 'planner/syllabus_list.html', {'items': items})

# Todo: add task view
@login_required
def add_todo(request):
    if request.method == "POST":
        task = request.POST.get("task")
        if task:
            Todo.objects.create(task=task, user=request.user)
            return redirect('todo_list')
    return render(request, 'planner/add_todo.html')

# Todo: list view
@login_required
def todo_list(request):
    todos = Todo.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'planner/todo_list.html', {'todos': todos})

# Todo: mark complete
def complete_todo(request, id):
    todo = get_object_or_404(Todo, id=id)
    todo.completed = True
    todo.save()
    return redirect('todo_list')

# Todo: delete
@login_required
def delete_todo(request, id):
    todo = get_object_or_404(Todo, id=id, user=request.user)
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
def wellness_timer(request):
    # Simple view — everything is handled by the template JS
    return render(request, 'planner/wellness_timer.html')

def custom_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name}!")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please check the form.")
    else:
        form = RegisterForm()
    return render(request, 'planner/register.html', {'form': form})

def complete_syllabus(request, syllabus_id):
    syllabus = get_object_or_404(Syllabus, id=syllabus_id)
    syllabus.completed = True
    syllabus.save()
    return redirect('syllabus_list')

@login_required
def complete_roadmap_day(request, roadmap_id):
    roadmap = get_object_or_404(Roadmap, id=roadmap_id, syllabus__user=request.user)
    roadmap.completed = True
    roadmap.save()
    return redirect('syllabus_plan', syllabus_id=roadmap.syllabus.id)


# Helper functions for syllabus processing
def extract_text_from_pdf(file_path):
    """Extract text from PDF file."""
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_image(file_path):
    """Extract text from image file using OCR."""
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text

def parse_topics(raw_text):
    """Simple topic parsing - split by lines and filter."""
    lines = raw_text.split('\n')
    topics = []
    for line in lines:
        line = line.strip()
        if len(line) > 3 and not line.isdigit() and not line.startswith(('Chapter', 'Unit', 'Module')):
            # Basic filtering - can be improved with AI later
            topics.append(line)
    return topics[:20]  # Limit to 20 topics for now

def distribute_topics(topics, start_date, end_date):
    """Distribute topics across days from start to end date."""
    if not topics:
        return []

    days_diff = (end_date - start_date).days
    if days_diff <= 0:
        return []

    topics_per_day = max(1, len(topics) // days_diff)
    roadmap_entries = []

    current_date = start_date
    topic_index = 0

    while current_date <= end_date and topic_index < len(topics):
        day_topics = topics[topic_index:topic_index + topics_per_day]
        if day_topics:
            roadmap_entries.append({
                'date': current_date,
                'topics': ', '.join(day_topics)
            })
        topic_index += topics_per_day
        current_date += datetime.timedelta(days=1)

    return roadmap_entries

# Syllabus upload view
def upload_syllabus(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = SyllabusForm(request.POST, request.FILES)
        if form.is_valid():
            syllabus = form.save(commit=False)
            syllabus.user = request.user

            # Process file if uploaded
            if syllabus.file:
                file_path = syllabus.file.path
                file_ext = os.path.splitext(file_path)[1].lower()

                try:
                    if file_ext == '.pdf':
                        raw_text = extract_text_from_pdf(file_path)
                    elif file_ext in ['.jpg', '.jpeg', '.png']:
                        raw_text = extract_text_from_image(file_path)
                    else:
                        messages.error(request, "Unsupported file format. Please upload PDF or image.")
                        return render(request, 'planner/add_syllabus.html', {'form': form})

                    # Parse topics
                    topics = parse_topics(raw_text)
                    syllabus.topics = ', '.join(topics)

                    # Save syllabus
                    syllabus.save()

                    # Generate study plan
                    start_date = timezone.now().date()
                    end_date = syllabus.exam_date
                    plan_entries = distribute_topics(topics, start_date, end_date)

                    # Save to Roadmap
                    for entry in plan_entries:
                        Roadmap.objects.create(
                            syllabus=syllabus,
                            day_number=(entry['date'] - start_date).days + 1,
                            date=entry['date'],
                            topics=entry['topics']
                        )

                    messages.success(request, f"Syllabus uploaded and study plan generated! {len(topics)} topics found.")
                    return redirect('syllabus_plan', syllabus_id=syllabus.id)

                except Exception as e:
                    messages.error(request, f"Error processing file: {str(e)}")
                    return render(request, 'planner/add_syllabus.html', {'form': form})
            else:
                # Manual entry
                syllabus.save()
                messages.success(request, "Syllabus saved successfully!")
                return redirect('syllabus_list')
    else:
        form = SyllabusForm()

    return render(request, 'planner/add_syllabus.html', {'form': form})

# Syllabus plan view
@login_required
def syllabus_plan(request, syllabus_id):
    syllabus = get_object_or_404(Syllabus, id=syllabus_id, user=request.user)
    roadmap = syllabus.roadmaps.all().order_by('date')

    # Calculate progress
    total_days = roadmap.count()
    completed_days = roadmap.filter(completed=True).count()
    progress_percentage = (completed_days / total_days * 100) if total_days > 0 else 0

    # Estimated days left
    today = timezone.now().date()
    remaining_days = roadmap.filter(date__gte=today, completed=False).count()

    context = {
        'syllabus': syllabus,
        'roadmap': roadmap,
        'progress_percentage': progress_percentage,
        'completed_days': completed_days,
        'total_days': total_days,
        'remaining_days': remaining_days,
    }

    return render(request, 'planner/syllabus_plan.html', context)

