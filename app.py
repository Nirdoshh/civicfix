"""CivicFix Flask Application

Main entry point for the CivicFix web project.
It configures Flask, SQLite, Flask-Login, registers routes, and creates
sample data for demonstration.
"""

import os
from datetime import datetime
from pathlib import Path
from flask import Flask
from flask_login import LoginManager
from models import db, User, Category, Department, Complaint, Attachment, StatusLog, AutoCategory


BASE_DIR = Path(__file__).resolve().parent
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    """Load the currently logged-in user from the database."""
    return User.query.get(int(user_id))


def create_app():
    """Application factory used locally and by Render/Gunicorn."""
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "civicfix-development-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///civicfix.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = str(BASE_DIR / "static" / "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB upload limit

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from routes.public import public_bp
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.admin import admin_bp
    from routes.department import department_bp
    from routes.api import api_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(department_bp)
    app.register_blueprint(api_bp)

    @app.template_filter("datetime")
    def format_datetime(value):
        """Format datetime values consistently in templates."""
        if not value:
            return "-"
        return value.strftime("%d %b %Y, %I:%M %p")

    @app.template_filter("date_only")
    def format_date(value):
        if not value:
            return "-"
        return value.strftime("%d %b %Y")

    with app.app_context():
        db.create_all()
        seed_default_data()

    return app


def create_complaint_code(complaint_id):
    """Generate a readable tracking ID such as CF-2026-0001."""
    return f"CF-{datetime.utcnow().year}-{complaint_id:04d}"


def seed_default_data():
    """Create default categories, departments, users, and sample complaints."""
    categories = [
        "Waste Management",
        "Water Supply",
        "Road Maintenance",
        "Electrical Issue",
        "Drainage",
        "Sanitation",
        "General Service",
    ]

    departments = [
        "Waste Management Department",
        "Water Supply Department",
        "Road Maintenance Department",
        "Electrical Department",
        "Drainage Department",
        "Sanitation Department",
        "General Service Department",
    ]

    for category_name in categories:
        if not Category.query.filter_by(category_name=category_name).first():
            db.session.add(Category(category_name=category_name))

    for department_name in departments:
        if not Department.query.filter_by(department_name=department_name).first():
            db.session.add(Department(department_name=department_name))

    db.session.commit()

    demo_accounts = [
        ("System Admin", "admin@civicfix.local", "admin", "admin123", None),
        ("Demo Citizen", "user@civicfix.local", "user", "user123", None),
        ("Waste Staff", "waste@civicfix.local", "department_staff", "staff123", "Waste Management Department"),
        ("Water Staff", "water@civicfix.local", "department_staff", "staff123", "Water Supply Department"),
        ("Road Staff", "road@civicfix.local", "department_staff", "staff123", "Road Maintenance Department"),
        ("Electrical Staff", "electrical@civicfix.local", "department_staff", "staff123", "Electrical Department"),
        ("Drainage Staff", "drainage@civicfix.local", "department_staff", "staff123", "Drainage Department"),
        ("Sanitation Staff", "sanitation@civicfix.local", "department_staff", "staff123", "Sanitation Department"),
    ]

    for full_name, email, role, password, department_name in demo_accounts:
        if not User.query.filter_by(email=email).first():
            department = Department.query.filter_by(department_name=department_name).first() if department_name else None
            user = User(
                full_name=full_name,
                email=email,
                role=role,
                department_id=department.department_id if department else None,
            )
            user.set_password(password)
            db.session.add(user)

    db.session.commit()

    # Create an SVG evidence image for demo use.
    sample_svg_path = BASE_DIR / "static" / "uploads" / "sample_evidence.svg"
    if not sample_svg_path.exists():
        sample_svg_path.write_text("""
        <svg xmlns='http://www.w3.org/2000/svg' width='900' height='560'>
          <rect width='900' height='560' fill='#e8f1ff'/>
          <rect x='80' y='80' width='740' height='400' rx='28' fill='#ffffff' stroke='#b8d4ff' stroke-width='6'/>
          <circle cx='220' cy='250' r='74' fill='#0d6efd' opacity='.16'/>
          <path d='M175 300h90l18 80H157z' fill='#0d6efd'/>
          <path d='M185 210h70l12 90h-94z' fill='#1f6feb'/>
          <circle cx='470' cy='270' r='90' fill='#198754' opacity='.16'/>
          <path d='M430 300c38-80 106-120 142-127-9 53-44 116-121 137z' fill='#198754'/>
          <text x='450' y='430' text-anchor='middle' font-family='Arial' font-size='36' font-weight='700' fill='#183b66'>Sample Evidence Image</text>
          <text x='450' y='470' text-anchor='middle' font-family='Arial' font-size='22' fill='#5b7190'>CivicFix Complaint Attachment</text>
        </svg>
        """.strip(), encoding="utf-8")

    demo_user = User.query.filter_by(email="user@civicfix.local").first()
    admin_user = User.query.filter_by(email="admin@civicfix.local").first()
    waste_category = Category.query.filter_by(category_name="Waste Management").first()
    waste_department = Department.query.filter_by(department_name="Waste Management Department").first()
    electrical_category = Category.query.filter_by(category_name="Electrical Issue").first()
    electrical_department = Department.query.filter_by(department_name="Electrical Department").first()

    if demo_user and waste_category and not Complaint.query.filter_by(title="Garbage pile near campus gate").first():
        complaint = Complaint(
            title="Garbage pile near campus gate",
            description="Garbage and plastic waste have not been collected near the campus gate for several days.",
            category_id=waste_category.category_id,
            department_id=waste_department.department_id if waste_department else None,
            user_id=demo_user.user_id,
            status="In Progress",
            location_lat=28.2096,
            location_lng=83.9856,
        )
        db.session.add(complaint)
        db.session.flush()
        complaint.complaint_code = create_complaint_code(complaint.complaint_id)
        db.session.add(Attachment(complaint_id=complaint.complaint_id, file_path="uploads/sample_evidence.svg"))
        db.session.add(AutoCategory(complaint_id=complaint.complaint_id, predicted_category="Waste Management", confidence_score=95))
        db.session.add(StatusLog(complaint_id=complaint.complaint_id, status="Pending", remarks="Complaint submitted with image evidence.", updated_by=demo_user.user_id))
        db.session.add(StatusLog(complaint_id=complaint.complaint_id, status="In Progress", remarks="Assigned to Waste Management Department.", updated_by=admin_user.user_id if admin_user else None))
        db.session.commit()

    if demo_user and electrical_category and not Complaint.query.filter_by(title="Broken street light near hostel block").first():
        complaint = Complaint(
            title="Broken street light near hostel block",
            description="The street light near hostel block B is not working at night and the area is unsafe.",
            category_id=electrical_category.category_id,
            department_id=electrical_department.department_id if electrical_department else None,
            user_id=demo_user.user_id,
            status="Resolved",
            location_lat=28.2107,
            location_lng=83.9861,
        )
        db.session.add(complaint)
        db.session.flush()
        complaint.complaint_code = create_complaint_code(complaint.complaint_id)
        db.session.add(AutoCategory(complaint_id=complaint.complaint_id, predicted_category="Electrical Issue", confidence_score=91))
        db.session.add(StatusLog(complaint_id=complaint.complaint_id, status="Pending", remarks="Complaint submitted by user.", updated_by=demo_user.user_id))
        db.session.add(StatusLog(complaint_id=complaint.complaint_id, status="In Progress", remarks="Electrical staff dispatched.", updated_by=admin_user.user_id if admin_user else None))
        db.session.add(StatusLog(complaint_id=complaint.complaint_id, status="Resolved", remarks="Street light repaired successfully.", updated_by=User.query.filter_by(email="electrical@civicfix.local").first().user_id))
        db.session.commit()


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
