"""
HireFlow AI - Job Model
Manages job postings created by recruiters
"""

from datetime import datetime, timezone
from models.user import db


class Job(db.Model):
    """Job posting model"""
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    posted_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Job Details
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=True)
    responsibilities = db.Column(db.Text, nullable=True)
    benefits = db.Column(db.Text, nullable=True)
    
    # Classification
    category = db.Column(db.String(100), nullable=True, index=True)
    subcategory = db.Column(db.String(100), nullable=True)
    employment_type = db.Column(db.String(50), nullable=True)  # full-time, part-time, contract, internship, temporary
    work_mode = db.Column(db.String(50), nullable=True)  # remote, hybrid, on-site
    experience_level = db.Column(db.String(50), nullable=True)  # entry, mid, senior, lead, executive
    min_experience = db.Column(db.Integer, nullable=True)
    max_experience = db.Column(db.Integer, nullable=True)
    
    # Location
    location = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True, default='United States')
    is_remote = db.Column(db.Boolean, default=False)
    
    # Compensation
    salary_min = db.Column(db.Integer, nullable=True)
    salary_max = db.Column(db.Integer, nullable=True)
    salary_currency = db.Column(db.String(10), default='USD')
    salary_period = db.Column(db.String(20), default='yearly')  # yearly, monthly, hourly
    show_salary = db.Column(db.Boolean, default=True)
    
    # Skills
    required_skills = db.Column(db.Text, nullable=True)  # JSON array
    preferred_skills = db.Column(db.Text, nullable=True)
    
    # Status & Settings
    status = db.Column(db.String(20), default='active', index=True)  # active, closed, draft, paused
    is_featured = db.Column(db.Boolean, default=False)
    is_urgent = db.Column(db.Boolean, default=False)
    application_deadline = db.Column(db.DateTime, nullable=True)
    positions_available = db.Column(db.Integer, default=1)
    views_count = db.Column(db.Integer, default=0)
    applications_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    published_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    company = db.relationship('Company', back_populates='jobs')
    poster = db.relationship('User', foreign_keys=[posted_by])
    applications = db.relationship('Application', back_populates='job', cascade='all, delete-orphan')
    saved_by = db.relationship('SavedJob', back_populates='job', cascade='all, delete-orphan')
    bookmarked_by = db.relationship('Bookmark', back_populates='job', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company': self.company.to_short_dict() if self.company else None,
            'posted_by': self.posted_by,
            'poster_name': self.poster.to_public_dict() if self.poster else None,
            'title': self.title,
            'description': self.description,
            'requirements': self.requirements,
            'responsibilities': self.responsibilities,
            'benefits': self.benefits,
            'category': self.category,
            'subcategory': self.subcategory,
            'employment_type': self.employment_type,
            'work_mode': self.work_mode,
            'experience_level': self.experience_level,
            'min_experience': self.min_experience,
            'max_experience': self.max_experience,
            'location': self.location,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'is_remote': self.is_remote,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'salary_currency': self.salary_currency,
            'salary_period': self.salary_period,
            'show_salary': self.show_salary,
            'required_skills': self.required_skills,
            'preferred_skills': self.preferred_skills,
            'status': self.status,
            'is_featured': self.is_featured,
            'is_urgent': self.is_urgent,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'positions_available': self.positions_available,
            'views_count': self.views_count,
            'applications_count': self.applications_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }

    def __repr__(self):
        return f'<Job {self.title} ({self.status})>'
