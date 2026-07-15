"""
HireFlow AI - Resume Model
Manages candidate resume uploads and parsing
"""

from datetime import datetime, timezone
from models.user import db


class Resume(db.Model):
    """Resume/CV model"""
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # File Details
    title = db.Column(db.String(200), nullable=True)  # User-given title
    filename = db.Column(db.String(500), nullable=False)
    original_filename = db.Column(db.String(500), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)  # Size in bytes
    file_type = db.Column(db.String(20), nullable=True)  # pdf, docx
    
    # Parsed Content
    parsed_text = db.Column(db.Text, nullable=True)
    parsed_data = db.Column(db.JSON, nullable=True)  # Structured parsed data
    is_parsed = db.Column(db.Boolean, default=False)
    
    # AI Analysis
    ats_score = db.Column(db.Integer, nullable=True)  # ATS compatibility score
    summary = db.Column(db.Text, nullable=True)
    strengths = db.Column(db.Text, nullable=True)
    weaknesses = db.Column(db.Text, nullable=True)
    missing_skills = db.Column(db.Text, nullable=True)
    suggestions = db.Column(db.Text, nullable=True)
    
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', back_populates='resumes')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'parsed_text': self.parsed_text[:500] + '...' if self.parsed_text and len(self.parsed_text) > 500 else self.parsed_text,
            'parsed_data': self.parsed_data,
            'is_parsed': self.is_parsed,
            'ats_score': self.ats_score,
            'summary': self.summary,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'missing_skills': self.missing_skills,
            'suggestions': self.suggestions,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Resume {self.original_filename} (User:{self.user_id})>'
