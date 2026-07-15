"""
HireFlow AI - Utility Helpers
Common utility functions used across the application
"""

import re
import json
import math
from datetime import datetime, timezone
from flask import jsonify
from werkzeug.utils import secure_filename


def success_response(data=None, message='Success', status_code=200, meta=None):
    """Generate a success response"""
    response = {
        'success': True,
        'message': message,
        'data': data
    }
    if meta:
        response['meta'] = meta
    return jsonify(response), status_code


def error_response(message='Error', status_code=400, errors=None):
    """Generate an error response"""
    response = {
        'success': False,
        'message': message
    }
    if errors:
        response['errors'] = errors
    return jsonify(response), status_code


def paginated_response(query, page, per_page, serialize=True):
    """Generate a paginated response from a SQLAlchemy query"""
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    items = pagination.items
    if serialize:
        items = [item.to_dict() for item in items]
    
    total_pages = math.ceil(pagination.total / per_page) if per_page > 0 else 0
    
    return success_response(
        data=items,
        meta={
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': total_pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    )


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, 'Password must be at least 8 characters'
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain an uppercase letter'
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain a lowercase letter'
    if not re.search(r'[0-9]', password):
        return False, 'Password must contain a number'
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, 'Password must contain a special character'
    return True, 'Password is valid'


def validate_phone(phone):
    """Validate phone number format"""
    pattern = r'^\+?1?\d{10,15}$'
    return re.match(pattern, phone.replace('-', '').replace(' ', '')) is not None


def allowed_file(filename, allowed_extensions=None):
    """Check if file extension is allowed"""
    if allowed_extensions is None:
        allowed_extensions = {'pdf', 'docx', 'doc', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions


def format_file_size(size_bytes):
    """Format file size in human-readable format"""
    if not size_bytes:
        return '0 B'
    size_names = ['B', 'KB', 'MB', 'GB']
    i = int(math.floor(math.log(size_bytes, 1024))) if size_bytes > 0 else 0
    i = min(i, len(size_names) - 1)
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f'{s} {size_names[i]}'


def generate_slug(text):
    """Generate URL-friendly slug from text"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:200]


def parse_date(date_string):
    """Parse date string to datetime object"""
    if not date_string:
        return None
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%d %H:%M:%S',
        '%m/%d/%Y',
        '%d/%m/%Y'
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    return None


def calculate_experience_years(experience_list):
    """Calculate total years of experience from experience list"""
    if not experience_list:
        return 0
    total_days = 0
    for exp in experience_list:
        start = parse_date(exp.get('start_date', ''))
        end = parse_date(exp.get('end_date', '')) or datetime.now(timezone.utc)
        if start and end:
            total_days += (end - start).days
    return round(total_days / 365.25, 1)


def sanitize_html(text):
    """Sanitize HTML content (basic XSS prevention)"""
    if not text:
        return text
    import bleach
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                    'ul', 'ol', 'li', 'a', 'span', 'div', 'b', 'i']
    allowed_attrs = {'a': ['href', 'title', 'target'], 'span': ['class'], 'div': ['class']}
    return bleach.clean(text, tags=allowed_tags, attributes=allowed_attrs, strip=True)


def truncate_text(text, max_length=200):
    """Truncate text to specified length"""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + '...'
