from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard_alt'), # Optional: handles /dashboard explicitly
    path('agent/<str:student_id>/', views.query_ollama_agent, name='query_agent'),
]