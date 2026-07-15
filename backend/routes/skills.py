"""
HireFlow AI - Skills Routes
Manages skills taxonomy and search
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import db
from models.skill import Skill
from utils.helpers import success_response, error_response

skills_bp = Blueprint('skills', __name__)


@skills_bp.route('', methods=['GET'])
def list_skills():
    """List all skills with optional category filter"""
    try:
        category = request.args.get('category')
        search = request.args.get('search', '')
        
        query = Skill.query.order_by(Skill.name)
        
        if category:
            query = query.filter(Skill.category == category)
        
        if search:
            query = query.filter(Skill.name.ilike(f'%{search}%'))
        
        skills = query.limit(100).all()
        return success_response(data=[s.to_dict() for s in skills])
        
    except Exception as e:
        return error_response(f'Failed to fetch skills: {str(e)}', 500)


@skills_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get skill categories"""
    try:
        categories = db.session.query(
            Skill.category, db.func.count(Skill.id)
        ).group_by(Skill.category).all()
        
        return success_response(data=[
            {'category': cat, 'count': count}
            for cat, count in categories if cat
        ])
        
    except Exception as e:
        return error_response(f'Failed to fetch categories: {str(e)}', 500)


@skills_bp.route('/top', methods=['GET'])
def get_top_skills():
    """Get most common/trending skills"""
    try:
        from models.user import User
        from models.candidate import CandidateProfile
        from models.skill import CandidateSkill
        
        # Get skills ranked by number of candidates
        top_skills = db.session.query(
            Skill.name, Skill.category,
            db.func.count(CandidateSkill.id).label('candidate_count')
        ).join(
            CandidateSkill, Skill.id == CandidateSkill.skill_id
        ).group_by(Skill.id).order_by(
            db.func.count(CandidateSkill.id).desc()
        ).limit(30).all()
        
        return success_response(data=[
            {
                'name': name,
                'category': category,
                'candidate_count': count
            }
            for name, category, count in top_skills
        ])
        
    except Exception as e:
        return error_response(f'Failed to fetch top skills: {str(e)}', 500)


@skills_bp.route('', methods=['POST'])
@jwt_required()
def create_skill():
    """Create a new skill (Admin only)"""
    try:
        from flask_jwt_extended import get_jwt_identity
        from models.user import User
        
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role.value != 'admin':
            return error_response('Only admins can create skills', 403)
        
        data = request.get_json()
        if not data or not data.get('name'):
            return error_response('Skill name is required', 400)
        
        name = data['name'].strip()
        existing = Skill.query.filter_by(name=name).first()
        if existing:
            return error_response('Skill already exists', 409)
        
        skill = Skill(
            name=name,
            category=data.get('category', 'Other'),
            is_technical=data.get('is_technical', True)
        )
        
        db.session.add(skill)
        db.session.commit()
        
        return success_response(
            data=skill.to_dict(),
            message='Skill created successfully',
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create skill: {str(e)}', 500)
