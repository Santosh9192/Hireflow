"""
HireFlow AI - AI Feature Routes
Endpoints for all AI-powered features using Google Gemini
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, db
from models.resume import Resume
from models.job import Job
from models.candidate import CandidateProfile
from models.ai_analysis import AIAnalysis
from models.skill import Skill, CandidateSkill
from services.ai_service import AIService
from services.resume_parser import ResumeParser
from utils.helpers import success_response, error_response
from datetime import datetime, timezone

ai_bp = Blueprint('ai', __name__)
# Lazy-initialized AI service (no app context needed at import time)
ai_service = None


def get_ai_service():
    global ai_service
    if ai_service is None:
        ai_service = AIService()
    return ai_service


@ai_bp.route('/parse-resume', methods=['POST'])
@jwt_required()
def parse_resume():
    """Parse resume text using AI"""
    try:
        data = request.get_json()
        if not data or not data.get('resume_text'):
            return error_response('Resume text is required', 400)
        
        result = get_ai_service().parse_resume(data['resume_text'])
        if not result['success']:
            return error_response(
                result.get('error', 'Failed to parse resume'), 500
            )
        
        # Save analysis
        user_id = int(get_jwt_identity())
        analysis = AIAnalysis(
            candidate_id=User.query.get(user_id).candidate_profile.id if User.query.get(user_id).candidate_profile else None,
            resume_id=data.get('resume_id'),
            analysis_type='resume_parse',
            input_text=data['resume_text'][:5000],
            output_text=result.get('text', '')[:5000],
            structured_data=result.get('structured_data'),
            status='completed',
            processing_time=result.get('processing_time'),
            model_used='gemini-pro'
        )
        db.session.add(analysis)
        db.session.commit()
        
        return success_response(
            data=result,
            message='Resume parsed successfully'
        )
        
    except Exception as e:
        return error_response(f'AI parsing failed: {str(e)}', 500)


@ai_bp.route('/ats-score', methods=['POST'])
@jwt_required()
def get_ats_score():
    """Calculate ATS compatibility score"""
    try:
        data = request.get_json()
        if not data:
            return error_response('Resume text and job description are required', 400)
        
        resume_text = data.get('resume_text', '')
        job_description = data.get('job_description', '')
        
        if not resume_text or not job_description:
            return error_response('Both resume text and job description are required', 400)
        
        result = get_ai_service().analyze_ats_score(resume_text, job_description)
        if not result['success']:
            return error_response(
                result.get('error', 'Failed to analyze ATS score'), 500
            )
        
        # Save analysis
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        analysis = AIAnalysis(
            candidate_id=user.candidate_profile.id if user.candidate_profile else None,
            resume_id=data.get('resume_id'),
            job_id=data.get('job_id'),
            analysis_type='ats_score',
            score=result.get('structured_data', {}).get('ats_score'),
            output_text=result.get('text', '')[:5000],
            structured_data=result.get('structured_data'),
            status='completed',
            processing_time=result.get('processing_time'),
            model_used='gemini-pro'
        )
        db.session.add(analysis)
        db.session.commit()
        
        return success_response(
            data=result,
            message='ATS analysis completed'
        )
        
    except Exception as e:
        return error_response(f'ATS analysis failed: {str(e)}', 500)


@ai_bp.route('/interview-questions', methods=['POST'])
@jwt_required()
def generate_questions():
    """Generate interview questions"""
    try:
        data = request.get_json()
        if not data:
            return error_response('Job title and description are required', 400)
        
        job_title = data.get('job_title', '')
        job_description = data.get('job_description', '')
        skills = data.get('skills', [])
        
        if not job_title:
            return error_response('Job title is required', 400)
        
        result = get_ai_service().generate_interview_questions(
            job_title, job_description, skills
        )
        
        if not result['success']:
            return error_response(
                result.get('error', 'Failed to generate questions'), 500
            )
        
        return success_response(
            data=result,
            message='Interview questions generated'
        )
        
    except Exception as e:
        return error_response(f'Question generation failed: {str(e)}', 500)


@ai_bp.route('/cover-letter', methods=['POST'])
@jwt_required()
def generate_cover_letter():
    """Generate a professional cover letter"""
    try:
        data = request.get_json()
        if not data:
            return error_response('Required information missing', 400)
        
        result = get_ai_service().generate_cover_letter(
            candidate_name=data.get('candidate_name', ''),
            job_title=data.get('job_title', ''),
            company_name=data.get('company_name', ''),
            skills=data.get('skills', ''),
            experience_summary=data.get('experience_summary', ''),
            job_description=data.get('job_description', '')
        )
        
        if not result['success']:
            return error_response(
                result.get('error', 'Failed to generate cover letter'), 500
            )
        
        return success_response(
            data=result,
            message='Cover letter generated'
        )
        
    except Exception as e:
        return error_response(f'Cover letter generation failed: {str(e)}', 500)


@ai_bp.route('/professional-summary', methods=['POST'])
@jwt_required()
def generate_summary():
    """Generate professional summary"""
    try:
        data = request.get_json()
        if not data or not data.get('resume_text'):
            return error_response('Resume text is required', 400)
        
        result = get_ai_service().generate_professional_summary(data['resume_text'])
        
        if not result['success']:
            return error_response(
                result.get('error', 'Failed to generate summary'), 500
            )
        
        return success_response(
            data=result,
            message='Professional summary generated'
        )
        
    except Exception as e:
        return error_response(f'Summary generation failed: {str(e)}', 500)


@ai_bp.route('/skill-gap', methods=['POST'])
@jwt_required()
def analyze_skill_gap():
    """Analyze skill gaps between candidate and job requirements"""
    try:
        data = request.get_json()
        if not data:
            return error_response('Skills data required', 400)
        
        result = get_ai_service().analyze_skill_gap(
            data.get('candidate_skills', []),
            data.get('required_skills', [])
        )
        
        if not result['success']:
            return error_response(
                result.get('error', 'Failed to analyze skill gap'), 500
            )
        
        return success_response(
            data=result,
            message='Skill gap analysis completed'
        )
        
    except Exception as e:
        return error_response(f'Skill gap analysis failed: {str(e)}', 500)


@ai_bp.route('/keyword-optimize', methods=['POST'])
@jwt_required()
def optimize_keywords():
    """Optimize resume keywords for ATS"""
    try:
        data = request.get_json()
        if not data or not data.get('resume_text') or not data.get('job_description'):
            return error_response('Resume text and job description required', 400)
        
        result = get_ai_service().optimize_keywords(
            data['resume_text'],
            data['job_description']
        )
        
        if not result['success']:
            return error_response(
                result.get('error', 'Failed to optimize keywords'), 500
            )
        
        return success_response(
            data=result,
            message='Keyword optimization completed'
        )
        
    except Exception as e:
        return error_response(f'Keyword optimization failed: {str(e)}', 500)


@ai_bp.route('/rank-candidates', methods=['POST'])
@jwt_required()
def rank_candidates():
    """Rank candidates for a job (Recruiter only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role.value not in ['recruiter', 'admin']:
            return error_response('Access denied', 403)
        
        data = request.get_json()
        if not data:
            return error_response('Job requirements and candidates data required', 400)
        
        result = get_ai_service().rank_candidates(
            data.get('job_requirements', {}),
            data.get('candidates', [])
        )
        
        if not result['success']:
            return error_response(
                result.get('error', 'Failed to rank candidates'), 500
            )
        
        return success_response(
            data=result,
            message='Candidates ranked successfully'
        )
        
    except Exception as e:
        return error_response(f'Candidate ranking failed: {str(e)}', 500)


@ai_bp.route('/chat', methods=['POST'])
@jwt_required()
def ai_chat():
    """Interactive AI chat assistant for career guidance"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        data = request.get_json()
        if not data or not data.get('message'):
            return error_response('Message is required', 400)
        
        message = data['message'].strip()
        context_type = data.get('context', 'general')  # general, career, resume, interview
        conversation_history = data.get('history', [])
        
        # Build system prompt based on user role and context
        system_prompt = """You are HireFlow AI, an expert career assistant integrated into an ATS platform.
You help with:
- Resume writing and optimization tips
- Interview preparation and practice questions
- Career advice and job search strategies
- Skill development recommendations
- Cover letter writing
- Salary negotiation tips
- Professional networking advice

Be concise, practical, and supportive. Provide actionable advice.
"""
        
        if context_type == 'resume':
            system_prompt = "You are an expert resume writer and ATS optimization specialist. Help improve resumes with specific, actionable advice for passing ATS filters and impressing recruiters."
        elif context_type == 'interview':
            system_prompt = "You are an interview coach. Help prepare for interviews with practice questions, STAR method guidance, and tips for different interview formats."
        elif context_type == 'career':
            system_prompt = "You are a career counselor. Provide guidance on career paths, skill development, job search strategies, and professional growth."
        
        # Build conversation prompt
        full_prompt = system_prompt + "\n\n"
        
        # Add conversation history
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            role = msg.get('role', 'user')
            text = msg.get('content', '')
            if role == 'user':
                full_prompt += f"User: {text}\n"
            else:
                full_prompt += f"Assistant: {text}\n"
        
        full_prompt += f"\nUser: {message}\nAssistant:"
        
        result = get_ai_service()._generate(full_prompt)
        
        if not result['success']:
            # Fallback response when AI is unavailable
            return success_response(
                data={
                    'reply': "I'm here to help with your career questions! Unfortunately, the AI service is currently unavailable. Please check your Gemini API configuration and try again. Meanwhile, you can explore our job listings, update your profile, or check your applications.",
                    'context': context_type,
                    'fallback': True
                },
                message='Chat response (fallback mode)'
            )
        
        return success_response(
            data={
                'reply': result['text'],
                'context': context_type,
                'processing_time': result.get('processing_time')
            },
            message='Chat response generated'
        )
        
    except Exception as e:
        return error_response(f'Chat failed: {str(e)}', 500)


@ai_bp.route('/analyze-job', methods=['POST'])
@jwt_required()
def analyze_job():
    """Analyze job description and extract key information"""
    try:
        data = request.get_json()
        if not data or not data.get('job_description'):
            return error_response('Job description is required', 400)
        
        # Use ATS analysis without resume for job analysis
        prompt = f"""
        Analyze this job description and extract key information in JSON format:
        
        {data['job_description'][:8000]}
        
        Return:
        {{
            "required_skills": [...],
            "preferred_skills": [...],
            "experience_required": "...",
            "education_required": "...",
            "key_responsibilities": [...],
            "soft_skills": [...],
            "industry": "...",
            "job_level": "...",
            "salary_range": "...",
            "keywords_for_resume": [...]
        }}
        """
        
        result = get_ai_service()._generate(prompt)
        
        if not result['success']:
            return error_response(
                result.get('error', 'Failed to analyze job'), 500
            )
        
        # Parse JSON from result
        import json, re
        try:
            cleaned = re.sub(r'```json\s*|\s*```', '', result['text']).strip()
            parsed = json.loads(cleaned)
            result['structured_data'] = parsed
        except json.JSONDecodeError:
            pass
        
        return success_response(
            data=result,
            message='Job analysis completed'
        )
        
    except Exception as e:
        return error_response(f'Job analysis failed: {str(e)}', 500)
