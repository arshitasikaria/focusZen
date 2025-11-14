from django.db import models

class Syllabus(models.Model):
    subject = models.CharField(max_length=200)
    topic = models.CharField(max_length=300)
    estimated_time = models.IntegerField(help_text="Time in minutes")
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} - {self.topic}"


class Todo(models.Model):
    task = models.CharField(max_length=300)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.task
