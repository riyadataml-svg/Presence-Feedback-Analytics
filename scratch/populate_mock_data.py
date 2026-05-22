import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from dashboard.models import Batch, DailyAttendance
from form.models import Student, Attendance
from feedback.models import Feedback

# Sample Names for realism
STUDENT_NAMES = [
    "Aarav Sharma", "Vivaan Gupta", "Aditya Patel", "Vihaan Singh", "Arjun Verma",
    "Sai Ram", "Ishaan Reddy", "Krishna Kumar", "Aryan Khan", "Shaurya Joshi",
    "Ananya Iyer", "Diya Malhotra", "Pari Saxena", "Saanvi Rao", "Myra Kapoor",
    "Kavya Nair", "Anika Bose", "Riya Das", "Aadhya Menon", "Sia Choudhury"
]

TOPICS = ["Introduction", "Syntax & Datatypes", "Functions", "Loops", "Classes & Objects", "APIs", "Database Connectivity", "Front-end Basics"]

def populate():
    print("Starting mock data population...")
    batches = Batch.objects.filter(status='Active')
    
    if not batches.exists():
        print("No active batches found. Please create some batches first.")
        return

    for batch in batches:
        print(f"Populating Batch: {batch.batch_name} ({batch.timing})...")
        
        # Select 10 random names for this batch
        batch_student_names = random.sample(STUDENT_NAMES, 10)
        
        for i, name in enumerate(batch_student_names):
            sid = f"DUC{batch.id}{i+1000}"
            
            # 1. Create Student
            student, created = Student.objects.update_or_create(
                sid=sid,
                defaults={
                    'name': name,
                    'phone_number': f"98765{random.randint(10000, 99999)}",
                    'email': f"{name.lower().replace(' ', '.')}@example.com",
                    'course': batch.batch_name,
                    'current_batch': batch,
                    'branch': batch.trainer.branch
                }
            )
            
            # 2. Create Attendance Record
            Attendance.objects.create(
                name=name,
                student_id=sid,
                technology=batch.batch_name,
                today_topic=random.choice(TOPICS),
                batch_time=batch.timing,
                trainer_name=batch.trainer.name,
                week_type=batch.batch_type,
                batch_mode=random.choice(['Online', 'Offline']),
                submitted_at=timezone.now() - timedelta(days=random.randint(0, 30))
            )
            
            # 3. Create Daily Attendance (Present)
            DailyAttendance.objects.get_or_create(
                batch=batch,
                student_sid=sid,
                date=timezone.now().date(),
                defaults={'student_name': name, 'is_present': True}
            )

            # 4. Create Feedbacks for all 5 Phases
            for phase in ['P-1', 'P-2', 'P-3', 'P-4', 'P-5']:
                Feedback.objects.create(
                    student_id=sid,
                    student_name=name,
                    email=student.email,
                    phone=student.phone_number,
                    branch=batch.trainer.branch,
                    trainer_name=batch.trainer.name,
                    technology=batch.batch_name,
                    batch_timing=batch.timing,
                    batch_mode='Offline' if random.random() > 0.3 else 'Online',
                    batch_type=batch.batch_type,
                    phase=phase,
                    ques1_rating=random.randint(4, 5),
                    ques2_rating=random.randint(4, 5),
                    ques3_rating=random.randint(3, 5),
                    ques4_rating=random.randint(4, 5),
                    review_description=f"Great experience in {phase}. Trainer is very helpful.",
                    submitted_at=timezone.now() - timedelta(days=random.randint(0, 15))
                )

    print("\nPopulation complete!")
    print(f"Total Batches Processed: {batches.count()}")
    print(f"Total Students Created: {batches.count() * 10}")
    print(f"Total Feedbacks Created: {batches.count() * 10 * 5}")

if __name__ == "__main__":
    populate()
