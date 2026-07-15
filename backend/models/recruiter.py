"""
HireFlow AI - Recruiter Profile Model
Manages recruiter-specific information
"""

from datetime import datetime, timezone
from models.user import db


class RecruiterProfile(db.Model):
    """Recruiter profile extending User model"""
    __tablename__ = 'recruiter_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='SET NULL'), nullable=True)
    designation = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    linkedin_url = db.Column(db.String(500), nullable=True)
    is_company_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', back_populates='recruiter_profile')
    company = db.relationship('Company', back_populates='recruiter_profiles')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': self.user.to_public_dict() if self.user else None,
            'company_id': self.company_id,
            'company': self.company.to_short_dict() if self.company else None,
            'designation': self.designation,
            'department': self.department,
            'linkedin_url': self.linkedin_url,
            'is_company_admin': self.is_company_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<RecruiterProfile User:{self.user_id}>'
