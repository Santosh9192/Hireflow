"""
HireFlow AI - Applications Routes
Handles job applications, tracking, and management
"""

from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
import csv
import io
from models.user import User, db
from models.job import Job
from models.application import Application
from models.candidate import CandidateProfile
from models.notification import Notification
from utils.helpers import success_response, error_response, paginated_response
from datetime import datetime, timezone

applications_bp = Blueprint('applications', __name__)


@applications_bp.route('', methods=['POST'])
@jwt_required()
def apply():
    """Apply for a job"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role.value != 'candidate':
            return error_response('Only candidates can apply for jobs', 403)
        
        data = request.get_json()
        if not data or not data.get('job_id'):
            return error_response('Job ID is required', 400)
        
        job = Job.query.get(data['job_id'])
        if not job:
            return error_response('Job not found', 404)
        
        if job.status != 'active':
            return error_response('This job is no longer accepting applications', 400)
        
        # Check if already applied
        existing = Application.query.filter_by(
            job_id=job.id,
            candidate_id=user.candidate_profile.id
        ).first()
        
        if existing:
            return error_response('You have already applied for this job', 409)
        
        # Create application
        application = Application(
            job_id=job.id,
            candidate_id=user.candidate_profile.id,
            resume_id=data.get('resume_id'),
            cover_letter=data.get('cover_letter', ''),
            notes=data.get('notes', '')
        )
        
        db.session.add(application)
        
        # Update job application count
        job.applications_count = (job.applications_count or 0) + 1
        
        # Create notification for job poster
        notification = Notification(
            user_id=job.posted_by,
            type='application_received',
            title=f'New application for {job.title}',
            message=f'{user.first_name} {user.last_name} has applied for {job.title}',
            icon='fa-paper-plane',
            color='#667eea',
            reference_type='application',
            reference_id=application.id
        )
        db.session.add(notification)
        
        db.session.commit()
        
        return success_response(
            data=application.to_dict(),
            message='Application submitted successfully',
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to submit application: {str(e)}', 500)


@applications_bp.route('', methods=['GET'])
@jwt_required()
def get_applications():
    """Get user's applications (candidate) or received applications (recruiter)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if user.role.value == 'candidate':
            # Get candidate's applications
            query = Application.query.filter_by(
                candidate_id=user.candidate_profile.id
            ).order_by(Application.created_at.desc())
            
        elif user.role.value == 'recruiter':
            # Get applications for recruiter's jobs
            job_ids = [job.id for job in Job.query.filter_by(posted_by=user_id).all()]
            query = Application.query.filter(
                Application.job_id.in_(job_ids)
            ).order_by(Application.created_at.desc()) if job_ids else Application.query.filter(False)
            
        elif user.role.value == 'admin':
            query = Application.query.order_by(Application.created_at.desc())
        else:
            return error_response('Invalid role', 403)
        
        # Status filter
        status = request.args.get('status')
        if status:
            query = query.filter(Application.status == status)
        
        # Job filter
        job_id = request.args.get('job_id')
        if job_id:
            query = query.filter(Application.job_id == job_id)
        
        return paginated_response(query, page, per_page)
        
    except Exception as e:
        return error_response(f'Failed to fetch applications: {str(e)}', 500)


@applications_bp.route('/<int:application_id>', methods=['GET'])
@jwt_required()
def get_application(application_id):
    """Get application details"""
    try:
        application = Application.query.get(application_id)
        if not application:
            return error_response('Application not found', 404)
        
        return success_response(data=application.to_dict())
        
    except Exception as e:
        return error_response(f'Failed to fetch application: {str(e)}', 500)


@applications_bp.route('/<int:application_id>/status', methods=['PUT'])
@jwt_required()
def update_application_status(application_id):
    """Update application status (Recruiter only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role.value not in ['recruiter', 'admin']:
            return error_response('Only recruiters can update application status', 403)
        
        application = Application.query.get(application_id)
        if not application:
            return error_response('Application not found', 404)
        
        data = request.get_json()
        if not data or not data.get('status'):
            return error_response('Status is required', 400)
        
        new_status = data['status']
        valid_statuses = ['pending', 'reviewing', 'shortlisted', 'rejected', 'offered', 'accepted']
        
        if new_status not in valid_statuses:
            return error_response(f'Invalid status. Must be one of: {", ".join(valid_statuses)}', 400)
        
        # Update status and timestamp
        application.status = new_status
        timestamp = datetime.now(timezone.utc)
        
        status_timestamps = {
            'reviewing': 'reviewed_at',
            'shortlisted': 'shortlisted_at',
            'rejected': 'rejected_at',
            'offered': 'offered_at',
            'accepted': 'accepted_at'
        }
        
        if new_status in status_timestamps:
            setattr(application, status_timestamps[new_status], timestamp)
        
        if new_status == 'rejected' and data.get('rejection_reason'):
            application.rejection_reason = data['rejection_reason']
        
        application.updated_at = timestamp
        
        # Notify candidate
        candidate_user = User.query.join(CandidateProfile).filter(
            CandidateProfile.id == application.candidate_id
        ).first()
        
        if candidate_user:
            notification = Notification(
                user_id=candidate_user.id,
                type='application_status',
                title=f'Application {new_status}',
                message=f'Your application for {application.job.title} has been {new_status}',
                icon='fa-bell',
                color='#667eea',
                reference_type='application',
                reference_id=application.id
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return success_response(
            data=application.to_dict(),
            message=f'Application status updated to {new_status}'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update application status: {str(e)}', 500)


@applications_bp.route('/<int:application_id>/notes', methods=['PUT'])
@jwt_required()
def update_application_notes(application_id):
    """Update recruiter notes on application"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role.value not in ['recruiter', 'admin']:
            return error_response('Only recruiters can add notes', 403)
        
        application = Application.query.get(application_id)
        if not application:
            return error_response('Application not found', 404)
        
        data = request.get_json()
        if not data:
            return error_response('Request body is required', 400)
        
        application.recruiter_notes = data.get('notes', '')
        db.session.commit()
        
        return success_response(
            data=application.to_dict(),
            message='Notes updated'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update notes: {str(e)}', 500)


@applications_bp.route('/<int:application_id>/withdraw', methods=['POST'])
@jwt_required()
def withdraw_application(application_id):
    """Withdraw an application (Candidate only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        application = Application.query.get(application_id)
        if not application:
            return error_response('Application not found', 404)
        
        if not user.candidate_profile or application.candidate_id != user.candidate_profile.id:
            return error_response('Not authorized to withdraw this application', 403)
        
        application.status = 'withdrawn'
        application.withdrawn_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return success_response(
            data=application.to_dict(),
            message='Application withdrawn'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to withdraw application: {str(e)}', 500)


@applications_bp.route('/export', methods=['GET'])
@jwt_required()
def export_applications():
    """Export applications as CSV"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role.value == 'candidate':
            apps = Application.query.filter_by(
                candidate_id=user.candidate_profile.id
            ).order_by(Application.created_at.desc()).all()
        elif user.role.value == 'recruiter':
            job_ids = [j.id for j in Job.query.filter_by(posted_by=user_id).all()]
            apps = Application.query.filter(Application.job_id.in_(job_ids)).all() if job_ids else []
        else:
            apps = Application.query.order_by(Application.created_at.desc()).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Job Title', 'Company', 'Status', 'Applied Date', 'Candidate Name', 'Candidate Email'])
        
        for app in apps:
            writer.writerow([
                app.job.title if app.job else 'N/A',
                app.job.company.name if app.job and app.job.company else 'N/A',
                app.status,
                app.created_at.strftime('%Y-%m-%d') if app.created_at else 'N/A',
                app.candidate.user.full_name if app.candidate and app.candidate.user else 'N/A',
                app.candidate.user.email if app.candidate and app.candidate.user else 'N/A'
            ])
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment;filename=applications.csv'}
        )
    except Exception as e:
        return error_response(f'Export failed: {str(e)}', 500)


@applications_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_application_stats():
    """Get application statistics for the current user"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role.value == 'candidate':
            candidate_id = user.candidate_profile.id if user.candidate_profile else None
            if not candidate_id:
                return success_response(data={'total': 0, 'by_status': {}})
            
            apps = Application.query.filter_by(candidate_id=candidate_id).all()
            
        elif user.role.value == 'recruiter':
            job_ids = [j.id for j in Job.query.filter_by(posted_by=user_id).all()]
            apps = Application.query.filter(Application.job_id.in_(job_ids)).all() if job_ids else []
        else:
            apps = Application.query.all()
        
        stats = {
            'total': len(apps),
            'by_status': {}
        }
        
        for app in apps:
            status = app.status
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        
        return success_response(data=stats)
        
    except Exception as e:
        return error_response(f'Failed to fetch stats: {str(e)}', 500)
