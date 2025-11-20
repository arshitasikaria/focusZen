from django.db import models
from django.contrib.auth.models import User

class Syllabus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    exam_date = models.DateField()
    topics = models.TextField(help_text="Comma-separated list of topics", blank=True)
    file = models.FileField(upload_to='syllabi/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_topics_list(self):
        return [t.strip() for t in self.topics.split(',') if t.strip()]


class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    task = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.task


class Roadmap(models.Model):
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE, related_name='roadmaps', null=True)
    day_number = models.IntegerField()
    date = models.DateField()
    topics = models.TextField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Day {self.day_number}: {self.topics}"


class ScheduledTopic(models.Model):
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE, related_name='scheduled_topics')
    topic = models.CharField(max_length=200)
    target_date = models.DateField()

    def __str__(self):
        return f"{self.topic} - {self.target_date}"
