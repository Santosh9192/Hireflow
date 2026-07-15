"""
HireFlow AI - Jobs Routes
Handles job posting CRUD and listing operations
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, db
from models.job import Job
from models.company import Company
from models.saved_job import SavedJob
from models.saved_job import Bookmark
from utils.helpers import success_response, error_response, paginated_response
from datetime import datetime, timezone

jobs_bp = Blueprint('jobs', __name__)


@jobs_bp.route('', methods=['GET'])
def list_jobs():
    """List all active jobs with filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
        query = Job.query.filter(Job.status == 'active')
        
        # Filters
        category = request.args.get('category')
        if category:
            query = query.filter(Job.category == category)
        
        employment_type = request.args.get('employment_type')
        if employment_type:
            query = query.filter(Job.employment_type == employment_type)
        
        work_mode = request.args.get('work_mode')
        if work_mode:
            query = query.filter(Job.work_mode == work_mode)
        
        experience_level = request.args.get('experience_level')
        if experience_level:
            query = query.filter(Job.experience_level == experience_level)
        
        location = request.args.get('location')
        if location:
            query = query.filter(
                (Job.location.ilike(f'%{location}%')) |
                (Job.city.ilike(f'%{location}%')) |
                (Job.state.ilike(f'%{location}%'))
            )
        
        is_remote = request.args.get('is_remote')
        if is_remote and is_remote.lower() == 'true':
            query = query.filter(Job.is_remote == True)
        
        salary_min = request.args.get('salary_min', type=int)
        if salary_min:
            query = query.filter(Job.salary_max >= salary_min)
        
        salary_max = request.args.get('salary_max', type=int)
        if salary_max:
            query = query.filter(Job.salary_min <= salary_max)
        
        # Search
        search = request.args.get('search')
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                (Job.title.ilike(search_term)) |
                (Job.description.ilike(search_term))
            )
        
        # Skills filter
        skills = request.args.get('skills')
        if skills:
            skill_list = [s.strip() for s in skills.split(',')]
            for skill in skill_list:
                query = query.filter(Job.required_skills.ilike(f'%{skill}%'))
        
        # Sort
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        sort_column = getattr(Job, sort_by, Job.created_at)
        if sort_order == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
        
        return paginated_response(query, page, per_page)
        
    except Exception as e:
        return error_response(f'Failed to fetch jobs: {str(e)}', 500)


@jobs_bp.route('/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """Get job details"""
    try:
        job = Job.query.get(job_id)
        if not job:
            return error_response('Job not found', 404)
        
        # Increment view count
        job.views_count = (job.views_count or 0) + 1
        db.session.commit()
        
        return success_response(data=job.to_dict())
        
    except Exception as e:
        return error_response(f'Failed to fetch job: {str(e)}', 500)


@jobs_bp.route('', methods=['POST'])
@jwt_required()
def create_job():
    """Create a new job posting (Recruiter only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role.value != 'recruiter':
            return error_response('Only recruiters can post jobs', 403)
        
        data = request.get_json()
        if not data:
            return error_response('Request body is required', 400)
        
        required_fields = ['title', 'description']
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            return error_response(f'Missing fields: {", ".join(missing)}', 400)
        
        company_id = data.get('company_id')
        if not company_id and user.recruiter_profile:
            company_id = user.recruiter_profile.company_id
        
        job = Job(
            company_id=company_id,
            posted_by=user_id,
            title=data['title'].strip(),
            description=data['description'].strip(),
            requirements=data.get('requirements', ''),
            responsibilities=data.get('responsibilities', ''),
            benefits=data.get('benefits', ''),
            category=data.get('category', ''),
            subcategory=data.get('subcategory', ''),
            employment_type=data.get('employment_type', 'full-time'),
            work_mode=data.get('work_mode', 'on-site'),
            experience_level=data.get('experience_level', 'mid'),
            min_experience=data.get('min_experience'),
            max_experience=data.get('max_experience'),
            location=data.get('location', ''),
            city=data.get('city', ''),
            state=data.get('state', ''),
            country=data.get('country', 'United States'),
            is_remote=data.get('is_remote', False),
            salary_min=data.get('salary_min'),
            salary_max=data.get('salary_max'),
            salary_currency=data.get('salary_currency', 'USD'),
            salary_period=data.get('salary_period', 'yearly'),
            show_salary=data.get('show_salary', True),
            required_skills=data.get('required_skills', ''),
            preferred_skills=data.get('preferred_skills', ''),
            status=data.get('status', 'active'),
            is_featured=data.get('is_featured', False),
            is_urgent=data.get('is_urgent', False),
            positions_available=data.get('positions_available', 1),
            published_at=datetime.now(timezone.utc) if data.get('status') == 'active' else None
        )
        
        db.session.add(job)
        db.session.commit()
        
        return success_response(
            data=job.to_dict(),
            message='Job posted successfully',
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create job: {str(e)}', 500)


@jobs_bp.route('/<int:job_id>', methods=['PUT'])
@jwt_required()
def update_job(job_id):
    """Update a job posting"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        job = Job.query.get(job_id)
        if not job:
            return error_response('Job not found', 404)
        
        if job.posted_by != user_id and user.role.value != 'admin':
            return error_response('Not authorized to update this job', 403)
        
        data = request.get_json()
        if not data:
            return error_response('Request body is required', 400)
        
        # Update allowed fields
        allowed_fields = [
            'title', 'description', 'requirements', 'responsibilities', 'benefits',
            'category', 'subcategory', 'employment_type', 'work_mode', 'experience_level',
            'min_experience', 'max_experience', 'location', 'city', 'state', 'country',
            'is_remote', 'salary_min', 'salary_max', 'salary_currency', 'salary_period',
            'show_salary', 'required_skills', 'preferred_skills', 'status',
            'is_featured', 'is_urgent', 'positions_available'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(job, field, data[field])
        
        job.updated_at = datetime.now(timezone.utc)
        if data.get('status') == 'active' and not job.published_at:
            job.published_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return success_response(
            data=job.to_dict(),
            message='Job updated successfully'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update job: {str(e)}', 500)


@jobs_bp.route('/<int:job_id>', methods=['DELETE'])
@jwt_required()
def delete_job(job_id):
    """Delete a job posting"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        job = Job.query.get(job_id)
        if not job:
            return error_response('Job not found', 404)
        
        if job.posted_by != user_id and user.role.value != 'admin':
            return error_response('Not authorized to delete this job', 403)
        
        db.session.delete(job)
        db.session.commit()
        
        return success_response(message='Job deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete job: {str(e)}', 500)


@jobs_bp.route('/<int:job_id>/save', methods=['POST'])
@jwt_required()
def save_job(job_id):
    """Save/bookmark a job for later"""
    try:
        user_id = int(get_jwt_identity())
        
        job = Job.query.get(job_id)
        if not job:
            return error_response('Job not found', 404)
        
        existing = SavedJob.query.filter_by(user_id=user_id, job_id=job_id).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            return success_response(data={'saved': False}, message='Job unsaved')
        
        saved = SavedJob(user_id=user_id, job_id=job_id)
        db.session.add(saved)
        db.session.commit()
        
        return success_response(data={'saved': True}, message='Job saved')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to save job: {str(e)}', 500)


@jobs_bp.route('/saved', methods=['GET'])
@jwt_required()
def get_saved_jobs():
    """Get user's saved jobs"""
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
        query = SavedJob.query.filter_by(user_id=user_id)\
            .order_by(SavedJob.created_at.desc())
        
        return paginated_response(query, page, per_page)
        
    except Exception as e:
        return error_response(f'Failed to fetch saved jobs: {str(e)}', 500)


@jobs_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get job categories and counts"""
    try:
        from sqlalchemy import func
        
        categories = db.session.query(
            Job.category,
            func.count(Job.id).label('count')
        ).filter(
            Job.status == 'active',
            Job.category != None,
            Job.category != ''
        ).group_by(Job.category).all()
        
        return success_response(data=[
            {'category': cat, 'count': count}
            for cat, count in categories
        ])
        
    except Exception as e:
        return error_response(f'Failed to fetch categories: {str(e)}', 500)
