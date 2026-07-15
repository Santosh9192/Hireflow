"""
HireFlow AI - Application Factory
Creates and configures the Flask application
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_mail import Mail
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config.config import config_by_name
from models.user import db, BlacklistedToken
from datetime import datetime, timezone

# Initialize extensions
mail = Mail()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)


def create_app(config_name=None):
    """Create and configure the Flask application"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static'
    )
    
    # Load configuration
    app.config.from_object(config_by_name.get(config_name, config_by_name['development']))
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    jwt.init_app(app)
    
    # CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('FRONTEND_URL', '*'),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Rate limiting
    if app.config.get('RATELIMIT_ENABLED'):
        limiter.init_app(app)
    
    # JWT configuration
    app.config['JWT_SECRET_KEY'] = app.config.get('JWT_SECRET_KEY', 'super-secret')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = app.config.get('JWT_ACCESS_TOKEN_EXPIRES')
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']
    
    # Register blueprints
    register_routes(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_commands(app)
    
    # Serve frontend
    register_frontend_routes(app)
    
    app.logger.info(f'HireFlow AI started in {config_name} mode')
    
    return app


def register_routes(app):
    """Register all API route blueprints"""
    from routes import register_routes as register_blueprints
    register_blueprints(app)


def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'success': False, 'message': 'Bad request'}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'success': False, 'message': 'Forbidden'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'message': 'Resource not found'}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'success': False, 'message': 'Method not allowed'}), 405
    
    @app.errorhandler(429)
    def too_many_requests(error):
        return jsonify({
            'success': False,
            'message': 'Too many requests. Please try again later.'
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'success': False, 'message': 'Internal server error'}), 500
    
    # JWT error handlers
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'success': False, 'message': 'Invalid token'}), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': 'Token has expired',
            'token_expired': True
        }), 401
    
    @jwt.token_verification_failed_loader
    def token_verification_failed(jwt_header, jwt_payload):
        return jsonify({'success': False, 'message': 'Token verification failed'}), 401


def register_commands(app):
    """Register CLI commands"""
    
    @app.cli.command('init-db')
    def init_db():
        """Initialize database tables"""
        with app.app_context():
            db.create_all()
            print('Database tables created successfully')
    
    @app.cli.command('seed-data')
    def seed_data():
        """Seed database with sample data"""
        from database.seed_data import seed_database
        with app.app_context():
            seed_database()
            print('Sample data seeded successfully')


def register_frontend_routes(app):
    """Register frontend serving routes"""
    from flask import render_template, send_from_directory
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/<path:path>')
    def serve_frontend(path):
        """Serve frontend static files and pages"""
        # Try to serve as template first
        template_path = os.path.join('templates', f'{path}.html')
        if os.path.exists(os.path.join(app.root_path, '..', template_path)):
            return render_template(f'{path}.html')
        
        # Try as static file
        static_path = os.path.join('static', path)
        if os.path.exists(os.path.join(app.root_path, '..', static_path)):
            return send_from_directory(
                os.path.join(app.root_path, '..', 'static'),
                path
            )
        
        # Default to index (SPA-like behavior)
        return render_template('index.html')
    
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory(
            os.path.join(app.root_path, '..', 'static'),
            filename
        )


# JWT blacklist check
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    """Check if token has been blacklisted"""
    jti = jwt_payload.get('jti')
    token = BlacklistedToken.query.filter_by(jti=jti).first()
    return token is not None


# JWT identity loader
@jwt.user_identity_loader
def user_identity_lookup(user_id):
    """Load user identity for JWT
    NOTE: PyJWT >= 2.13 requires the 'sub' claim to be a string.
    """
    return str(user_id)


@jwt.user_lookup_loader
def user_lookup_callback(jwt_header, jwt_payload):
    """Load user from JWT"""
    identity = jwt_payload.get('sub')
    from models.user import User
    try:
        return User.query.get(int(identity))
    except (ValueError, TypeError):
        return None
