"""
HireFlow AI - Resume Routes
Manages resume uploads, downloads, and analysis
"""

from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, db
from models.resume import Resume
from models.candidate import CandidateProfile
from services.file_service import FileService
from services.resume_parser import ResumeParser
from services.ai_service import AIService
from utils.helpers import success_response, error_response
from datetime import datetime, timezone
import os

resumes_bp = Blueprint('resumes', __name__)
file_service = FileService()
resume_parser = ResumeParser()
ai_service = AIService()


@resumes_bp.route('', methods=['GET'])
@jwt_required()
def get_resumes():
    """Get user's resumes"""
    try:
        user_id = int(get_jwt_identity())
        resumes = Resume.query.filter_by(user_id=user_id)\
            .order_by(Resume.is_default.desc(), Resume.created_at.desc()).all()
        
        return success_response(data=[r.to_dict() for r in resumes])
        
    except Exception as e:
        return error_response(f'Failed to fetch resumes: {str(e)}', 500)


@resumes_bp.route('', methods=['POST'])
@jwt_required()
def upload_resume():
    """Upload a new resume"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if 'file' not in request.files:
            return error_response('No file provided', 400)
        
        file = request.files['file']
        if file.filename == '':
            return error_response('No file selected', 400)
        
        # Validate file type
        if not file_service.validate_file_type(file.filename):
            return error_response('Only PDF and DOCX files are allowed', 400)
        
        # Save file
        result = file_service.save_file(file, subfolder='resumes')
        if result.get('error'):
            return error_response(result['error'], 400)
        
        # Create resume record
        resume = Resume(
            user_id=user_id,
            title=request.form.get('title', result['original_filename']),
            filename=result['filename'],
            original_filename=result['original_filename'],
            file_path=result['file_path'],
            file_size=result['file_size'],
            file_type=result['file_type'],
            is_parsed=False
        )
        
        # Set as default if first resume
        existing_count = Resume.query.filter_by(user_id=user_id).count()
        if existing_count == 0:
            resume.is_default = True
        
        db.session.add(resume)
        db.session.flush()
        
        # Parse resume
        parse_result = resume_parser.extract_text(result['full_path'])
        if parse_result['success']:
            resume.parsed_text = parse_result['text']
            resume.is_parsed = True
            
            # Extract sections
            sections = resume_parser.extract_sections(parse_result['text'])
            resume.parsed_data = sections
            
            # AI analysis (async - don't block)
            try:
                ai_result = ai_service.parse_resume(parse_result['text'][:15000])
                if ai_result['success'] and ai_result.get('structured_data'):
                    resume.parsed_data = ai_result['structured_data']
                    if 'professional_summary' in ai_result['structured_data']:
                        resume.summary = ai_result['structured_data']['professional_summary']
            except Exception as ai_error:
                pass  # AI analysis failure shouldn't block upload
        
        # Update candidate profile
        if user.candidate_profile and not user.candidate_profile.current_resume_id:
            user.candidate_profile.current_resume_id = resume.id
        
        db.session.commit()
        
        return success_response(
            data=resume.to_dict(),
            message='Resume uploaded successfully',
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to upload resume: {str(e)}', 500)


@resumes_bp.route('/<int:resume_id>', methods=['GET'])
@jwt_required()
def get_resume(resume_id):
    """Get resume details"""
    try:
        user_id = int(get_jwt_identity())
        resume = Resume.query.get(resume_id)
        
        if not resume:
            return error_response('Resume not found', 404)
        
        if resume.user_id != user_id:
            return error_response('Not authorized', 403)
        
        return success_response(data=resume.to_dict())
        
    except Exception as e:
        return error_response(f'Failed to fetch resume: {str(e)}', 500)


@resumes_bp.route('/<int:resume_id>/download', methods=['GET'])
@jwt_required()
def download_resume(resume_id):
    """Download resume file"""
    try:
        user_id = int(get_jwt_identity())
        resume = Resume.query.get(resume_id)
        
        if not resume:
            return error_response('Resume not found', 404)
        
        # Allow download if owner or recruiter/admin
        user = User.query.get(user_id)
        if resume.user_id != user_id and user.role.value not in ['recruiter', 'admin']:
            return error_response('Not authorized', 403)
        
        file_path = os.path.join(
            file_service.get_upload_folder(''),
            resume.file_path
        )
        
        if not os.path.exists(file_path):
            return error_response('File not found on disk', 404)
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=resume.original_filename
        )
        
    except Exception as e:
        return error_response(f'Failed to download resume: {str(e)}', 500)


@resumes_bp.route('/<int:resume_id>', methods=['DELETE'])
@jwt_required()
def delete_resume(resume_id):
    """Delete a resume"""
    try:
        user_id = int(get_jwt_identity())
        resume = Resume.query.get(resume_id)
        
        if not resume:
            return error_response('Resume not found', 404)
        
        if resume.user_id != user_id:
            return error_response('Not authorized', 403)
        
        # Delete file from disk
        file_service.delete_file(resume.file_path)
        
        db.session.delete(resume)
        db.session.commit()
        
        return success_response(message='Resume deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete resume: {str(e)}', 500)


@resumes_bp.route('/<int:resume_id>/default', methods=['POST'])
@jwt_required()
def set_default_resume(resume_id):
    """Set resume as default"""
    try:
        user_id = int(get_jwt_identity())
        resume = Resume.query.get(resume_id)
        
        if not resume:
            return error_response('Resume not found', 404)
        
        if resume.user_id != user_id:
            return error_response('Not authorized', 403)
        
        # Remove default from all other resumes
        Resume.query.filter_by(user_id=user_id, is_default=True)\
            .update({'is_default': False})
        
        resume.is_default = True
        
        # Update candidate profile
        user = User.query.get(user_id)
        if user.candidate_profile:
            user.candidate_profile.current_resume_id = resume.id
        
        db.session.commit()
        
        return success_response(
            data=resume.to_dict(),
            message='Default resume updated'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to set default resume: {str(e)}', 500)


@resumes_bp.route('/<int:resume_id>/analyze', methods=['POST'])
@jwt_required()
def analyze_resume(resume_id):
    """Run AI analysis on resume"""
    try:
        user_id = int(get_jwt_identity())
        resume = Resume.query.get(resume_id)
        
        if not resume:
            return error_response('Resume not found', 404)
        
        if resume.user_id != user_id:
            return error_response('Not authorized', 403)
        
        if not resume.parsed_text:
            return error_response('Resume text not available. Upload a valid file.', 400)
        
        # Run AI analysis
        ai_result = ai_service.parse_resume(resume.parsed_text[:15000])
        
        if not ai_result['success']:
            return error_response(
                ai_result.get('error', 'AI analysis failed'), 500
            )
        
        # Update resume with analysis
        if ai_result.get('structured_data'):
            resume.parsed_data = ai_result['structured_data']
            if 'professional_summary' in ai_result['structured_data']:
                resume.summary = ai_result['structured_data']['professional_summary']
        
        resume.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return success_response(
            data=resume.to_dict(),
            message='Resume analysis completed'
        )
        
    except Exception as e:
        return error_response(f'Analysis failed: {str(e)}', 500)
