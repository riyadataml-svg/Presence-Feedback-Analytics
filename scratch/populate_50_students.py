import os
import django
import random
import sys
from datetime import timedelta
from django.utils import timezone

# Add the project root to the sys path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from dashboard.models import Batch, DailyAttendance
from form.models import Student, Attendance
from feedback.models import Feedback

STUDENT_NAMES = [
    "Aarav Sharma", "Vivaan Gupta", "Aditya Patel", "Vihaan Singh", "Arjun Verma",
    "Sai Ram", "Ishaan Reddy", "Krishna Kumar", "Aryan Khan", "Shaurya Joshi",
    "Ananya Iyer", "Diya Malhotra", "Pari Saxena", "Saanvi Rao", "Myra Kapoor",
    "Kavya Nair", "Anika Bose", "Riya Das", "Aadhya Menon", "Sia Choudhury",
    "Rahul Verma", "Sneha Kapoor", "Amit Singh", "Priya Sharma", "Vikram Rathore",
    "Anjali Gupta", "Rohan Mehra", "Pooja Malhotra", "Karan Johar", "Simran Kaur",
    "Akash Verma", "Nisha Reddy", "Suresh Kumar", "Meena Kumari", "Rajesh Khanna",
    "Shilpa Shetty", "Abhishek Bachchan", "Aishwarya Rai", "Ranbir Kapoor", "Deepika Padukone",
    "Varun Dhawan", "Alia Bhatt", "Sidharth Malhotra", "Kiara Advani", "Kartik Aaryan",
    "Sara Ali Khan", "Janhvi Kapoor", "Ishaan Khatter", "Ananya Panday", "Tiger Shroff"
]

TOPICS = ["Python Basics", "Advanced JS", "React Hooks", "Database Normalization", "System Design", "Cloud Deployment"]

def populate_50():
    print("--- 50 STUDENT DATA SIMULATION ---")
    
    # 1. Cleanup old data
    print("Clearing old records for clean simulation...")
    Feedback.objects.all().delete()
    DailyAttendance.objects.all().delete()
    Attendance.objects.all().delete()
    Student.objects.all().delete()
    
    batches = list(Batch.objects.filter(status='Active'))
    if not batches:
        print("Error: No active batches found.")
        return

    print(f"Distributing 50 students across {len(batches)} batches...")

    for i in range(50):
        name = STUDENT_NAMES[i]
        batch = random.choice(batches)
        sid = f"STUD{1000 + i}"
        
        # Create Student
        student = Student.objects.create(
            sid=sid,
            name=name,
            phone_number=f"98{random.randint(10000000, 99999999)}",
            email=f"{name.lower().replace(' ', '.')}@ducat.com",
            course=batch.batch_name,
            current_batch=batch,
            branch=batch.trainer.branch
        )
        
        # Create Attendance (Random past 10 days)
        for d in range(random.randint(5, 10)):
            DailyAttendance.objects.create(
                batch=batch,
                student_sid=sid,
                student_name=name,
                date=timezone.now().date() - timedelta(days=d),
                is_present=random.random() > 0.1
            )

        # Create Feedbacks for ALL phases
        for p_num in range(1, 6):
            phase = f"P-{p_num}"
            
            # Vary ratings for 3, 4, 5 stars
            # Student 1-15: 5 stars
            # Student 16-35: 4 stars
            # Student 36-50: 3 stars (with some 4/5 mix)
            if i < 15:
                r1, r2, r3, r4 = 5, 5, 5, 5
                review = "Exceptional training! Everything was clear."
            elif i < 35:
                r1, r2, r3, r4 = random.randint(4, 5), 4, random.randint(4, 5), 4
                review = "Very good session. Explained well."
            else:
                r1, r2, r3, r4 = random.randint(3, 4), 3, random.randint(3, 4), random.randint(3, 4)
                review = "Good, but pace was a bit fast for me."

            Feedback.objects.create(
                student_id=sid,
                student_name=name,
                email=student.email,
                phone=student.phone_number,
                branch=batch.trainer.branch,
                trainer_name=batch.trainer.name,
                technology=batch.batch_name,
                batch_timing=batch.timing,
                batch_mode=random.choice(['Online', 'Offline']),
                batch_type=batch.batch_type,
                phase=phase,
                ques1_rating=r1,
                ques2_rating=r2,
                ques3_rating=r3,
                ques4_rating=r4,
                review_description=review,
                submitted_at=timezone.now() - timedelta(days=random.randint(1, 15))
            )

    print("\nSUCCESS: 50 Students populated with full history!")
    print(f"Total Feedback Records: {Feedback.objects.count()}")
    print(f"Check Dashboard now to see the Phase Hub and Stats.")

if __name__ == "__main__":
    populate_50()
