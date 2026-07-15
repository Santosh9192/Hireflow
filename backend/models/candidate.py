"""
HireFlow AI - Candidate Profile Model
Manages candidate-specific information including education, experience, and preferences
"""

from datetime import datetime, timezone
from models.user import db


class CandidateProfile(db.Model):
    """Candidate profile extending User model"""
    __tablename__ = 'candidate_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    # Professional Info
    headline = db.Column(db.String(200), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    linkedin_url = db.Column(db.String(500), nullable=True)
    github_url = db.Column(db.String(500), nullable=True)
    portfolio_url = db.Column(db.String(500), nullable=True)
    website_url = db.Column(db.String(500), nullable=True)
    
    # Education (JSON field for flexibility)
    education = db.Column(db.JSON, nullable=True)
    # experience (JSON field)
    experience = db.Column(db.JSON, nullable=True)
    # projects (JSON field)
    projects = db.Column(db.JSON, nullable=True)
    # certifications (JSON field)
    certifications = db.Column(db.JSON, nullable=True)
    # languages (JSON array)
    languages = db.Column(db.JSON, nullable=True)
    
    # Job Preferences
    preferred_title = db.Column(db.String(200), nullable=True)
    preferred_locations = db.Column(db.Text, nullable=True)  # JSON array
    preferred_salary_min = db.Column(db.Integer, nullable=True)
    preferred_salary_max = db.Column(db.Integer, nullable=True)
    preferred_employment_type = db.Column(db.String(50), nullable=True)  # full-time, part-time, contract, internship
    preferred_work_mode = db.Column(db.String(50), nullable=True)  # remote, hybrid, on-site
    is_open_to_work = db.Column(db.Boolean, default=True)
    notice_period = db.Column(db.String(50), nullable=True)
    
    # Resume
    current_resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id', ondelete='SET NULL'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', back_populates='candidate_profile')
    current_resume = db.relationship('Resume', foreign_keys=[current_resume_id], post_update=True)
    applications = db.relationship('Application', back_populates='candidate', cascade='all, delete-orphan')
    skills = db.relationship('CandidateSkill', back_populates='candidate', cascade='all, delete-orphan')
    ai_analyses = db.relationship('AIAnalysis', back_populates='candidate', cascade='all, delete-orphan')
    interview_invitations = db.relationship('InterviewInvitation', back_populates='candidate', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': self.user.to_public_dict() if self.user else None,
            'headline': self.headline,
            'bio': self.bio,
            'linkedin_url': self.linkedin_url,
            'github_url': self.github_url,
            'portfolio_url': self.portfolio_url,
            'website_url': self.website_url,
            'education': self.education,
            'experience': self.experience,
            'projects': self.projects,
            'certifications': self.certifications,
            'languages': self.languages,
            'preferred_title': self.preferred_title,
            'preferred_locations': self.preferred_locations,
            'preferred_salary_min': self.preferred_salary_min,
            'preferred_salary_max': self.preferred_salary_max,
            'preferred_employment_type': self.preferred_employment_type,
            'preferred_work_mode': self.preferred_work_mode,
            'is_open_to_work': self.is_open_to_work,
            'notice_period': self.notice_period,
            'current_resume_id': self.current_resume_id,
            'skills': [s.to_dict() for s in self.skills] if self.skills else [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<CandidateProfile User:{self.user_id}>'
