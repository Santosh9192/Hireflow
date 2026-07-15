"""
HireFlow AI - Admin Routes
System administration and management features
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, db
from models.job import Job
from models.application import Application
from models.activity_log import ActivityLog
from models.company import Company
from models.notification import Notification
from utils.helpers import success_response, error_response, paginated_response
from datetime import datetime, timezone, timedelta

admin_bp = Blueprint('admin', __name__)


# Admin routes use @jwt_required decorator per-route for clarity
# Role verification is done inside each route handler


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get admin dashboard statistics"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role.value != 'admin':
            return error_response('Admin access required', 403)
        
        # System statistics
        total_users = User.query.count()
        total_candidates = User.query.filter(User.role == 'candidate').count()
        total_recruiters = User.query.filter(User.role == 'recruiter').count()
        total_active_users = User.query.filter(User.is_active == True).count()
        
        total_companies = Company.query.count()
        total_jobs = Job.query.count()
        total_active_jobs = Job.query.filter(Job.status == 'active').count()
        total_applications = Application.query.count()
        
        # Today's stats
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_users = User.query.filter(User.created_at >= today_start).count()
        today_jobs = Job.query.filter(Job.created_at >= today_start).count()
        today_applications = Application.query.filter(Application.created_at >= today_start).count()
        
        # Recent activities
        recent_activities = ActivityLog.query.order_by(
            ActivityLog.created_at.desc()
        ).limit(10).all()
        
        # Job by status
        job_statuses = db.session.query(
            Job.status, db.func.count(Job.id)
        ).group_by(Job.status).all()
        
        dashboard_data = {
            'total_users': total_users,
            'total_candidates': total_candidates,
            'total_recruiters': total_recruiters,
            'total_active_users': total_active_users,
            'total_companies': total_companies,
            'total_jobs': total_jobs,
            'total_active_jobs': total_active_jobs,
            'total_applications': total_applications,
            'today_users': today_users,
            'today_jobs': today_jobs,
            'today_applications': today_applications,
            'recent_activities': [a.to_dict() for a in recent_activities],
            'job_statuses': {status: count for status, count in job_statuses}
        }
        
        return success_response(data=dashboard_data)
        
    except Exception as e:
        return error_response(f'Failed to fetch dashboard: {str(e)}', 500)


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users with filters"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role.value != 'admin':
            return error_response('Admin access required', 403)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = User.query.order_by(User.created_at.desc())
        
        # Filters
        role = request.args.get('role')
        if role:
            query = query.filter(User.role == role)
        
        is_active = request.args.get('is_active')
        if is_active and is_active.lower() == 'true':
            query = query.filter(User.is_active == True)
        elif is_active and is_active.lower() == 'false':
            query = query.filter(User.is_active == False)
        
        search = request.args.get('search')
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                (User.first_name.ilike(search_term)) |
                (User.last_name.ilike(search_term)) |
                (User.email.ilike(search_term))
            )
        
        return paginated_response(query, page, per_page)
        
    except Exception as e:
        return error_response(f'Failed to fetch users: {str(e)}', 500)


@admin_bp.route('/users/<int:target_user_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def manage_user(target_user_id):
    """Manage specific user (GET, UPDATE, DELETE)"""
    try:
        admin_id = int(get_jwt_identity())
        admin = User.query.get(admin_id)
        
        if admin.role.value != 'admin':
            return error_response('Admin access required', 403)
        
        target_user = User.query.get(target_user_id)
        if not target_user:
            return error_response('User not found', 404)
        
        if request.method == 'GET':
            user_data = target_user.to_dict()
            
            # Add profile data
            if target_user.candidate_profile:
                user_data['profile'] = target_user.candidate_profile.to_dict()
            elif target_user.recruiter_profile:
                user_data['profile'] = target_user.recruiter_profile.to_dict()
            
            return success_response(data=user_data)
        
        elif request.method == 'PUT':
            data = request.get_json()
            if not data:
                return error_response('Request body is required', 400)
            
            # Admin can update user status and role
            if 'is_active' in data:
                target_user.is_active = bool(data['is_active'])
            
            if 'is_email_verified' in data:
                target_user.is_email_verified = bool(data['is_email_verified'])
            
            if 'role' in data and data['role'] in ['admin', 'recruiter', 'candidate']:
                target_user.role = data['role']
            
            target_user.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            
            return success_response(
                data=target_user.to_dict(),
                message='User updated successfully'
            )
        
        elif request.method == 'DELETE':
            # Don't allow deleting yourself
            if target_user.id == admin_id:
                return error_response('Cannot delete your own account', 400)
            
            db.session.delete(target_user)
            db.session.commit()
            
            return success_response(message='User deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to manage user: {str(e)}', 500)


@admin_bp.route('/jobs', methods=['GET'])
@jwt_required()
def get_jobs():
    """Get all jobs (admin view)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role.value != 'admin':
            return error_response('Admin access required', 403)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = Job.query.order_by(Job.created_at.desc())
        
        status = request.args.get('status')
        if status:
            query = query.filter(Job.status == status)
        
        search = request.args.get('search')
        if search:
            search_term = f'%{search}%'
            query = query.filter(Job.title.ilike(search_term))
        
        return paginated_response(query, page, per_page)
        
    except Exception as e:
        return error_response(f'Failed to fetch jobs: {str(e)}', 500)


@admin_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_logs():
    """Get activity logs"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role.value != 'admin':
            return error_response('Admin access required', 403)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        query = ActivityLog.query.order_by(ActivityLog.created_at.desc())
        
        # Filters
        action = request.args.get('action')
        if action:
            query = query.filter(ActivityLog.action == action)
        
        user_id_filter = request.args.get('user_id')
        if user_id_filter:
            query = query.filter(ActivityLog.user_id == user_id_filter)
        
        days = request.args.get('days', type=int)
        if days:
            since = datetime.now(timezone.utc) - timedelta(days=days)
            query = query.filter(ActivityLog.created_at >= since)
        
        return paginated_response(query, page, per_page)
        
    except Exception as e:
        return error_response(f'Failed to fetch logs: {str(e)}', 500)


@admin_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_reports():
    """Generate system reports"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role.value != 'admin':
            return error_response('Admin access required', 403)
        
        report_type = request.args.get('type', 'summary')
        
        if report_type == 'users':
            # Users by role and month
            users_by_role = db.session.query(
                User.role, db.func.count(User.id)
            ).group_by(User.role).all()
            
            return success_response(data={
                'users_by_role': {role: count for role, count in users_by_role}
            })
        
        elif report_type == 'jobs':
            # Jobs by status and month
            jobs_by_status = db.session.query(
                Job.status, db.func.count(Job.id)
            ).group_by(Job.status).all()
            
            return success_response(data={
                'jobs_by_status': {status: count for status, count in jobs_by_status}
            })
        
        elif report_type == 'applications':
            # Applications by status
            apps_by_status = db.session.query(
                Application.status, db.func.count(Application.id)
            ).group_by(Application.status).all()
            
            # Applications over time (last 30 days)
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            apps_over_time = db.session.query(
                db.func.date(Application.created_at),
                db.func.count(Application.id)
            ).filter(
                Application.created_at >= thirty_days_ago
            ).group_by(db.func.date(Application.created_at)).all()
            
            return success_response(data={
                'applications_by_status': {status: count for status, count in apps_by_status},
                'applications_over_time': [
                    {'date': str(d), 'count': c} for d, c in apps_over_time
                ]
            })
        
        else:
            # Summary report
            total_users = User.query.count()
            total_jobs = Job.query.count()
            total_apps = Application.query.count()
            active_jobs = Job.query.filter(Job.status == 'active').count()
            
            return success_response(data={
                'total_users': total_users,
                'total_jobs': total_jobs,
                'total_applications': total_apps,
                'active_jobs': active_jobs,
                'generated_at': datetime.now(timezone.utc).isoformat()
            })
        
    except Exception as e:
        return error_response(f'Failed to generate report: {str(e)}', 500)


@admin_bp.route('/notifications/broadcast', methods=['POST'])
@jwt_required()
def broadcast_notification():
    """Send broadcast notification to all users"""
    try:
        admin_id = int(get_jwt_identity())
        admin = User.query.get(admin_id)
        
        if admin.role.value != 'admin':
            return error_response('Admin access required', 403)
        
        data = request.get_json()
        if not data or not data.get('title') or not data.get('message'):
            return error_response('Title and message are required', 400)
        
        # Send to all users
        users = User.query.filter(User.is_active == True).all()
        notifications = []
        
        for target_user in users:
            notification = Notification(
                user_id=target_user.id,
                type='system',
                title=data['title'],
                message=data['message'],
                icon=data.get('icon', 'fa-bullhorn'),
                color=data.get('color', '#667eea')
            )
            notifications.append(notification)
        
        db.session.bulk_save_objects(notifications)
        db.session.commit()
        
        return success_response(
            message=f'Notification broadcast to {len(notifications)} users'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to broadcast: {str(e)}', 500)
