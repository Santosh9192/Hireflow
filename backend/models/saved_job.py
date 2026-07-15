"""
HireFlow AI - Saved Job & Bookmark Models
Manages user saved jobs and bookmarks
"""

from datetime import datetime, timezone
from models.user import db


class SavedJob(db.Model):
    """Saved jobs model - for candidates saving jobs to review later"""
    __tablename__ = 'saved_jobs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', back_populates='saved_jobs')
    job = db.relationship('Job', back_populates='saved_by')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'job_id', name='unique_user_job_save'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'job': self.job.to_dict() if self.job else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<SavedJob User:{self.user_id} Job:{self.job_id}>'


class Bookmark(db.Model):
    """General bookmarks model - for marking any resource"""
    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    resource_type = db.Column(db.String(50), default='job')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', back_populates='bookmarks')
    job = db.relationship('Job', back_populates='bookmarked_by')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'job_id', 'resource_type', name='unique_bookmark'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'job': self.job.to_dict() if self.job else None,
            'resource_type': self.resource_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Bookmark User:{self.user_id} Resource:{self.resource_type}:{self.job_id}>'
