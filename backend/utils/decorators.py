"""
HireFlow AI - Decorators
Custom decorators for authentication, authorization, and utilities
"""

from functools import wraps
from flask import request, jsonify, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.user import User, BlacklistedToken


def role_required(*roles):
    """Decorator to check user role(s) for route access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                identity = get_jwt_identity()
                # Convert to int (PyJWT >=2.13 requires string 'sub' claim)
                user_id = int(identity) if identity is not None else None
                
                if user_id is None:
                    return jsonify({'success': False, 'message': 'Invalid token identity'}), 401
                
                user = User.query.get(user_id)
                if not user:
                    return jsonify({'success': False, 'message': 'User not found'}), 404
                
                if user.role.value not in roles:
                    return jsonify({
                        'success': False,
                        'message': f'Access denied. Required role(s): {", ".join(roles)}'
                    }), 403
                
                g.current_user = user
                g.user_role = user.role.value
                
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'Invalid token identity'}), 401
            except Exception as e:
                return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def api_key_required(f):
    """Decorator to require API key for route access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'success': False, 'message': 'API key is required'}), 401
        
        # Verify API key (implementation depends on your API key storage)
        # For now, basic check
        if len(api_key) < 16:
            return jsonify({'success': False, 'message': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function


def validate_json(*required_fields):
    """Decorator to validate JSON request body fields"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Request must be JSON',
                    'errors': {'content-type': 'application/json required'}
                }), 400
            
            data = request.get_json(silent=True)
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'Invalid JSON body'
                }), 400
            
            missing_fields = []
            for field in required_fields:
                if field not in data or (isinstance(data.get(field), str) and not data[field].strip()):
                    missing_fields.append(field)
            
            if missing_fields:
                return jsonify({
                    'success': False,
                    'message': f'Missing required fields: {", ".join(missing_fields)}',
                    'errors': {field: f'{field} is required' for field in missing_fields}
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def log_activity(f):
    """Decorator to log user activity"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from models.activity_log import db, ActivityLog
        from datetime import datetime, timezone
        
        result = f(*args, **kwargs)
        
        try:
            user_id = None
            if hasattr(g, 'current_user'):
                user_id = g.current_user.id
            
            if user_id:
                activity = ActivityLog(
                    user_id=user_id,
                    action=request.endpoint or 'unknown',
                    resource_type=request.path.split('/')[1] if request.path else None,
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string[:500] if request.user_agent else None,
                    created_at=datetime.now(timezone.utc)
                )
                db.session.add(activity)
                db.session.commit()
        except Exception:
            db.session.rollback()
        
        return result
    return decorated_function


def rate_limit(f):
    """Simple rate limiting decorator (can be replaced with Flask-Limiter)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Implement redis/memory rate limiting here
        # For now, pass through
        return f(*args, **kwargs)
    return decorated_function
