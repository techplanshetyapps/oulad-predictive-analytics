from django.db import models

class StudentDemographic(models.Model):
    student_id = models.CharField(max_length=50, unique=True)
    code_module = models.CharField(max_length=10)
    code_presentation = models.CharField(max_length=10)
    gender = models.CharField(max_length=10)
    region = models.CharField(max_length=50)  # Location / Region
    highest_education = models.CharField(max_length=100)  # Education Level
    imd_band = models.CharField(max_length=20)
    age_band = models.CharField(max_length=20)  # Age Group
    num_of_prev_attempts = models.IntegerField(default=0)
    studied_credits = models.IntegerField(default=0)
    disability = models.CharField(max_length=5)  # Disability Status
    avg_assessment_score = models.FloatField(default=0.0)  # Student Assessment Marks Summary
    vle_interaction_clicks = models.IntegerField(default=0)  # Virtual Learning Environment Interactions
    final_result = models.CharField(max_length=20)  # Pass, Fail, Withdrawn, Distinction

    def __str__(self):
        return f"Student {self.student_id} [{self.code_module}]"

class TeacherInsightFlag(models.Model):
    student = models.ForeignKey(StudentDemographic, on_delete=models.CASCADE)
    risk_score = models.FloatField(default=0.0)
    ai_recommendation = models.TextField()
    flagged_date = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Alert: {self.student.student_id} (Risk: {self.risk_score})"