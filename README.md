# CivicFix: Smart Complaint Management and Tracking System with Auto-Categorization

Final-year Bachelor of Software Engineering project website for complaint registration, auto-categorization, department assignment, status tracking, and reports.

## Features

- Public home, about, features, and complaint tracking pages
- Register, login, logout, and forgot password page
- Secure password hashing using Werkzeug
- Role-based dashboards:
  - Regular User
  - Admin
  - Department Staff
- Complaint submission with:
  - Title
  - Description
  - Auto-suggested category using keyword-based NLP
  - Image evidence upload
  - Leaflet + OpenStreetMap location picker
- Complaint ID generation like `CF-2026-0001`
- Admin complaint filters, assignment, status update, remarks, users, departments
- Department staff complaint status update and resolution remarks
- Status timeline/history logs
- Reports and analytics using Chart.js
- CSV export and browser print/PDF support
- Responsive Bootstrap 5 design

## Tech Stack

- Frontend: HTML, CSS, Bootstrap 5, JavaScript
- Backend: Python Flask
- Database: SQLite with Flask-SQLAlchemy
- Authentication: Flask-Login
- Map: Leaflet.js + OpenStreetMap
- Charts: Chart.js
- Auto-categorization: Offline keyword-based Python NLP

## Project Structure

```text
civicfix_final_project/
├── app.py
├── models.py
├── categorizer.py
├── requirements.txt
├── render.yaml
├── routes/
│   ├── public.py
│   ├── auth.py
│   ├── user.py
│   ├── admin.py
│   ├── department.py
│   └── api.py
├── templates/
│   ├── base.html
│   ├── public/
│   ├── auth/
│   ├── user/
│   ├── admin/
│   └── department/
└── static/
    ├── css/
    ├── js/
    └── uploads/
```

## How to Run Locally on Windows

Open CMD or PowerShell inside the project folder and run:

```bash
python -m pip install -r requirements.txt
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Demo Accounts

```text
Admin:
admin@civicfix.local
admin123

Regular User:
user@civicfix.local
user123

Department Staff:
waste@civicfix.local
staff123
```

Other department staff accounts use the same password `staff123`:

```text
water@civicfix.local
road@civicfix.local
electrical@civicfix.local
drainage@civicfix.local
sanitation@civicfix.local
```

## Render Deployment

This project includes `render.yaml` and `gunicorn` in `requirements.txt`.

1. Upload the project to GitHub.
2. Go to Render.
3. Create a new Web Service.
4. Connect your GitHub repository.
5. Use:

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

Render will provide a public `onrender.com` link after deployment.

## Notes

SQLite is suitable for local demos and academic presentations. For production deployment, use PostgreSQL or MySQL and protected persistent storage for uploaded evidence files.
