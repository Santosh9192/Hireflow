"""
HireFlow AI - Validation Middleware
Input validation and sanitization utilities
"""

import re
from flask import request, jsonify
from functools import wraps


class ValidationMiddleware:
    """Input validation middleware"""

    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(email).strip()))

    @staticmethod
    def validate_required_fields(data, required_fields):
        """Validate required fields in request data"""
        missing = []
        for field in required_fields:
            if field not in data or (isinstance(data.get(field), str) and not data[field].strip()):
                missing.append(field)
        return missing

    @staticmethod
    def sanitize_string(value, max_length=None):
        """Sanitize string input"""
        if not value:
            return ''
        cleaned = str(value).strip()
        if max_length:
            cleaned = cleaned[:max_length]
        # Remove potentially dangerous characters
        cleaned = re.sub(r'[<>\'"]', '', cleaned)
        return cleaned

    @staticmethod
    def validate_json_body(f):
        """Decorator to validate JSON request body exists"""
        @wraps(f)
        def decorated(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Content-Type must be application/json'
                }), 400
            
            data = request.get_json(silent=True)
            if data is None:
                return jsonify({
                    'success': False,
                    'message': 'Invalid JSON body'
                }), 400
            
            return f(*args, **kwargs)
        return decorated

    @staticmethod
    def validate_file_upload(f):
        """Decorator to validate file upload exists"""
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'message': 'No file provided'
                }), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'message': 'No file selected'
                }), 400
            
            return f(*args, **kwargs)
        return decorated
