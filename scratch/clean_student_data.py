import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from dashboard.models import Attendance, Feedback, Student, DailyAttendance

def clean_data():
    print("Deleting all Student, Attendance, and Feedback records...")
    
    # Order matters for foreign keys
    try:
        feedback_count = Feedback.objects.all().delete()[0]
        attendance_count = Attendance.objects.all().delete()[0]
        daily_count = DailyAttendance.objects.all().delete()[0]
        student_count = Student.objects.all().delete()[0]
        
        print(f"Successfully deleted:")
        print(f"- {feedback_count} Feedback records")
        print(f"- {attendance_count} Attendance records")
        print(f"- {daily_count} DailyAttendance records")
        print(f"- {student_count} Student records")
        print("\nTrainers and Batches were preserved.")
        
    except Exception as e:
        print(f"Error during deletion: {e}")

if __name__ == "__main__":
    clean_data()
