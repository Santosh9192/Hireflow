"""
HireFlow AI - Notification Routes
Manages user notifications and preferences
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, db
from models.notification import Notification
from utils.helpers import success_response, error_response, paginated_response

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get user notifications"""
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = Notification.query.filter_by(user_id=user_id)\
            .order_by(Notification.created_at.desc())
        
        unread_only = request.args.get('unread_only')
        if unread_only and unread_only.lower() == 'true':
            query = query.filter_by(is_read=False)
        
        return paginated_response(query, page, per_page)
        
    except Exception as e:
        return error_response(f'Failed to fetch notifications: {str(e)}', 500)


@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get unread notification count"""
    try:
        user_id = int(get_jwt_identity())
        count = Notification.query.filter_by(
            user_id=user_id, is_read=False
        ).count()
        
        return success_response(data={'unread_count': count})
        
    except Exception as e:
        return error_response(f'Failed to get count: {str(e)}', 500)


@notifications_bp.route('/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_as_read(notification_id):
    """Mark notification as read"""
    try:
        user_id = int(get_jwt_identity())
        notification = Notification.query.get(notification_id)
        
        if not notification:
            return error_response('Notification not found', 404)
        
        if notification.user_id != user_id:
            return error_response('Not authorized', 403)
        
        notification.mark_as_read()
        db.session.commit()
        
        return success_response(
            data=notification.to_dict(),
            message='Marked as read'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to mark as read: {str(e)}', 500)


@notifications_bp.route('/read-all', methods=['POST'])
@jwt_required()
def mark_all_as_read():
    """Mark all notifications as read"""
    try:
        user_id = int(get_jwt_identity())
        from datetime import datetime, timezone
        
        Notification.query.filter_by(
            user_id=user_id, is_read=False
        ).update({
            'is_read': True,
            'read_at': datetime.now(timezone.utc)
        })
        
        db.session.commit()
        
        return success_response(message='All notifications marked as read')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to mark all as read: {str(e)}', 500)


@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """Delete a notification"""
    try:
        user_id = int(get_jwt_identity())
        notification = Notification.query.get(notification_id)
        
        if not notification:
            return error_response('Notification not found', 404)
        
        if notification.user_id != user_id:
            return error_response('Not authorized', 403)
        
        db.session.delete(notification)
        db.session.commit()
        
        return success_response(message='Notification deleted')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete: {str(e)}', 500)


@notifications_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_all():
    """Clear all notifications for user"""
    try:
        user_id = int(get_jwt_identity())
        Notification.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
        return success_response(message='All notifications cleared')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to clear: {str(e)}', 500)
