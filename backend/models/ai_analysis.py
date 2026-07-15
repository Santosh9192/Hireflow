"""
HireFlow AI - AI Analysis Model
Stores AI-generated analysis results for resumes and job matches
"""

from datetime import datetime, timezone
from models.user import db


class AIAnalysis(db.Model):
    """AI analysis results model"""
    __tablename__ = 'ai_analyses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate_profiles.id', ondelete='CASCADE'), nullable=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id', ondelete='CASCADE'), nullable=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=True)
    
    # Analysis Type
    analysis_type = db.Column(db.String(50), nullable=False, index=True)
    # resume_parse, resume_summary, skill_extract, ats_score, job_match,
    # interview_questions, cover_letter, professional_summary, skill_gap
    
    # Analysis Content
    input_text = db.Column(db.Text, nullable=True)
    output_text = db.Column(db.Text, nullable=True)
    structured_data = db.Column(db.JSON, nullable=True)
    
    # Scores
    score = db.Column(db.Integer, nullable=True)
    confidence = db.Column(db.Float, nullable=True)
    
    # Status
    status = db.Column(db.String(20), default='completed')  # pending, processing, completed, failed
    error_message = db.Column(db.Text, nullable=True)
    processing_time = db.Column(db.Float, nullable=True)  # In seconds
    
    model_used = db.Column(db.String(100), default='gemini-pro')
    tokens_used = db.Column(db.Integer, nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    candidate = db.relationship('CandidateProfile', back_populates='ai_analyses')
    resume = db.relationship('Resume', foreign_keys=[resume_id])
    job = db.relationship('Job', foreign_keys=[job_id])

    def to_dict(self):
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'resume_id': self.resume_id,
            'job_id': self.job_id,
            'analysis_type': self.analysis_type,
            'output_text': self.output_text[:500] + '...' if self.output_text and len(self.output_text) > 500 else self.output_text,
            'structured_data': self.structured_data,
            'score': self.score,
            'confidence': self.confidence,
            'status': self.status,
            'error_message': self.error_message,
            'processing_time': self.processing_time,
            'model_used': self.model_used,
            'tokens_used': self.tokens_used,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<AIAnalysis {self.analysis_type} (Score:{self.score})>'
