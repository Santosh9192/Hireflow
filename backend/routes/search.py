"""
HireFlow AI - Search Routes
Global search functionality across jobs, candidates, companies, and skills
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, db
from models.job import Job
from models.candidate import CandidateProfile
from models.company import Company
from models.skill import Skill
from utils.helpers import success_response, error_response

search_bp = Blueprint('search', __name__)


@search_bp.route('', methods=['GET'])
def global_search():
    """Global search across all resources"""
    try:
        query = request.args.get('q', '').strip()
        if not query or len(query) < 2:
            return success_response(data={
                'jobs': [],
                'candidates': [],
                'companies': [],
                'skills': []
            })
        
        search_term = f'%{query}%'
        limit = min(request.args.get('limit', 10, type=int), 50)
        
        results = {}
        
        # Search jobs
        jobs = Job.query.filter(
            Job.status == 'active',
            (Job.title.ilike(search_term) |
             Job.description.ilike(search_term) |
             Job.location.ilike(search_term) |
             Job.category.ilike(search_term))
        ).limit(limit).all()
        results['jobs'] = [j.to_dict() for j in jobs]
        
        # Search candidates (public profiles)
        candidates = CandidateProfile.query.join(User).filter(
            CandidateProfile.is_open_to_work == True,
            (User.first_name.ilike(search_term) |
             User.last_name.ilike(search_term) |
             CandidateProfile.headline.ilike(search_term))
        ).limit(limit).all()
        results['candidates'] = [c.to_dict() for c in candidates]
        
        # Search companies
        companies = Company.query.filter(
            Company.name.ilike(search_term) |
            Company.industry.ilike(search_term) |
            Company.headquarters.ilike(search_term)
        ).limit(limit).all()
        results['companies'] = [c.to_short_dict() for c in companies]
        
        # Search skills
        skills = Skill.query.filter(
            Skill.name.ilike(search_term)
        ).limit(limit).all()
        results['skills'] = [s.to_dict() for s in skills]
        
        return success_response(data=results)
        
    except Exception as e:
        return error_response(f'Search failed: {str(e)}', 500)


@search_bp.route('/jobs', methods=['GET'])
def search_jobs():
    """Advanced job search"""
    try:
        from routes.jobs import list_jobs
        return list_jobs()
    except Exception as e:
        return error_response(f'Job search failed: {str(e)}', 500)


@search_bp.route('/candidates', methods=['GET'])
def search_candidates():
    """Search candidate profiles"""
    try:
        query = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
        search_query = CandidateProfile.query.filter(
            CandidateProfile.is_open_to_work == True
        )
        
        if query:
            search_term = f'%{query}%'
            search_query = search_query.join(User).filter(
                (User.first_name.ilike(search_term)) |
                (User.last_name.ilike(search_term)) |
                (CandidateProfile.headline.ilike(search_term)) |
                (CandidateProfile.bio.ilike(search_term))
            )
        
        # Location filter
        location = request.args.get('location')
        if location:
            search_query = search_query.filter(
                CandidateProfile.preferred_locations.ilike(f'%{location}%')
            )
        
        search_query = search_query.order_by(
            CandidateProfile.updated_at.desc()
        )
        
        from utils.helpers import paginated_response
        return paginated_response(search_query, page, per_page)
        
    except Exception as e:
        return error_response(f'Candidate search failed: {str(e)}', 500)


@search_bp.route('/skills', methods=['GET'])
def search_skills():
    """Search skills"""
    try:
        query = request.args.get('q', '').strip()
        if not query or len(query) < 1:
            categories = db.session.query(
                Skill.category, db.func.count(Skill.id)
            ).group_by(Skill.category).all()
            return success_response(data={
                'categories': [
                    {'category': cat, 'count': count}
                    for cat, count in categories if cat
                ]
            })
        
        skills = Skill.query.filter(
            Skill.name.ilike(f'%{query}%')
        ).order_by(Skill.name).limit(20).all()
        
        return success_response(data=[s.to_dict() for s in skills])
        
    except Exception as e:
        return error_response(f'Skill search failed: {str(e)}', 500)


@search_bp.route('/suggestions', methods=['GET'])
def get_search_suggestions():
    """Get search suggestions for autocomplete"""
    try:
        query = request.args.get('q', '').strip()
        if not query or len(query) < 2:
            return success_response(data=[])
        
        search_term = f'%{query}%'
        suggestions = set()
        
        # Job title suggestions
        job_titles = Job.query.filter(
            Job.status == 'active',
            Job.title.ilike(search_term)
        ).with_entities(Job.title).distinct().limit(5).all()
        suggestions.update(t[0] for t in job_titles if t[0])
        
        # Skill suggestions
        skills = Skill.query.filter(
            Skill.name.ilike(search_term)
        ).limit(5).all()
        suggestions.update(s.name for s in skills)
        
        # Location suggestions
        locations = Job.query.filter(
            Job.status == 'active',
            Job.location.ilike(search_term)
        ).with_entities(Job.location).distinct().limit(5).all()
        suggestions.update(l[0] for l in locations if l[0])
        
        # Company suggestions
        companies = Company.query.filter(
            Company.name.ilike(search_term)
        ).limit(5).all()
        suggestions.update(c.name for c in companies)
        
        return success_response(data=list(suggestions)[:15])
        
    except Exception as e:
        return error_response(f'Suggestions failed: {str(e)}', 500)
