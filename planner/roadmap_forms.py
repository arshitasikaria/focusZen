from django import forms

class GoalRoadmapForm(forms.Form):
    goal_text = forms.CharField(
        label="Your goal (e.g. Data Science)",
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Data Science, Web Developer'})
    )
    months = forms.IntegerField(
        label="Duration in months",
        min_value=1,
        max_value=36,
        initial=6
    )
