"""
HireFlow AI - Google Gemini AI Service
Handles all AI-powered features including resume parsing, analysis, and generation
"""

import json
import time
import re
from flask import current_app
import google.generativeai as genai


class AIService:
    """Service for interacting with Google Gemini AI"""

    def __init__(self, api_key=None):
        self.api_key = api_key
        self.model = None
        self._initialized = False
        # Lazy initialization - defer to first use

    def _ensure_initialized(self):
        """Lazy-initialize the Gemini AI model on first use"""
        if self._initialized:
            return True
        try:
            api_key = self.api_key or current_app.config.get('GEMINI_API_KEY', '')
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')
            self._initialized = True
            return True
        except Exception as e:
            try:
                current_app.logger.warning(f'Gemini AI not available: {str(e)}')
            except Exception:
                pass  # App context not available
            return False

    def _generate(self, prompt, max_retries=2):
        """Generate content using Gemini AI with retry logic"""
        if not self._ensure_initialized():
            return {'error': 'AI service not initialized', 'success': False}

        for attempt in range(max_retries):
            try:
                start_time = time.time()
                response = self.model.generate_content(prompt)
                processing_time = time.time() - start_time
                
                return {
                    'success': True,
                    'text': response.text,
                    'processing_time': processing_time,
                    'candidates': response.candidates
                }
            except Exception as e:
                if attempt == max_retries - 1:
                    return {'error': str(e), 'success': False}
                time.sleep(1)

    def parse_resume(self, resume_text):
        """Extract structured information from resume text"""
        prompt = f"""
        You are an expert resume parser. Extract the following information from this resume text.
        Return the output as a valid JSON object with these fields:
        - personal_info: {{name, email, phone, location, linkedin, github, portfolio}}
        - professional_summary: string (2-3 sentence summary)
        - skills: array of {{name, category, proficiency (1-5)}}
        - education: array of {{degree, institution, graduation_year, gpa, field}}
        - experience: array of {{title, company, location, start_date, end_date, description, current}}
        - projects: array of {{name, description, technologies, url}}
        - certifications: array of {{name, issuer, year}}
        - languages: array of language names
        
        Resume text:
        {resume_text[:15000]}
        
        Return ONLY valid JSON, no other text.
        """
        result = self._generate(prompt)
        if result['success']:
            try:
                cleaned = re.sub(r'```json\s*|\s*```', '', result['text']).strip()
                parsed = json.loads(cleaned)
                result['structured_data'] = parsed
            except json.JSONDecodeError:
                current_app.logger.error('Failed to parse resume JSON from AI response')
                result['structured_data'] = None
        return result

    def analyze_ats_score(self, resume_text, job_description):
        """Calculate ATS compatibility score between resume and job"""
        prompt = f"""
        You are an ATS (Applicant Tracking System) expert. Analyze this resume against the job description.
        
        Resume:
        {resume_text[:8000]}
        
        Job Description:
        {job_description[:8000]}
        
        Provide analysis in valid JSON format:
        {{
            "ats_score": (0-100 integer),
            "matched_keywords": [array of matched skills/keywords],
            "missing_keywords": [array of missing important keywords],
            "keyword_match_percentage": (float),
            "format_issues": [array of formatting issues],
            "section_scores": {{
                "skills": (0-100),
                "experience": (0-100),
                "education": (0-100),
                "keywords": (0-100)
            }},
            "strengths": [array of strengths],
            "weaknesses": [array of weaknesses],
            "suggestions": [array of improvement suggestions],
            "overall_assessment": "string"
        }}
        
        Return ONLY valid JSON, no other text.
        """
        result = self._generate(prompt)
        if result['success']:
            try:
                cleaned = re.sub(r'```json\s*|\s*```', '', result['text']).strip()
                parsed = json.loads(cleaned)
                result['structured_data'] = parsed
            except json.JSONDecodeError:
                current_app.logger.error('Failed to parse ATS score JSON')
                result['structured_data'] = None
        return result

    def generate_interview_questions(self, job_title, job_description, skills=None):
        """Generate interview questions based on job description"""
        skills_text = ', '.join(skills) if skills else 'Not specified'
        prompt = f"""
        Generate comprehensive interview questions for a {job_title} position.
        
        Job Description:
        {job_description[:5000]}
        
        Required Skills: {skills_text}
        
        Return in valid JSON format:
        {{
            "technical_questions": [
                {{"question": "...", "expected_answer_keywords": [...], "difficulty": "easy/medium/hard", "category": "..."}}
            ],
            "behavioral_questions": [
                {{"question": "...", "context": "..."}}
            ],
            "situational_questions": [
                {{"scenario": "...", "question": "..."}}
            ],
            "role_specific_questions": [
                {{"question": "...", "focus_area": "..."}}
            ]
        }}
        
        Generate at least 5 questions per category.
        Return ONLY valid JSON.
        """
        result = self._generate(prompt)
        if result['success']:
            try:
                cleaned = re.sub(r'```json\s*|\s*```', '', result['text']).strip()
                parsed = json.loads(cleaned)
                result['structured_data'] = parsed
            except json.JSONDecodeError:
                current_app.logger.error('Failed to parse interview questions JSON')
                result['structured_data'] = None
        return result

    def generate_cover_letter(self, candidate_name, job_title, company_name, 
                               skills, experience_summary, job_description):
        """Generate a professional cover letter"""
        prompt = f"""
        Write a professional cover letter for:
        
        Candidate: {candidate_name}
        Job Title: {job_title}
        Company: {company_name}
        Key Skills: {skills[:500]}
        Experience: {experience_summary[:500]}
        Job Description: {job_description[:2000]}
        
        Write a compelling, professional cover letter that:
        1. Opens with enthusiasm for the role and company
        2. Highlights relevant skills and experience
        3. Shows understanding of the company's needs
        4. Includes specific achievements
        5. Closes with a call to action
        
        Format it properly with date, salutation, body paragraphs, and closing.
        """
        return self._generate(prompt)

    def generate_professional_summary(self, resume_text):
        """Generate a professional summary from resume"""
        prompt = f"""
        Based on this resume, write 3 versions of a professional summary (2-3 sentences each):
        1. Standard professional summary
        2. Achievement-focused summary
        3. Skills-focused summary
        
        Resume:
        {resume_text[:8000]}
        
        Return in JSON format:
        {{
            "standard": "...",
            "achievement_focused": "...",
            "skills_focused": "..."
        }}
        
        Return ONLY valid JSON.
        """
        result = self._generate(prompt)
        if result['success']:
            try:
                cleaned = re.sub(r'```json\s*|\s*```', '', result['text']).strip()
                parsed = json.loads(cleaned)
                result['structured_data'] = parsed
            except json.JSONDecodeError:
                current_app.logger.error('Failed to parse professional summary JSON')
                result['structured_data'] = None
        return result

    def analyze_skill_gap(self, resume_skills, required_skills):
        """Analyze skill gaps between candidate and job requirements"""
        prompt = f"""
        Analyze the skill gap between these skills:
        
        Candidate Skills: {json.dumps(resume_skills[:50])}
        Required Skills: {json.dumps(required_skills[:50])}
        
        Return in valid JSON:
        {{
            "matching_skills": [array of {{name, proficiency, relevance}}],
            "missing_skills": [array of {{name, importance (high/medium/low), learning_resources: [array of suggestions]}}],
            "gap_percentage": (0-100),
            "skill_recommendations": [array of {{skill, reason, priority}}],
            "overall_readiness": "string",
            "estimated_training_time": "string"
        }}
        
        Return ONLY valid JSON.
        """
        result = self._generate(prompt)
        if result['success']:
            try:
                cleaned = re.sub(r'```json\s*|\s*```', '', result['text']).strip()
                parsed = json.loads(cleaned)
                result['structured_data'] = parsed
            except json.JSONDecodeError:
                current_app.logger.error('Failed to parse skill gap JSON')
                result['structured_data'] = None
        return result

    def rank_candidates(self, job_requirements, candidates_data):
        """Rank candidates based on job requirements"""
        prompt = f"""
        Rank these candidates for the following job:
        
        Job Requirements:
        {json.dumps(job_requirements)[:2000]}
        
        Candidates:
        {json.dumps(candidates_data)[:8000]}
        
        Return in valid JSON array:
        [
            {{
                "candidate_id": "...",
                "rank": 1,
                "overall_score": (0-100),
                "skill_match": (0-100),
                "experience_match": (0-100),
                "education_match": (0-100),
                "strengths": [...],
                "concerns": [...],
                "recommendation": "strongly_recommend/recommend/consider/not_recommended"
            }}
        ]
        
        Return ONLY valid JSON array.
        """
        result = self._generate(prompt)
        if result['success']:
            try:
                cleaned = re.sub(r'```json\s*|\s*```', '', result['text']).strip()
                parsed = json.loads(cleaned)
                result['structured_data'] = parsed
            except json.JSONDecodeError:
                current_app.logger.error('Failed to parse candidate ranking JSON')
                result['structured_data'] = None
        return result

    def optimize_keywords(self, resume_text, job_description):
        """Suggest keyword optimizations for resume"""
        prompt = f"""
        Analyze this resume against the job description and suggest keyword optimizations.
        
        Resume:
        {resume_text[:8000]}
        
        Job Description:
        {job_description[:8000]}
        
        Return in valid JSON:
        {{
            "current_keywords": [array of keywords present],
            "missing_keywords": [array of keywords to add],
            "keyword_density": {{"current": "...", "recommended": "..."}},
            "optimization_suggestions": [
                {{"section": "...", "current": "...", "suggested": "...", "reason": "..."}}
            ],
            "priority_changes": [array of {{change, impact (high/medium/low)}}]
        }}
        
        Return ONLY valid JSON.
        """
        result = self._generate(prompt)
        if result['success']:
            try:
                cleaned = re.sub(r'```json\s*|\s*```', '', result['text']).strip()
                parsed = json.loads(cleaned)
                result['structured_data'] = parsed
            except json.JSONDecodeError:
                current_app.logger.error('Failed to parse keyword optimization JSON')
                result['structured_data'] = None
        return result

    def analyze_sentiment(self, text):
        """Analyze sentiment of text (for cover letters, messages, etc.)"""
        prompt = f"""
        Analyze the sentiment and tone of this text:
        
        "{text[:3000]}"
        
        Return in valid JSON:
        {{
            "sentiment": "positive/negative/neutral",
            "confidence": 0.0-1.0,
            "tone": "...",
            "key_emotions": [...],
            "suggestions": "..."
        }}
        
        Return ONLY valid JSON.
        """
        result = self._generate(prompt)
        if result['success']:
            try:
                cleaned = re.sub(r'```json\s*|\s*```', '', result['text']).strip()
                parsed = json.loads(cleaned)
                result['structured_data'] = parsed
            except json.JSONDecodeError:
                current_app.logger.error('Failed to parse sentiment JSON')
                result['structured_data'] = None
        return result
