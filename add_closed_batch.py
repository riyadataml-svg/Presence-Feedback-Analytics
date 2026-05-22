import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from dashboard.models import Batch, Trainer
from form.models import Student

def create_closed_data():
    trainer = Trainer.objects.first()
    if not trainer:
        print("No trainer found.")
        return

    # Create a closed batch
    batch = Batch.objects.create(
        trainer=trainer,
        batch_name='PYTHON MASTERCLASS (CLOSED)',
        batch_type='Weekdays',
        timing='10:00 AM - 12:00 PM',
        month='April',
        year='2026',
        status='Closed',
        start_date=timezone.now().date() - timezone.timedelta(days=30),
        end_date=timezone.now().date() - timezone.timedelta(days=1)
    )
    print(f"Created closed batch: {batch}")

    # Find or create a student and enroll them
    student = Student.objects.first()
    if student:
        batch.enrolled_students.add(student)
        print(f"Enrolled student {student.name} ({student.sid}) in the closed batch.")
    else:
        print("No student found to enroll.")

if __name__ == "__main__":
    create_closed_data()
