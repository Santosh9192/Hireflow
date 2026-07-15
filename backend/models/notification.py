"""
HireFlow AI - Notification Model
Manages user notifications and alerts
"""

from datetime import datetime, timezone
from models.user import db


class Notification(db.Model):
    """User notification model"""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Notification Content
    type = db.Column(db.String(50), nullable=False, index=True)
    # application_received, application_status, interview_invitation, job_alert, system, message
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(20), nullable=True)  # For UI styling
    
    # Reference
    reference_type = db.Column(db.String(50), nullable=True)  # application, job, interview, etc.
    reference_id = db.Column(db.Integer, nullable=True)
    reference_url = db.Column(db.String(500), nullable=True)
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    is_email_sent = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    read_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    user = db.relationship('User', back_populates='notifications')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'icon': self.icon,
            'color': self.color,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'reference_url': self.reference_url,
            'is_read': self.is_read,
            'is_archived': self.is_archived,
            'is_email_sent': self.is_email_sent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }

    def mark_as_read(self):
        self.is_read = True
        self.read_at = datetime.now(timezone.utc)

    def __repr__(self):
        return f'<Notification {self.type}: {self.title[:50]}>'
