"""
HireFlow AI - Authentication Middleware
Handles JWT token verification and user authentication
"""

from functools import wraps
from flask import request, jsonify, g
from flask_jwt_extended import (
    verify_jwt_in_request, get_jwt_identity, get_jwt,
    create_access_token, create_refresh_token
)
from models.user import User, BlacklistedToken
from datetime import datetime, timezone, timedelta


class AuthMiddleware:
    """Authentication middleware for JWT token management"""

    @staticmethod
    def token_required(f):
        """Decorator to require valid JWT token"""
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                verify_jwt_in_request()
                jwt_data = get_jwt()
                jti = jwt_data.get('jti')
                
                # Check if token is blacklisted
                blacklisted = BlacklistedToken.query.filter_by(jti=jti).first()
                if blacklisted:
                    return jsonify({
                        'success': False,
                        'message': 'Token has been revoked'
                    }), 401
                
                user_id = int(get_jwt_identity())
                user = User.query.get(user_id)
                
                if not user or not user.is_active:
                    return jsonify({
                        'success': False,
                        'message': 'User not found or deactivated'
                    }), 401
                
                g.current_user = user
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': 'Invalid or expired token'
                }), 401
            
            return f(*args, **kwargs)
        return decorated

    @staticmethod
    def optional_auth(f):
        """Decorator that optionally authenticates user"""
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                verify_jwt_in_request(optional=True)
                user_id = int(get_jwt_identity())
                if user_id:
                    user = User.query.get(user_id)
                    if user and user.is_active:
                        g.current_user = user
            except Exception:
                pass
            
            return f(*args, **kwargs)
        return decorated

    @staticmethod
    def blacklist_token(jti):
        """Blacklist a JWT token"""
        from flask import current_app
        from models.user import db
        
        try:
            token = BlacklistedToken.query.filter_by(jti=jti).first()
            if not token:
                return False
            
            db.session.delete(token)
            db.session.commit()
            return True
        except Exception as e:
            current_app.logger.error(f'Error blacklisting token: {str(e)}')
            return False

    @staticmethod
    def generate_tokens(user):
        """Generate access and refresh tokens"""
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'role': user.role.value if hasattr(user.role, 'value') else user.role,
                'email': user.email,
                'username': user.username
            }
        )
        
        refresh_token = create_refresh_token(
            identity=user.id,
            additional_claims={'type': 'refresh'}
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': 86400
        }
