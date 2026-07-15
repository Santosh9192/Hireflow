"""
HireFlow AI - Company Model
Manages company profiles for recruiters
"""

from datetime import datetime, timezone
from models.user import db


class Company(db.Model):
    """Company profile model"""
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(500), nullable=True)
    logo = db.Column(db.String(500), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    company_size = db.Column(db.String(50), nullable=True)  # 1-10, 11-50, 51-200, 201-1000, 1000+
    founded_year = db.Column(db.Integer, nullable=True)
    headquarters = db.Column(db.String(200), nullable=True)
    locations = db.Column(db.Text, nullable=True)  # JSON array of locations
    culture = db.Column(db.Text, nullable=True)
    benefits = db.Column(db.Text, nullable=True)
    social_links = db.Column(db.Text, nullable=True)  # JSON object
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    recruiter_profiles = db.relationship('RecruiterProfile', back_populates='company', cascade='all, delete-orphan')
    jobs = db.relationship('Job', back_populates='company', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'website': self.website,
            'logo': self.logo,
            'industry': self.industry,
            'company_size': self.company_size,
            'founded_year': self.founded_year,
            'headquarters': self.headquarters,
            'locations': self.locations,
            'culture': self.culture,
            'benefits': self.benefits,
            'social_links': self.social_links,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_short_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'logo': self.logo,
            'industry': self.industry,
            'headquarters': self.headquarters,
            'is_verified': self.is_verified
        }

    def __repr__(self):
        return f'<Company {self.name}>'
