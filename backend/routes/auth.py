"""
HireFlow AI - Authentication Routes
Handles user authentication, registration, and password management
"""

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from models.user import User, BlacklistedToken, db
from models.candidate import CandidateProfile
from models.recruiter import RecruiterProfile
from middleware.auth import AuthMiddleware
from middleware.validation import ValidationMiddleware
from utils.helpers import success_response, error_response, validate_email, validate_password
from services.email_service import EmailService
from datetime import datetime, timezone, timedelta
import secrets

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        if not data:
            return error_response('Request body is required', 400)
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            return error_response(f'Missing fields: {", ".join(missing)}', 400)
        
        # Validate email
        if not validate_email(data['email']):
            return error_response('Invalid email format', 400)
        
        # Validate password
        is_valid, msg = validate_password(data['password'])
        if not is_valid:
            return error_response(msg, 400)
        
        # Validate role
        role = data['role'].lower()
        if role not in ['candidate', 'recruiter']:
            return error_response('Role must be candidate or recruiter', 400)
        
        # Check existing user
        if User.query.filter_by(email=data['email']).first():
            return error_response('Email already registered', 409)
        
        if User.query.filter_by(username=data.get('username', data['email'].split('@')[0])).first():
            return error_response('Username already taken', 409)
        
        # Create user
        user = User(
            email=data['email'].lower().strip(),
            username=data.get('username', data['email'].split('@')[0]),
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            phone=data.get('phone', ''),
            role=role
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()
        
        # Create role-specific profile
        if role == 'candidate':
            profile = CandidateProfile(user_id=user.id)
            db.session.add(profile)
        elif role == 'recruiter':
            profile = RecruiterProfile(user_id=user.id)
            db.session.add(profile)
        
        db.session.commit()
        
        # Generate tokens
        tokens = AuthMiddleware.generate_tokens(user)
        
        # Send welcome email (async)
        try:
            from flask import current_app
            mail = current_app.extensions.get('mail')
            if mail:
                email_service = EmailService(mail)
                email_service.send_welcome_email(user)
        except Exception as e:
            current_app.logger.warning(f'Failed to send welcome email: {str(e)}')
        
        return success_response(
            data={
                'user': user.to_dict(),
                'tokens': tokens
            },
            message='Registration successful',
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Registration failed: {str(e)}', 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return tokens"""
    try:
        data = request.get_json()
        if not data:
            return error_response('Request body is required', 400)
        
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            return error_response('Email and password are required', 400)
        
        # Find user by email or username
        user = User.query.filter(
            (User.email == email) | (User.username == email)
        ).first()
        
        if not user or not user.check_password(password):
            return error_response('Invalid email or password', 401)
        
        if not user.is_active:
            return error_response('Account is deactivated. Contact support.', 403)
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        # Generate tokens
        tokens = AuthMiddleware.generate_tokens(user)
        
        return success_response(
            data={
                'user': user.to_dict(),
                'tokens': tokens
            },
            message='Login successful'
        )
        
    except Exception as e:
        return error_response(f'Login failed: {str(e)}', 500)


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user and blacklist token"""
    try:
        jti = get_jwt()['jti']
        user_id = int(get_jwt_identity())
        expires = datetime.fromtimestamp(get_jwt()['exp'], tz=timezone.utc)
        
        # Blacklist token
        blacklisted = BlacklistedToken(
            jti=jti,
            token_type='access',
            user_id=user_id,
            expires_at=expires
        )
        db.session.add(blacklisted)
        db.session.commit()
        
        return success_response(message='Logged out successfully')
        
    except Exception as e:
        return error_response(f'Logout failed: {str(e)}', 500)


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return error_response('User not found or deactivated', 401)
        
        tokens = AuthMiddleware.generate_tokens(user)
        
        return success_response(data={'tokens': tokens}, message='Token refreshed')
        
    except Exception as e:
        return error_response(f'Token refresh failed: {str(e)}', 500)


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        profile_data = user.to_dict()
        
        # Add role-specific profile data
        if user.role.value == 'candidate' and user.candidate_profile:
            profile_data['candidate_profile'] = user.candidate_profile.to_dict()
        elif user.role.value == 'recruiter' and user.recruiter_profile:
            profile_data['recruiter_profile'] = user.recruiter_profile.to_dict()
        
        return success_response(data=profile_data)
        
    except Exception as e:
        return error_response(f'Failed to get profile: {str(e)}', 500)


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email"""
    try:
        data = request.get_json()
        if not data or not data.get('email'):
            return error_response('Email is required', 400)
        
        email = data['email'].lower().strip()
        user = User.query.filter_by(email=email).first()
        
        # Always return success to prevent email enumeration
        if not user:
            return success_response(
                message='If the email exists, a reset link has been sent'
            )
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db.session.commit()
        
        # Send email
        try:
            from flask import current_app
            mail = current_app.extensions.get('mail')
            if mail:
                email_service = EmailService(mail)
                email_service.send_password_reset_email(user, reset_token)
        except Exception as e:
            current_app.logger.warning(f'Failed to send password reset email: {str(e)}')
        
        return success_response(
            message='If the email exists, a reset link has been sent'
        )
        
    except Exception as e:
        return error_response(f'Failed to process request: {str(e)}', 500)


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token"""
    try:
        data = request.get_json()
        if not data or not data.get('token') or not data.get('password'):
            return error_response('Token and password are required', 400)
        
        # Validate password
        is_valid, msg = validate_password(data['password'])
        if not is_valid:
            return error_response(msg, 400)
        
        # Find user by reset token
        user = User.query.filter_by(
            reset_token=data['token']
        ).first()
        
        if not user:
            return error_response('Invalid or expired reset token', 400)
        
        if user.reset_token_expires < datetime.now(timezone.utc):
            return error_response('Reset token has expired', 400)
        
        # Update password
        user.set_password(data['password'])
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        
        return success_response(message='Password reset successful')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to reset password: {str(e)}', 500)


@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        data = request.get_json()
        if not data:
            return error_response('Request body is required', 400)
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'phone']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field].strip())
        
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return success_response(
            data={'user': user.to_dict()},
            message='Profile updated successfully'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update profile: {str(e)}', 500)


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        data = request.get_json()
        if not data or not data.get('current_password') or not data.get('new_password'):
            return error_response('Current password and new password are required', 400)
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return error_response('Current password is incorrect', 400)
        
        # Validate new password
        is_valid, msg = validate_password(data['new_password'])
        if not is_valid:
            return error_response(msg, 400)
        
        # Update password
        user.set_password(data['new_password'])
        db.session.commit()
        
        return success_response(message='Password changed successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to change password: {str(e)}', 500)
