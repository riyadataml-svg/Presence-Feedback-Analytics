#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from feedback.models import Feedback
from django.utils import timezone

# Update all NULL dates to current time
updated = Feedback.objects.filter(submitted_at__isnull=True).update(submitted_at=timezone.now())

# Verify
count = Feedback.objects.filter(submitted_at__isnull=True).count()
print(f"Updated {updated} records")
print(f"Remaining NULL dates: {count}")
print(f"Total feedback records: {Feedback.objects.count()}")
