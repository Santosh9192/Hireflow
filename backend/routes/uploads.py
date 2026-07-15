"""
HireFlow AI - Upload Routes
Handles file uploads for profile photos and general files
"""

from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, db
from services.file_service import FileService
from utils.helpers import success_response, error_response
import os

uploads_bp = Blueprint('uploads', __name__)
file_service = FileService()


@uploads_bp.route('/profile-photo', methods=['POST'])
@jwt_required()
def upload_profile_photo():
    """Upload profile photo"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        if 'file' not in request.files:
            return error_response('No file provided', 400)
        
        file = request.files['file']
        if file.filename == '':
            return error_response('No file selected', 400)
        
        # Validate image type
        if not file_service.validate_image_type(file.filename):
            return error_response('Only image files (PNG, JPG, JPEG, GIF) are allowed', 400)
        
        # Save file
        result = file_service.save_file(file, subfolder='photos')
        if result.get('error'):
            return error_response(result['error'], 400)
        
        # Delete old photo if exists
        if user.profile_photo:
            file_service.delete_file(user.profile_photo)
        
        # Update user profile photo
        user.profile_photo = result['file_path']
        db.session.commit()
        
        return success_response(
            data={
                'profile_photo': file_service.get_file_url(result['file_path']),
                'filename': result['filename']
            },
            message='Profile photo uploaded successfully'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to upload photo: {str(e)}', 500)


@uploads_bp.route('/profile-photo', methods=['DELETE'])
@jwt_required()
def delete_profile_photo():
    """Delete profile photo"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        if user.profile_photo:
            file_service.delete_file(user.profile_photo)
            user.profile_photo = None
            db.session.commit()
        
        return success_response(message='Profile photo deleted')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete photo: {str(e)}', 500)


@uploads_bp.route('/company-logo', methods=['POST'])
@jwt_required()
def upload_company_logo():
    """Upload company logo"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role.value != 'recruiter':
            return error_response('Only recruiters can upload company logos', 403)
        
        if 'file' not in request.files:
            return error_response('No file provided', 400)
        
        file = request.files['file']
        if not file_service.validate_image_type(file.filename):
            return error_response('Only image files are allowed', 400)
        
        result = file_service.save_file(file, subfolder='logos')
        if result.get('error'):
            return error_response(result['error'], 400)
        
        return success_response(
            data={
                'logo_url': file_service.get_file_url(result['file_path']),
                'filename': result['filename']
            },
            message='Logo uploaded successfully'
        )
        
    except Exception as e:
        return error_response(f'Failed to upload logo: {str(e)}', 500)
