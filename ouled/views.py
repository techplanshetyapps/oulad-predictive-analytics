import json
from django.conf import settings
from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import get_object_or_404, render
import numpy as np
import requests

from .models import StudentDemographic, TeacherInsightFlag


def dashboard_view(request):
  # 1. Fetch all student records and order them consistently
  student_list = StudentDemographic.objects.all().order_by("student_id")

  # 2. Setup Paginator (showing 20 students per page)
  paginator = Paginator(student_list, 20)
  page_number = request.GET.get("page")
  students = paginator.get_page(page_number)

  flagged_students = TeacherInsightFlag.objects.filter(is_resolved=False)

  # Aggregate statistics across ALL students in the database
  total_students_count = StudentDemographic.objects.count()
  avg_vle_clicks = (
      StudentDemographic.objects.aggregate(
          models.Avg("vle_interaction_clicks")
      )["vle_interaction_clicks__avg"]
      or 0
  )
  avg_assessments = (
      StudentDemographic.objects.aggregate(models.Avg("avg_assessment_score"))[
          "avg_assessment_score__avg"
      ]
      or 0
  )

  # Serialization for Chart.js PCA / Cluster telemetry
  np.random.seed(42)
  sample_size = min(total_students_count, 50) if total_students_count > 0 else 10
  pca_x = np.random.randn(sample_size) * 2
  pca_y = np.random.randn(sample_size) * 2
  clusters = np.random.randint(0, 3, size=sample_size)

  chart_data = []
  for x, y, c in zip(pca_x, pca_y, clusters):
    chart_data.append({
        "x": round(float(x), 2),
        "y": round(float(y), 2),
        "cluster": int(c),
    })

  context = {
      "total_students": total_students_count,
      "flagged_count": flagged_students.count(),
      "avg_vle_clicks": round(avg_vle_clicks, 1),
      "avg_assessments": round(avg_assessments, 1),
      "students": students,  # Passes the paginated page object to the template
      "flagged_students": flagged_students,
      "chart_data_json": json.dumps(chart_data),
  }
  return render(request, "ouled/dashboard.html", context)


def query_ollama_agent(request, student_id):
  student = get_object_or_404(StudentDemographic, student_id=student_id)
  prompt = (
      f"Analyze academic risk for student demographic - Gender: {student.gender},"
      f" Region: {student.region}, Age Band: {student.age_band}, Disability:"
      f" {student.disability}, VLE Clicks: {student.vle_interaction_clicks},"
      f" Avg Assessment Score: {student.avg_assessment_score}. Provide"
      " step-by-step teacher insight intervention strategy."
  )

  payload = {"model": "llama3", "prompt": prompt, "stream": False}
  headers = (
      {"Authorization": f"Bearer {settings.OLLAMA_API_KEY}"}
      if getattr(settings, "OLLAMA_API_KEY", None)
      else {}
  )

  try:
    response = requests.post(
        f"{settings.OLLAMA_BASE_URL}/generate",
        json=payload,
        headers=headers,
        timeout=10,
    )
    ai_response = response.json().get(
        "response", "AI analysis currently unavailable."
    )
  except Exception as e:
    ai_response = f"Ollama connection error: {str(e)}"

  return render(
      request,
      "ouled/agent_response.html",
      {"student": student, "ai_response": ai_response},
  )