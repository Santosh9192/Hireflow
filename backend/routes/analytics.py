"""
HireFlow AI - Analytics Routes
Endpoints for dashboard charts, statistics, and analytics
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, db
from models.job import Job
from models.application import Application
from models.candidate import CandidateProfile
from models.company import Company
from models.activity_log import ActivityLog
from utils.helpers import success_response, error_response
from datetime import datetime, timedelta
from sqlalchemy import func

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_analytics():
    """Get dashboard analytics based on user role"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        data = {}
        
        if user.role.value == 'candidate':
            data = get_candidate_analytics(user)
        elif user.role.value == 'recruiter':
            data = get_recruiter_analytics(user)
        elif user.role.value == 'admin':
            data = get_admin_analytics()
        
        return success_response(data=data)
        
    except Exception as e:
        return error_response(f'Failed to get analytics: {str(e)}', 500)


def get_candidate_analytics(user):
    """Get candidate-specific analytics"""
    profile = user.candidate_profile
    if not profile:
        return {}
    
    applications = Application.query.filter_by(
        candidate_id=profile.id
    ).all()
    
    # Application statistics
    total_apps = len(applications)
    status_counts = {}
    for app in applications:
        status_counts[app.status] = status_counts.get(app.status, 0) + 1
    
    # Application trend (last 30 days)
    # Use naive datetime to match MySQL DATETIME (no timezone info stored)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_apps = [a for a in applications if a.created_at and a.created_at.replace(tzinfo=None) >= thirty_days_ago]
    
    # Skill match insights
    from models.skill import CandidateSkill, Skill
    skills = CandidateSkill.query.filter_by(candidate_id=profile.id).all()
    
    # Interview statistics
    from models.interview import InterviewInvitation
    interviews = InterviewInvitation.query.filter_by(
        candidate_id=profile.id
    ).all()
    
    return {
        'total_applications': total_apps,
        'applications_by_status': status_counts,
        'recent_applications_count': len(recent_apps),
        'interviews_count': len(interviews),
        'pending_interviews': len([i for i in interviews if i.status == 'pending']),
        'skills_count': len(skills),
        'profile_completion': calculate_profile_completion(profile)
    }


def get_recruiter_analytics(user):
    """Get recruiter-specific analytics"""
    job_ids = [j.id for j in Job.query.filter_by(posted_by=user.id).all()]
    
    if not job_ids:
        return {
            'total_jobs': 0,
            'active_jobs': 0,
            'total_applications': 0,
            'applications_by_status': {},
            'jobs_by_category': [],
            'monthly_applications': []
        }
    
    # Job statistics
    total_jobs = len(job_ids)
    active_jobs = Job.query.filter(
        Job.id.in_(job_ids), Job.status == 'active'
    ).count()
    
    # Application statistics
    applications = Application.query.filter(
        Application.job_id.in_(job_ids)
    ).all()
    
    status_counts = {}
    for app in applications:
        status_counts[app.status] = status_counts.get(app.status, 0) + 1
    
    # Jobs by category
    jobs_by_category = db.session.query(
        Job.category, func.count(Job.id)
    ).filter(Job.id.in_(job_ids)).group_by(Job.category).all()
    
    # Monthly applications (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_apps = db.session.query(
        func.date_format(Application.created_at, '%Y-%m').label('month'),
        func.count(Application.id).label('count')
    ).filter(
        Application.job_id.in_(job_ids),
        Application.created_at >= six_months_ago
    ).group_by('month').order_by('month').all()
    
    return {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': len(applications),
        'applications_by_status': status_counts,
        'jobs_by_category': [
            {'category': cat, 'count': count}
            for cat, count in jobs_by_category if cat
        ],
        'monthly_applications': [
            {'month': m, 'count': c}
            for m, c in monthly_apps
        ]
    }


def get_admin_analytics():
    """Get admin-level system analytics"""
    # User statistics
    total_users = User.query.count()
    users_by_role = db.session.query(
        User.role, func.count(User.id)
    ).group_by(User.role).all()
    
    # New users this month
    first_of_month = datetime.utcnow().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    new_users_this_month = User.query.filter(
        User.created_at >= first_of_month
    ).count()
    
    # Job statistics
    total_jobs = Job.query.count()
    active_jobs = Job.query.filter(Job.status == 'active').count()
    jobs_by_status = db.session.query(
        Job.status, func.count(Job.id)
    ).group_by(Job.status).all()
    
    # Application statistics
    total_applications = Application.query.count()
    apps_by_status = db.session.query(
        Application.status, func.count(Application.id)
    ).group_by(Application.status).all()
    
    # Company statistics
    total_companies = Company.query.count()
    
    # Monthly growth (last 12 months)
    twelve_months_ago = datetime.utcnow() - timedelta(days=365)
    monthly_users = db.session.query(
        func.date_format(User.created_at, '%Y-%m').label('month'),
        func.count(User.id).label('count')
    ).filter(
        User.created_at >= twelve_months_ago
    ).group_by('month').order_by('month').all()
    
    return {
        'total_users': total_users,
        'users_by_role': {role: count for role, count in users_by_role},
        'new_users_this_month': new_users_this_month,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'jobs_by_status': {status: count for status, count in jobs_by_status},
        'total_applications': total_applications,
        'applications_by_status': {status: count for status, count in apps_by_status},
        'total_companies': total_companies,
        'monthly_growth': [
            {'month': m, 'users': c}
            for m, c in monthly_users
        ]
    }


def calculate_profile_completion(profile):
    """Calculate profile completion percentage"""
    if not profile:
        return 0
    
    fields = [
        'headline', 'bio', 'linkedin_url', 'github_url',
        'education', 'experience', 'projects', 'certifications',
        'languages', 'preferred_title'
    ]
    
    filled = sum(1 for f in fields if getattr(profile, f, None))
    return int((filled / len(fields)) * 100)
