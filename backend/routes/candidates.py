"""
HireFlow AI - Candidate Routes
Manages candidate profiles, skills, education, and experience
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, db
from models.candidate import CandidateProfile
from models.skill import Skill, CandidateSkill
from models.application import Application
from models.interview import InterviewInvitation
from utils.helpers import success_response, error_response, paginated_response
from datetime import datetime, timezone

candidates_bp = Blueprint('candidates', __name__)


@candidates_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get candidate profile"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role.value != 'candidate':
            return error_response('Only candidates can access this profile', 403)
        
        if not user.candidate_profile:
            return error_response('Profile not found', 404)
        
        return success_response(data=user.candidate_profile.to_dict())
        
    except Exception as e:
        return error_response(f'Failed to fetch profile: {str(e)}', 500)


@candidates_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update candidate profile"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role.value != 'candidate':
            return error_response('Only candidates can update this profile', 403)
        
        data = request.get_json()
        if not data:
            return error_response('Request body is required', 400)
        
        profile = user.candidate_profile
        if not profile:
            return error_response('Profile not found', 404)
        
        # Update allowed fields
        allowed_fields = [
            'headline', 'bio', 'linkedin_url', 'github_url', 'portfolio_url', 'website_url',
            'education', 'experience', 'projects', 'certifications', 'languages',
            'preferred_title', 'preferred_locations', 'preferred_salary_min', 'preferred_salary_max',
            'preferred_employment_type', 'preferred_work_mode', 'is_open_to_work', 'notice_period'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(profile, field, data[field])
        
        profile.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return success_response(
            data=profile.to_dict(),
            message='Profile updated successfully'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update profile: {str(e)}', 500)


@candidates_bp.route('/skills', methods=['GET'])
@jwt_required()
def get_skills():
    """Get candidate skills"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user.candidate_profile:
            return error_response('Profile not found', 404)
        
        skills = CandidateSkill.query.filter_by(
            candidate_id=user.candidate_profile.id
        ).all()
        
        return success_response(data=[s.to_dict() for s in skills])
        
    except Exception as e:
        return error_response(f'Failed to fetch skills: {str(e)}', 500)


@candidates_bp.route('/skills', methods=['PUT'])
@jwt_required()
def update_skills():
    """Update candidate skills"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role.value != 'candidate':
            return error_response('Only candidates can update skills', 403)
        
        data = request.get_json()
        if not data or not data.get('skills'):
            return error_response('Skills data is required', 400)
        
        profile = user.candidate_profile
        if not profile:
            return error_response('Profile not found', 404)
        
        # Remove existing skills
        CandidateSkill.query.filter_by(candidate_id=profile.id).delete()
        
        # Add new skills
        for skill_data in data['skills']:
            skill_name = skill_data.get('name', '').strip()
            if not skill_name:
                continue
            
            # Find or create skill
            skill = Skill.query.filter_by(name=skill_name).first()
            if not skill:
                skill = Skill(
                    name=skill_name,
                    category=skill_data.get('category', 'Other'),
                    is_technical=skill_data.get('is_technical', True)
                )
                db.session.add(skill)
                db.session.flush()
            
            candidate_skill = CandidateSkill(
                candidate_id=profile.id,
                skill_id=skill.id,
                proficiency=skill_data.get('proficiency', 3),
                years_experience=skill_data.get('years_experience'),
                is_top_skill=skill_data.get('is_top_skill', False)
            )
            db.session.add(candidate_skill)
        
        db.session.commit()
        
        # Return updated skills
        skills = CandidateSkill.query.filter_by(candidate_id=profile.id).all()
        return success_response(
            data=[s.to_dict() for s in skills],
            message='Skills updated successfully'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update skills: {str(e)}', 500)


@candidates_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    """Get candidate's applications"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user.candidate_profile:
            return error_response('Profile not found', 404)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Application.query.filter_by(
            candidate_id=user.candidate_profile.id
        ).order_by(Application.created_at.desc())
        
        status = request.args.get('status')
        if status:
            query = query.filter(Application.status == status)
        
        return paginated_response(query, page, per_page)
        
    except Exception as e:
        return error_response(f'Failed to fetch applications: {str(e)}', 500)


@candidates_bp.route('/interviews', methods=['GET'])
@jwt_required()
def get_interviews():
    """Get candidate's interview invitations"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user.candidate_profile:
            return error_response('Profile not found', 404)
        
        interviews = InterviewInvitation.query.filter_by(
            candidate_id=user.candidate_profile.id
        ).order_by(InterviewInvitation.created_at.desc()).all()
        
        return success_response(data=[i.to_dict() for i in interviews])
        
    except Exception as e:
        return error_response(f'Failed to fetch interviews: {str(e)}', 500)


@candidates_bp.route('/search', methods=['GET'])
def search_candidates():
    """Search candidates (Recruiter/Admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
        query = CandidateProfile.query.filter(
            CandidateProfile.is_open_to_work == True
        )
        
        # Search by name or headline
        search = request.args.get('search')
        if search:
            search_term = f'%{search}%'
            query = query.join(User).filter(
                (User.first_name.ilike(search_term)) |
                (User.last_name.ilike(search_term)) |
                (CandidateProfile.headline.ilike(search_term))
            )
        
        # Skills filter
        skills = request.args.get('skills')
        if skills:
            skill_list = [s.strip() for s in skills.split(',')]
            # Find candidates with these skills
            skill_ids = Skill.query.filter(Skill.name.in_(skill_list)).with_entities(Skill.id).all()
            skill_ids = [s[0] for s in skill_ids]
            if skill_ids:
                candidate_ids = CandidateSkill.query.filter(
                    CandidateSkill.skill_id.in_(skill_ids)
                ).with_entities(CandidateSkill.candidate_id).distinct().all()
                candidate_ids = [c[0] for c in candidate_ids]
                query = query.filter(CandidateProfile.id.in_(candidate_ids))
        
        # Location filter
        location = request.args.get('location')
        if location:
            query = query.filter(
                CandidateProfile.preferred_locations.ilike(f'%{location}%')
            )
        
        query = query.order_by(CandidateProfile.updated_at.desc())
        
        return paginated_response(query, page, per_page)
        
    except Exception as e:
        return error_response(f'Failed to search candidates: {str(e)}', 500)


@candidates_bp.route('/<int:candidate_id>', methods=['GET'])
def get_candidate(candidate_id):
    """Get public candidate profile"""
    try:
        profile = CandidateProfile.query.get(candidate_id)
        if not profile:
            return error_response('Candidate not found', 404)
        
        data = profile.to_dict()
        # Remove sensitive info for non-authenticated users
        if data.get('user'):
            data['user'] = profile.user.to_public_dict()
        
        return success_response(data=data)
        
    except Exception as e:
        return error_response(f'Failed to fetch candidate: {str(e)}', 500)
