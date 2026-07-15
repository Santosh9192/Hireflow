"""
HireFlow AI - Activity Log Model
Tracks all user activities for audit trail and analytics
"""

from datetime import datetime, timezone
from models.user import db


class ActivityLog(db.Model):
    """User activity log for audit trail"""
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Activity Details
    action = db.Column(db.String(100), nullable=False, index=True)
    # login, logout, register, create_job, update_job, delete_job, apply_job, etc.
    resource_type = db.Column(db.String(50), nullable=True)  # job, application, resume, user, etc.
    resource_id = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Additional Data
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    extra_data = db.Column(db.JSON, nullable=True)  # Additional context
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    user = db.relationship('User', back_populates='activity_logs')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': self.user.to_public_dict() if self.user else None,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'description': self.description,
            'ip_address': self.ip_address,
            'extra_data': self.extra_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<ActivityLog {self.action} (User:{self.user_id})>'
