"""
HireFlow AI - Skill Models
Manages skills taxonomy and candidate skill associations
"""

from datetime import datetime, timezone
from models.user import db


class Skill(db.Model):
    """Master skills taxonomy"""
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(100), nullable=True)  # Programming, Design, Marketing, etc.
    is_technical = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'is_technical': self.is_technical
        }

    def __repr__(self):
        return f'<Skill {self.name}>'


class CandidateSkill(db.Model):
    """Many-to-many relationship between candidates and skills"""
    __tablename__ = 'candidate_skills'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate_profiles.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    proficiency = db.Column(db.Integer, default=3)  # 1-5 rating
    years_experience = db.Column(db.Integer, nullable=True)
    is_top_skill = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    candidate = db.relationship('CandidateProfile', back_populates='skills')
    skill = db.relationship('Skill')

    def to_dict(self):
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'skill_id': self.skill_id,
            'skill': self.skill.to_dict() if self.skill else None,
            'proficiency': self.proficiency,
            'years_experience': self.years_experience,
            'is_top_skill': self.is_top_skill
        }

    def __repr__(self):
        return f'<CandidateSkill Candidate:{self.candidate_id} Skill:{self.skill_id}>'
