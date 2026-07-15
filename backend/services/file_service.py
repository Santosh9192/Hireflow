"""
HireFlow AI - File Service
Handles file uploads, validation, and management
"""

import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
from utils.helpers import allowed_file


class FileService:
    """Service for file upload and management"""

    @staticmethod
    def get_upload_folder(subfolder=''):
        """Get upload folder path"""
        base_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
        folder = os.path.join(base_folder, subfolder)
        os.makedirs(folder, exist_ok=True)
        return folder

    @staticmethod
    def save_file(file, subfolder='', allowed_types=None):
        """
        Save uploaded file to disk
        Returns: dict with filename, path, original_name, size, type
        """
        if not file or not file.filename:
            return {'error': 'No file provided'}
        
        # Validate file type
        if allowed_types is None:
            allowed_types = {'pdf', 'docx', 'doc', 'png', 'jpg', 'jpeg', 'gif'}
        
        if not allowed_file(file.filename, allowed_types):
            return {'error': f'File type not allowed. Allowed: {", ".join(allowed_types)}'}
        
        # Validate file size (16MB max)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
        if file_size > max_size:
            return {'error': f'File too large. Maximum size: {max_size // (1024*1024)}MB'}
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        unique_name = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{extension}"
        
        # Save file
        upload_folder = FileService.get_upload_folder(subfolder)
        file_path = os.path.join(upload_folder, unique_name)
        file.save(file_path)
        
        return {
            'filename': unique_name,
            'original_filename': original_filename,
            'file_path': os.path.join(subfolder, unique_name).replace('\\', '/'),
            'full_path': file_path,
            'file_size': file_size,
            'file_type': extension,
            'success': True
        }

    @staticmethod
    def delete_file(file_path):
        """Delete a file from disk"""
        if not file_path:
            return False
        
        full_path = os.path.join(
            current_app.root_path,
            current_app.config.get('UPLOAD_FOLDER', 'static/uploads'),
            file_path
        )
        
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                return True
            except OSError:
                return False
        return False

    @staticmethod
    def get_file_url(file_path):
        """Get the URL for a file"""
        if not file_path:
            return None
        return f"/static/uploads/{file_path}"

    @staticmethod
    def validate_file_type(filename):
        """Validate file type for resume uploads"""
        allowed = {'pdf', 'docx', 'doc'}
        return allowed_file(filename, allowed)

    @staticmethod
    def validate_image_type(filename):
        """Validate file type for image uploads"""
        allowed = {'png', 'jpg', 'jpeg', 'gif'}
        return allowed_file(filename, allowed)
