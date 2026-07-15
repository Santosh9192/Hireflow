from routes.auth import auth_bp
from routes.jobs import jobs_bp
from routes.applications import applications_bp
from routes.candidates import candidates_bp
from routes.recruiters import recruiters_bp
from routes.admin import admin_bp
from routes.ai_routes import ai_bp
from routes.notifications import notifications_bp
from routes.analytics import analytics_bp
from routes.search import search_bp
from routes.resumes import resumes_bp
from routes.companies import companies_bp
from routes.skills import skills_bp
from routes.uploads import uploads_bp

def register_routes(app):
    """Register all blueprint routes with the app"""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
    app.register_blueprint(applications_bp, url_prefix='/api/applications')
    app.register_blueprint(candidates_bp, url_prefix='/api/candidates')
    app.register_blueprint(recruiters_bp, url_prefix='/api/recruiters')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(resumes_bp, url_prefix='/api/resumes')
    app.register_blueprint(companies_bp, url_prefix='/api/companies')
    app.register_blueprint(skills_bp, url_prefix='/api/skills')
    app.register_blueprint(uploads_bp, url_prefix='/api/uploads')

__all__ = ['register_routes']
