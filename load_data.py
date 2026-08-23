import os
import django
import pandas as pd
import kagglehub

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from ouled.models import StudentDemographic

print("Downloading dataset via kagglehub...")
path = kagglehub.dataset_download("anlgrbz/student-demographics-online-education-dataoulad")
files = os.listdir(path)
csv_filename = next((f for f in files if 'studentinfo' in f.lower()), files[0])
csv_file_path = os.path.join(path, csv_filename)

print(f"Loading CSV from: {csv_file_path}")
df = pd.read_csv(csv_file_path)

count = 0
print("Populating database...")
for _, row in df.head(200).iterrows():
    student_id = str(row.get('id_student', ''))
    StudentDemographic.objects.update_or_create(
        student_id=student_id,
        defaults={
            'code_module': str(row.get('code_module', '')),
            'gender': str(row.get('gender', '')),
            'age_band': str(row.get('age_band', '')),
            'region': str(row.get('region', '')),
            'highest_education': str(row.get('highest_education', '')),
            'disability': str(row.get('disability', '')),
            'vle_interaction_clicks': int(row.get('studied_credits', 0)),
            'avg_assessment_score': 75.0,
            'final_result': str(row.get('final_result', 'Unknown')),
        }
    )
    count += 1

print(f"Successfully loaded {count} student records into SQLite database!")
