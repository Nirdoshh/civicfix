"""Database models for CivicFix.

This file defines all SQLite tables using Flask-SQLAlchemy.
The same models support users, complaints, uploaded evidence, status history,
departments, categories, and auto-categorization results.
"""

from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Stores regular users, admins, and department staff."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="user")
    department_id = db.Column(db.Integer, db.ForeignKey("departments.department_id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    complaints = db.relationship("Complaint", backref="user", lazy=True)
    department = db.relationship("Department", backref="staff_members", lazy=True)

    def get_id(self):
        """Flask-Login requires the user ID as a string."""
        return str(self.user_id)

    def set_password(self, raw_password):
        """Hash a password before storing it in the database."""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        """Check a raw password against the stored hash."""
        return check_password_hash(self.password, raw_password)


class Category(db.Model):
    """Complaint categories such as Waste Management and Water Supply."""

    __tablename__ = "categories"

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), unique=True, nullable=False)

    complaints = db.relationship("Complaint", backref="category", lazy=True)


class Department(db.Model):
    """Departments that receive and resolve assigned complaints."""

    __tablename__ = "departments"

    department_id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(120), unique=True, nullable=False)

    complaints = db.relationship("Complaint", backref="department", lazy=True)


class Complaint(db.Model):
    """Main complaint table."""

    __tablename__ = "complaints"

    complaint_id = db.Column(db.Integer, primary_key=True)
    complaint_code = db.Column(db.String(30), unique=True, nullable=True, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.category_id"), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.department_id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Pending")
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    location_lat = db.Column(db.Float, nullable=True)
    location_lng = db.Column(db.Float, nullable=True)

    attachments = db.relationship(
        "Attachment",
        backref="complaint",
        lazy=True,
        cascade="all, delete-orphan",
    )
    status_logs = db.relationship(
        "StatusLog",
        backref="complaint",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="StatusLog.updated_at.asc()",
    )
    auto_category = db.relationship(
        "AutoCategory",
        backref="complaint",
        lazy=True,
        uselist=False,
        cascade="all, delete-orphan",
    )


class Attachment(db.Model):
    """Stores evidence image paths for complaints."""

    __tablename__ = "attachments"

    attachment_id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.complaint_id"), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class StatusLog(db.Model):
    """Stores every status update and remark for audit tracking."""

    __tablename__ = "status_logs"

    log_id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.complaint_id"), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    remarks = db.Column(db.Text, nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True)

    updater = db.relationship("User", backref="status_updates", lazy=True)


class AutoCategory(db.Model):
    """Stores keyword-based NLP prediction results."""

    __tablename__ = "auto_categories"

    auto_id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.complaint_id"), nullable=False)
    predicted_category = db.Column(db.String(100), nullable=False)
    confidence_score = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
