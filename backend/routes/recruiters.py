"""
HireFlow AI - Recruiter Routes
Handles recruiter-specific operations including company management and analytics
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, db
from models.recruiter import RecruiterProfile
from models.company import Company
from models.job import Job
from models.application import Application
from models.interview import InterviewInvitation
from models.notification import Notification
from models.candidate import CandidateProfile
from utils.helpers import success_response, error_response, paginated_response
from datetime import datetime, timezone, date

recruiters_bp = Blueprint('recruiters', __name__)


@recruiters_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get recruiter dashboard statistics"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role.value != 'recruiter':
            return error_response('Access denied', 403)
        
        # Get recruiter's jobs
        jobs = Job.query.filter_by(posted_by=user_id).all()
        job_ids = [j.id for j in jobs]
        
        # Statistics
        total_jobs = len(jobs)
        active_jobs = len([j for j in jobs if j.status == 'active'])
        total_applications = Application.query.filter(
            Application.job_id.in_(job_ids)
        ).count() if job_ids else 0
        
        # Applications by status
        pending_count = Application.query.filter(
            Application.job_id.in_(job_ids),
            Application.status == 'pending'
        ).count() if job_ids else 0
        
        shortlisted_count = Application.query.filter(
            Application.job_id.in_(job_ids),
            Application.status == 'shortlisted'
        ).count() if job_ids else 0
        
        # Recent applications
        recent_applications = []
        if job_ids:
            recent = Application.query.filter(
                Application.job_id.in_(job_ids)
            ).order_by(Application.created_at.desc()).limit(5).all()
            recent_applications = [a.to_dict() for a in recent]
        
        # Interview count
        interview_count = InterviewInvitation.query.join(
            Application, InterviewInvitation.application_id == Application.id
        ).filter(
            Application.job_id.in_(job_ids)
        ).count() if job_ids else 0
        
        dashboard_data = {
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'total_applications': total_applications,
            'pending_applications': pending_count,
            'shortlisted_applications': shortlisted_count,
            'interview_count': interview_count,
            'recent_applications': recent_applications,
            'jobs': [j.to_dict() for j in jobs[:10]]
        }
        
        return success_response(data=dashboard_data)
        
    except Exception as e:
        return error_response(f'Failed to fetch dashboard: {str(e)}', 500)


@recruiters_bp.route('/company', methods=['GET', 'PUT'])
@jwt_required()
def manage_company():
    """Get or update company profile"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role.value != 'recruiter':
            return error_response('Access denied', 403)
        
        profile = user.recruiter_profile
        if not profile:
            return error_response('Recruiter profile not found', 404)
        
        if request.method == 'GET':
            if profile.company:
                return success_response(data=profile.company.to_dict())
            return success_response(data=None, message='No company profile')
        
        # PUT - Update company
        data = request.get_json()
        if not data:
            return error_response('Request body is required', 400)
        
        if profile.company:
            company = profile.company
        else:
            company = Company(name=data.get('name', ''))
            db.session.add(company)
            db.session.flush()
            profile.company_id = company.id
        
        # Update company fields
        allowed_fields = [
            'name', 'description', 'website', 'logo', 'industry',
            'company_size', 'founded_year', 'headquarters', 'locations',
            'culture', 'benefits', 'social_links'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(company, field, data[field])
        
        company.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return success_response(
            data=company.to_dict(),
            message='Company profile updated'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to manage company: {str(e)}', 500)


@recruiters_bp.route('/jobs', methods=['GET'])
@jwt_required()
def get_my_jobs():
    """Get recruiter's job postings"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role.value != 'recruiter':
            return error_response('Access denied', 403)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Job.query.filter_by(posted_by=user_id)\
            .order_by(Job.created_at.desc())
        
        status = request.args.get('status')
        if status:
            query = query.filter(Job.status == status)
        
        return paginated_response(query, page, per_page)
        
    except Exception as e:
        return error_response(f'Failed to fetch jobs: {str(e)}', 500)


@recruiters_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    """Get applications for recruiter's jobs"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role.value != 'recruiter':
            return error_response('Access denied', 403)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        job_ids = [j.id for j in Job.query.filter_by(posted_by=user_id).all()]
        
        if not job_ids:
            return success_response(data=[], meta={'total': 0, 'page': page})
        
        query = Application.query.filter(
            Application.job_id.in_(job_ids)
        ).order_by(Application.created_at.desc())
        
        # Filters
        status = request.args.get('status')
        if status:
            query = query.filter(Application.status == status)
        
        job_id = request.args.get('job_id')
        if job_id:
            query = query.filter(Application.job_id == job_id)
        
        return paginated_response(query, page, per_page)
        
    except Exception as e:
        return error_response(f'Failed to fetch applications: {str(e)}', 500)


@recruiters_bp.route('/interviews', methods=['GET', 'POST'])
@jwt_required()
def manage_interviews():
    """List or create interview invitations"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role.value != 'recruiter':
            return error_response('Access denied', 403)
        
        if request.method == 'GET':
            interviews = InterviewInvitation.query.filter_by(
                recruiter_id=user_id
            ).order_by(InterviewInvitation.created_at.desc()).all()
            
            return success_response(data=[i.to_dict() for i in interviews])
        
        # POST - Create interview
        data = request.get_json()
        if not data:
            return error_response('Request body is required', 400)
        
        required = ['application_id', 'title', 'proposed_date', 'proposed_time']
        missing = [f for f in required if not data.get(f)]
        if missing:
            return error_response(f'Missing fields: {", ".join(missing)}', 400)
        
        application = Application.query.get(data['application_id'])
        if not application:
            return error_response('Application not found', 404)
        
        try:
            interview_date = datetime.strptime(data['proposed_date'], '%Y-%m-%d').date()
            interview_time = datetime.strptime(data['proposed_time'], '%H:%M').time()
        except ValueError:
            return error_response('Invalid date or time format. Use YYYY-MM-DD and HH:MM', 400)
        
        interview = InterviewInvitation(
            application_id=application.id,
            recruiter_id=user_id,
            candidate_id=application.candidate_id,
            title=data['title'],
            description=data.get('description', ''),
            interview_type=data.get('interview_type', 'video'),
            location=data.get('location', ''),
            meeting_link=data.get('meeting_link', ''),
            proposed_date=interview_date,
            proposed_time=interview_time,
            duration_minutes=data.get('duration_minutes', 60),
            timezone=data.get('timezone', 'UTC')
        )
        
        db.session.add(interview)
        
        # Update application status
        application.status = 'interviewed'
        application.interviewed_at = datetime.now(timezone.utc)
        
        # Notify candidate
        notification = Notification(
            user_id=application.candidate.user_id,
            type='interview_invitation',
            title='Interview Invitation',
            message=f'You have been invited for an interview: {interview.title}',
            icon='fa-calendar',
            color='#667eea',
            reference_type='interview',
            reference_id=interview.id
        )
        db.session.add(notification)
        
        db.session.commit()
        
        return success_response(
            data=interview.to_dict(),
            message='Interview invitation sent',
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to manage interviews: {str(e)}', 500)


@recruiters_bp.route('/candidates/search', methods=['GET'])
@jwt_required()
def search_candidates():
    """Search for candidates (Recruiter feature)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
        query = CandidateProfile.query.filter(
            CandidateProfile.is_open_to_work == True
        )
        
        search = request.args.get('search')
        if search:
            search_term = f'%{search}%'
            query = query.join(User).filter(
                (User.first_name.ilike(search_term)) |
                (User.last_name.ilike(search_term)) |
                (CandidateProfile.headline.ilike(search_term)) |
                (CandidateProfile.bio.ilike(search_term))
            )
        
        skills = request.args.get('skills')
        if skills:
            from models.skill import Skill, CandidateSkill
            skill_list = [s.strip() for s in skills.split(',')]
            skill_ids = Skill.query.filter(
                Skill.name.in_(skill_list)
            ).with_entities(Skill.id).all()
            skill_ids = [s[0] for s in skill_ids]
            
            if skill_ids:
                candidate_ids = CandidateSkill.query.filter(
                    CandidateSkill.skill_id.in_(skill_ids)
                ).with_entities(CandidateSkill.candidate_id).distinct().all()
                candidate_ids = [c[0] for c in candidate_ids]
                query = query.filter(CandidateProfile.id.in_(candidate_ids))
        
        query = query.order_by(CandidateProfile.updated_at.desc())
        
        return paginated_response(query, page, per_page)
        
    except Exception as e:
        return error_response(f'Failed to search candidates: {str(e)}', 500)


@recruiters_bp.route('/interviews/<int:interview_id>', methods=['PUT'])
@jwt_required()
def update_interview(interview_id):
    """Update interview invitation status"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        interview = InterviewInvitation.query.get(interview_id)
        if not interview:
            return error_response('Interview not found', 404)
        
        if interview.recruiter_id != user_id and user.role.value != 'admin':
            return error_response('Not authorized', 403)
        
        data = request.get_json()
        if not data:
            return error_response('Request body is required', 400)
        
        if 'status' in data:
            valid_statuses = ['confirmed', 'cancelled', 'completed']
            if data['status'] in valid_statuses:
                interview.status = data['status']
        
        interview.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return success_response(
            data=interview.to_dict(),
            message='Interview updated'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update interview: {str(e)}', 500)
