"""
HireFlow AI - Interview Invitation Model
Manages interview scheduling and invitations
"""

from datetime import datetime, timezone
from models.user import db


class InterviewInvitation(db.Model):
    """Interview invitation/scheduling model"""
    __tablename__ = 'interview_invitations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate_profiles.id', ondelete='CASCADE'), nullable=False)
    
    # Interview Details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    interview_type = db.Column(db.String(50), default='video')  # phone, video, in-person, technical
    location = db.Column(db.String(500), nullable=True)  # For in-person interviews
    meeting_link = db.Column(db.String(500), nullable=True)  # For video interviews
    
    # Scheduling
    proposed_date = db.Column(db.Date, nullable=False)
    proposed_time = db.Column(db.Time, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    timezone = db.Column(db.String(50), default='UTC')
    
    # Status
    status = db.Column(db.String(50), default='pending', index=True)
    # pending, confirmed, rescheduled, cancelled, completed
    candidate_message = db.Column(db.Text, nullable=True)
    
    # Rescheduling
    rescheduled_date = db.Column(db.Date, nullable=True)
    rescheduled_time = db.Column(db.Time, nullable=True)
    reschedule_reason = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    application = db.relationship('Application', back_populates='interview')
    recruiter = db.relationship('User', foreign_keys=[recruiter_id])
    candidate = db.relationship('CandidateProfile', back_populates='interview_invitations')

    def to_dict(self):
        return {
            'id': self.id,
            'application_id': self.application_id,
            'application': self.application.to_dict() if self.application else None,
            'recruiter_id': self.recruiter_id,
            'recruiter': self.recruiter.to_public_dict() if self.recruiter else None,
            'candidate_id': self.candidate_id,
            'candidate': self.candidate.to_dict() if self.candidate else None,
            'title': self.title,
            'description': self.description,
            'interview_type': self.interview_type,
            'location': self.location,
            'meeting_link': self.meeting_link,
            'proposed_date': self.proposed_date.isoformat() if self.proposed_date else None,
            'proposed_time': self.proposed_time.strftime('%H:%M') if self.proposed_time else None,
            'duration_minutes': self.duration_minutes,
            'timezone': self.timezone,
            'status': self.status,
            'candidate_message': self.candidate_message,
            'rescheduled_date': self.rescheduled_date.isoformat() if self.rescheduled_date else None,
            'rescheduled_time': self.rescheduled_time.strftime('%H:%M') if self.rescheduled_time else None,
            'reschedule_reason': self.reschedule_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<InterviewInvitation App:{self.application_id} ({self.status})>'
