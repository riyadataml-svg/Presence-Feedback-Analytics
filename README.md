# Ducat Project Dashboard

This is the main dashboard for tracking student presence and feedback across different branches (Vikaspuri, Pitampura). Built entirely with Django, it gives admins a clean interface to check trainer feedback, daily attendance, and overall class performance.

### Features
- Central dashboard with analytics and charts
- Track daily attendance and student feedback forms
- Filter records by branch, trainer, or course
- Export the data to Excel or CSV formats
- Simple branch switcher between Vikaspuri and Pitampura

### Tech Stack
- Python / Django 
- HTML, CSS, JavaScript
- SQLite (default setup for local testing)
- Chart.js (for the frontend graphs)

### How to run locally

1. Clone this repository to your machine.
2. Create a virtual environment so packages don't mess up your system:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Make sure the database is up to date:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Start the dev server:
   ```bash
   python manage.py runserver 8001
   ```
6. Open your browser and visit `http://127.0.0.1:8001/`

*Tip: If you need to access the backend, run `python manage.py createsuperuser` to create an admin account.*
