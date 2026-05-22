from django.shortcuts import render, redirect
from django.http import JsonResponse
from form.models import Student, Attendance
from django.contrib import messages
from django.db import models
from dashboard.models import Trainer
from .models import Feedback

def feedback_form(request, phase=None):
    # Get branch from query params
    branch_filter = request.GET.get('branch', 'Vikaspuri')
    trainers = Trainer.objects.filter(branch=branch_filter).order_by('name')
    
    # Phase normalization
    phase_map = {
        'phase-1': 'P-1', 'phase-2': 'P-2', 'phase-3': 'P-3',
        'phase-4': 'P-4', 'phase-5': 'P-5'
    }
    
    # If no phase is provided (bare link), DEFAULT TO P-1
    if not phase:
        mapped_phase = 'P-1'
    else:
        mapped_phase = phase_map.get(phase, phase)
    
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student_id')
            student_name = request.POST.get('student_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            branch = request.POST.get('branch', branch_filter)
            trainer_name = request.POST.get('trainer_name')
            technology = request.POST.get('batch_name') or request.POST.get('technology')
            
            # Legacy handling for old templates if any
            hour = request.POST.get('hour')
            batch_timing = request.POST.get('batch_timing', '00:00 AM')
            batch_mode = request.POST.get('batch_mode', 'Offline')
            batch_type = request.POST.get('batch_type', 'Weekdays')
            
            form_phase = mapped_phase if mapped_phase else request.POST.get('phase', 'P-1')
            
            # Check for duplicate
            if Feedback.objects.filter(student_id=student_id, phase=form_phase, technology=technology).exists():
                 messages.error(request, f'You have already submitted {form_phase} feedback for {technology}!')
                 if phase: return redirect('feedback_phase', phase=phase)
                 return redirect('feedback_form')

            q1 = int(request.POST.get('ques1_rating', 5))
            q2 = int(request.POST.get('ques2_rating', 5))
            q3 = int(request.POST.get('ques3_rating', 5))
            q4 = int(request.POST.get('ques4_rating', 5))
            
            review_desc = request.POST.get('review_description', '')
            
            # Normalize and Clean data for Dashboard Matching
            def clean_str(s): return str(s or '').strip().upper()
            
            f_trainer = clean_str(trainer_name)
            f_tech = clean_str(technology)
            f_timing = clean_str(batch_timing)
            # Remove " Batch" suffix if present in type (e.g. "Weekdays Batch" -> "WEEKDAYS")
            f_type = clean_str(batch_type).replace(' BATCH', '')
            f_phase = clean_str(form_phase)

            Feedback.objects.create(
                student_id=student_id, student_name=student_name, email=email, phone=phone,
                branch=branch, trainer_name=f_trainer, technology=f_tech,
                batch_timing=f_timing, batch_mode=batch_mode, batch_type=f_type,
                phase=f_phase, ques1_rating=q1, ques2_rating=q2, ques3_rating=q3,
                ques4_rating=q4, review_description=review_desc
            )
            messages.success(request, 'Success! Feedback submitted.')
            if phase: return redirect('feedback_phase', phase=phase)
            return redirect('feedback_form')
        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, 'Please fill all fields correctly.')

    # Labels for UI
    phase_labels = {
        'P-1': 'P-1 (Orientation & Basics)',
        'P-2': 'P-2 (Core Implementation)',
        'P-3': 'P-3 (Mid-Project Assessment)',
        'P-4': 'P-4 (Advanced Concepts)',
        'P-5': 'P-5 (Final Submission/Project)'
    }
    phase_label = phase_labels.get(mapped_phase, 'P-1 (Orientation & Basics)')
    
    # Pre-fetch all batches grouped by technology for dynamic frontend selection
    from django.utils import timezone
    from dashboard.models import Batch
    import json
    
    today = timezone.localdate()
    # 1. Fetch active batches for the selected branch
    batches = Batch.objects.select_related('trainer').filter(
        models.Q(status='Active') & 
        models.Q(trainer__branch=branch_filter) &
        (models.Q(end_date__gte=today) | models.Q(end_date__isnull=True))
    )
    
    # 2. Use static technology choices globally
    dynamic_tech_choices = Attendance.TECHNOLOGY_CHOICES
    
    # 3. Group batches by their technology (Fuzzy matching with static choices)
    batch_data = {t[0]: [] for t in dynamic_tech_choices}
    
    for b in batches:
        b_techs = []
        if b.batch_name: b_techs.append(b.batch_name.upper())
        if b.trainer and b.trainer.course: b_techs.append(b.trainer.course.upper())
        
        # Match batch against ALL possible static tech choices
        for tech_val, _ in dynamic_tech_choices:
            is_match = False
            for bt in b_techs:
                # Fuzzy match: "DATA ANALYTICS" matches "DATA ANALYTICS & AI"
                if bt in tech_val or tech_val in bt:
                    is_match = True
                    break
                # Special cases for course mapping
                if "MERN" in bt and "MERN" in tech_val: is_match = True
                if "JAVA" in bt and "JAVA" in tech_val: is_match = True
                if "MACHINE LEARNING" in bt and "DATA SCIENCE" in tech_val: is_match = True
                if "DATA SCIENCE" in bt and "MACHINE LEARNING" in tech_val: is_match = True
                
            if is_match:
                # Avoid duplicate batch entries under same tech
                if not any(exist_b['id'] == b.id for exist_b in batch_data[tech_val]):
                    batch_data[tech_val].append({
                        'id': b.id,
                        'batch_name': b.batch_name,
                        'trainer': b.trainer.name,
                        'timing': b.timing,
                        'type': b.batch_type
                    })

    context = {
        'trainers': trainers,
        'technology_choices': dynamic_tech_choices,  # Using dynamic list now
        'selected_phase': mapped_phase,
        'phase_label': phase_label,
        'batch_data_json': json.dumps(batch_data),
        'active_branch': branch_filter,
    }
    
    # Template selection mapping
    template_map = {
        'P-1': 'feedback/form_p1.html',
        'P-2': 'feedback/form_p2.html',
        'P-3': 'feedback/form_p3.html',
        'P-4': 'feedback/form_p4.html',
        'P-5': 'feedback/form.html', # Default for P-5
    }
    template = template_map.get(mapped_phase, 'feedback/form.html')
    return render(request, template, context)

def get_student_details(request):
    sid = request.GET.get('sid', '').strip()
    if sid:
        try:
            student = Student.objects.filter(sid=sid).first()
            print(student)
            if not student: student = Student.objects.filter(sid__icontains=sid).first()
            
            trainer = request.GET.get('trainer', '')
            phase = request.GET.get('phase', '')
            
            existing_fb = None
            if student and phase:
                # If trainer not provided, try to find it from student's current batch
                search_trainer = trainer or (student.current_batch.trainer.name if student.current_batch else None)
                if search_trainer:
                    existing_fb = Feedback.objects.filter(student_id=student.sid, trainer_name=search_trainer, phase=phase).first()
            
            if student:
                data = {
                    'id':student.sid,
                    'status': 'success',
                    'name': student.name,
                    'course': student.course.upper() if student.course else '',
                    'email': getattr(student, 'email', '') or '',
                    'phone': getattr(student, 'phone_number', '') or '',
                    'semester': getattr(student, 'semester', '') or '',
                    'section': getattr(student, 'section', '') or '',
                    'already_submitted': existing_fb is not None
                }
                
                # Add Batch Info if available
                if student.current_batch:
                    data.update({
                        'trainer_name': student.current_batch.trainer.name,
                        'batch_type': student.current_batch.batch_type,
                        'batch_timing': student.current_batch.timing
                    })
                
                if existing_fb:
                    data.update({
                        'q1': existing_fb.ques1_rating,
                        'q2': existing_fb.ques2_rating,
                        'q3': existing_fb.ques3_rating,
                        'q4': existing_fb.ques4_rating,
                        'review': existing_fb.review_description or ''
                    })
                
                return JsonResponse(data)
        except Exception as e:
            print(f"Fetch Error: {e}")
    return JsonResponse({'status': 'not_found'})
