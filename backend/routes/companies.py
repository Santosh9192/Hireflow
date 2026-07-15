"""
HireFlow AI - Company Routes
Handles company profiles and information
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, db
from models.company import Company
from models.job import Job
from utils.helpers import success_response, error_response, paginated_response

companies_bp = Blueprint('companies', __name__)


@companies_bp.route('', methods=['GET'])
def list_companies():
    """List all companies"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
        query = Company.query.order_by(Company.name.asc())
        
        # Filters
        industry = request.args.get('industry')
        if industry:
            query = query.filter(Company.industry == industry)
        
        search = request.args.get('search')
        if search:
            search_term = f'%{search}%'
            query = query.filter(Company.name.ilike(search_term))
        
        return paginated_response(query, page, per_page)
        
    except Exception as e:
        return error_response(f'Failed to fetch companies: {str(e)}', 500)


@companies_bp.route('/<int:company_id>', methods=['GET'])
def get_company(company_id):
    """Get company details"""
    try:
        company = Company.query.get(company_id)
        if not company:
            return error_response('Company not found', 404)
        
        data = company.to_dict()
        
        # Get active jobs for this company
        jobs = Job.query.filter_by(
            company_id=company_id, status='active'
        ).order_by(Job.created_at.desc()).limit(10).all()
        
        data['active_jobs'] = [j.to_dict() for j in jobs]
        data['active_jobs_count'] = len(jobs)
        
        return success_response(data=data)
        
    except Exception as e:
        return error_response(f'Failed to fetch company: {str(e)}', 500)


@companies_bp.route('/<int:company_id>', methods=['PUT'])
@jwt_required()
def update_company(company_id):
    """Update company profile (Admin/Recruiter)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role.value not in ['admin', 'recruiter']:
            return error_response('Not authorized', 403)
        
        company = Company.query.get(company_id)
        if not company:
            return error_response('Company not found', 404)
        
        # Check if recruiter belongs to this company
        if (user.role.value == 'recruiter' and 
            user.recruiter_profile and 
            user.recruiter_profile.company_id != company_id):
            return error_response('Not authorized to update this company', 403)
        
        data = request.get_json()
        if not data:
            return error_response('Request body is required', 400)
        
        allowed_fields = [
            'name', 'description', 'website', 'logo', 'industry',
            'company_size', 'founded_year', 'headquarters', 'locations',
            'culture', 'benefits', 'social_links'
        ]
        
        from datetime import datetime, timezone
        for field in allowed_fields:
            if field in data:
                setattr(company, field, data[field])
        
        company.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return success_response(
            data=company.to_dict(),
            message='Company updated successfully'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update company: {str(e)}', 500)


@companies_bp.route('/industries', methods=['GET'])
def get_industries():
    """Get list of industries"""
    try:
        industries = db.session.query(Company.industry).distinct().all()
        industries = [i[0] for i in industries if i[0]]
        industries.sort()
        
        return success_response(data=industries)
        
    except Exception as e:
        return error_response(f'Failed to fetch industries: {str(e)}', 500)
