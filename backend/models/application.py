"""
HireFlow AI - Application Model
Tracks job applications from candidates
"""

from datetime import datetime, timezone
from models.user import db


class Application(db.Model):
    """Job application model"""
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate_profiles.id', ondelete='CASCADE'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id', ondelete='SET NULL'), nullable=True)
    
    # Application Details
    status = db.Column(db.String(50), default='pending', index=True)
    # pending, reviewing, shortlisted, interviewed, rejected, offered, accepted, withdrawn
    cover_letter = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    recruiter_notes = db.Column(db.Text, nullable=True)  # Private notes from recruiter
    
    # Status Timeline
    applied_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reviewed_at = db.Column(db.DateTime, nullable=True)
    shortlisted_at = db.Column(db.DateTime, nullable=True)
    interviewed_at = db.Column(db.DateTime, nullable=True)
    rejected_at = db.Column(db.DateTime, nullable=True)
    offered_at = db.Column(db.DateTime, nullable=True)
    accepted_at = db.Column(db.DateTime, nullable=True)
    withdrawn_at = db.Column(db.DateTime, nullable=True)
    
    # Rejection Details
    rejection_reason = db.Column(db.String(500), nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    job = db.relationship('Job', back_populates='applications')
    candidate = db.relationship('CandidateProfile', back_populates='applications')
    resume = db.relationship('Resume', foreign_keys=[resume_id])
    interview = db.relationship('InterviewInvitation', back_populates='application', uselist=False, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'job': self.job.to_dict() if self.job else None,
            'candidate_id': self.candidate_id,
            'candidate': self.candidate.to_dict() if self.candidate else None,
            'resume_id': self.resume_id,
            'resume': self.resume.to_dict() if self.resume else None,
            'status': self.status,
            'cover_letter': self.cover_letter,
            'notes': self.notes,
            'recruiter_notes': self.recruiter_notes,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'shortlisted_at': self.shortlisted_at.isoformat() if self.shortlisted_at else None,
            'interviewed_at': self.interviewed_at.isoformat() if self.interviewed_at else None,
            'rejected_at': self.rejected_at.isoformat() if self.rejected_at else None,
            'offered_at': self.offered_at.isoformat() if self.offered_at else None,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None,
            'rejection_reason': self.rejection_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Application Job:{self.job_id} Candidate:{self.candidate_id} ({self.status})>'
