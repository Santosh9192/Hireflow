"""
HireFlow AI - Database Seed Data
Generates realistic sample data for development and testing
"""

import random
import json
from datetime import datetime, timezone, timedelta
from models.user import User, db
from models.company import Company
from models.job import Job
from models.candidate import CandidateProfile
from models.recruiter import RecruiterProfile
from models.skill import Skill, CandidateSkill
from models.resume import Resume
from models.application import Application
from models.notification import Notification


def seed_database():
    """Seed database with sample data"""
    print('Seeding database with sample data...')
    
    # Create skills
    skills_data = [
        # Programming Languages
        ('Python', 'Programming Languages', True), ('JavaScript', 'Programming Languages', True),
        ('TypeScript', 'Programming Languages', True), ('Java', 'Programming Languages', True),
        ('C++', 'Programming Languages', True), ('Ruby', 'Programming Languages', True),
        ('Go', 'Programming Languages', True), ('Rust', 'Programming Languages', True),
        ('PHP', 'Programming Languages', True), ('Swift', 'Programming Languages', True),
        ('Kotlin', 'Programming Languages', True), ('SQL', 'Programming Languages', True),
        
        # Web Development
        ('React', 'Web Development', True), ('Angular', 'Web Development', True),
        ('Vue.js', 'Web Development', True), ('Node.js', 'Web Development', True),
        ('Django', 'Web Development', True), ('Flask', 'Web Development', True),
        ('Express.js', 'Web Development', True), ('Next.js', 'Web Development', True),
        ('HTML/CSS', 'Web Development', True), ('REST API', 'Web Development', True),
        ('GraphQL', 'Web Development', True), ('Redux', 'Web Development', True),
        
        # Data Science & AI
        ('Machine Learning', 'Data Science & AI', True), ('Deep Learning', 'Data Science & AI', True),
        ('TensorFlow', 'Data Science & AI', True), ('PyTorch', 'Data Science & AI', True),
        ('Natural Language Processing', 'Data Science & AI', True),
        ('Computer Vision', 'Data Science & AI', True),
        ('Data Analysis', 'Data Science & AI', True), ('Statistics', 'Data Science & AI', True),
        
        # Cloud & DevOps
        ('AWS', 'Cloud & DevOps', True), ('Azure', 'Cloud & DevOps', True),
        ('GCP', 'Cloud & DevOps', True), ('Docker', 'Cloud & DevOps', True),
        ('Kubernetes', 'Cloud & DevOps', True), ('CI/CD', 'Cloud & DevOps', True),
        ('Terraform', 'Cloud & DevOps', True), ('Linux', 'Cloud & DevOps', True),
        
        # Databases
        ('PostgreSQL', 'Databases', True), ('MongoDB', 'Databases', True),
        ('MySQL', 'Databases', True), ('Redis', 'Databases', True),
        ('Elasticsearch', 'Databases', True), ('DynamoDB', 'Databases', True),
        
        # Design
        ('UI/UX Design', 'Design', False), ('Figma', 'Design', False),
        ('Adobe XD', 'Design', False), ('Photoshop', 'Design', False),
        ('Illustrator', 'Design', False),
        
        # Soft Skills
        ('Leadership', 'Soft Skills', False), ('Communication', 'Soft Skills', False),
        ('Problem Solving', 'Soft Skills', False), ('Teamwork', 'Soft Skills', False),
        ('Project Management', 'Soft Skills', False), ('Agile/Scrum', 'Soft Skills', False),
        
        # Marketing
        ('Digital Marketing', 'Marketing', False), ('SEO', 'Marketing', False),
        ('Content Marketing', 'Marketing', False), ('Social Media', 'Marketing', False),
        
        # Other Technical
        ('Git', 'Other Technical', True), ('Agile Methodologies', 'Other Technical', True),
        ('Microservices', 'Other Technical', True), ('System Design', 'Other Technical', True),
        ('Testing', 'Other Technical', True), ('Security', 'Other Technical', True),
    ]
    
    skills_map = {}
    for name, category, is_tech in skills_data:
        skill = Skill.query.filter_by(name=name).first()
        if not skill:
            skill = Skill(name=name, category=category, is_technical=is_tech)
            db.session.add(skill)
        skills_map[name] = skill
    
    db.session.commit()
    print(f'Created {len(skills_data)} skills')
    
    # Create admin user
    admin = User.query.filter_by(email='admin@hireflow.ai').first()
    if not admin:
        admin = User(
            email='admin@hireflow.ai',
            username='admin',
            first_name='System',
            last_name='Admin',
            role='admin',
            is_email_verified=True,
            is_active=True
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        print('Created admin user')
    
    # Create companies
    companies_data = [
        ('TechCorp Solutions', 'Technology', 'San Francisco, CA', 'Leading technology solutions provider'),
        ('DataFlow Analytics', 'Data Science', 'New York, NY', 'Data analytics and AI company'),
        ('CloudBase Inc', 'Cloud Computing', 'Seattle, WA', 'Cloud infrastructure provider'),
        ('DesignStudio', 'Design', 'Los Angeles, CA', 'Creative design agency'),
        ('FinSecure Bank', 'Finance', 'Chicago, IL', 'Digital banking solutions'),
        ('HealthTech Medical', 'Healthcare', 'Boston, MA', 'Healthcare technology'),
        ('EcoGreen Energy', 'Energy', 'Denver, CO', 'Renewable energy solutions'),
        ('EduLearn Platform', 'Education', 'Austin, TX', 'Online education platform'),
        ('GameForge Studios', 'Gaming', 'Portland, OR', 'Game development studio'),
        ('SocialConnect Media', 'Social Media', 'Miami, FL', 'Social media platform'),
    ]
    
    companies = []
    for name, industry, hq, desc in companies_data:
        company = Company.query.filter_by(name=name).first()
        if not company:
            company = Company(
                name=name,
                description=desc,
                industry=industry,
                headquarters=hq,
                company_size=random.choice(['51-200', '201-1000', '1000+']),
                founded_year=random.randint(2010, 2022),
                is_verified=True
            )
            db.session.add(company)
        companies.append(company)
    
    db.session.commit()
    print(f'Created {len(companies_data)} companies')
    
    # Create recruiters
    recruiter_data = [
        ('sarah.johnson@techcorp.com', 'Sarah', 'Johnson', 'HR Manager', 0),
        ('mike.chen@dataflow.com', 'Mike', 'Chen', 'Technical Recruiter', 1),
        ('emma.davis@cloudbase.com', 'Emma', 'Davis', 'Talent Acquisition Lead', 2),
        ('james.wilson@designstudio.com', 'James', 'Wilson', 'Creative Recruiter', 3),
        ('lisa.thompson@finsecure.com', 'Lisa', 'Thompson', 'HR Director', 4),
    ]
    
    recruiters = []
    for email, first, last, designation, company_idx in recruiter_data:
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                email=email,
                username=email.split('@')[0],
                first_name=first,
                last_name=last,
                role='recruiter',
                is_email_verified=True,
                is_active=True
            )
            user.set_password('Recruiter@123')
            db.session.add(user)
            db.session.flush()
        
        profile = RecruiterProfile.query.filter_by(user_id=user.id).first()
        if not profile:
            profile = RecruiterProfile(
                user_id=user.id,
                company_id=companies[company_idx].id,
                designation=designation,
                department='Human Resources',
                is_company_admin=True
            )
            db.session.add(profile)
        recruiters.append(user)
    
    db.session.commit()
    print(f'Created {len(recruiter_data)} recruiters')
    
    # Create candidates
    candidate_data = [
        ('alex.martinez@gmail.com', 'Alex', 'Martinez', 'Senior Full Stack Developer'),
        ('priya.patel@gmail.com', 'Priya', 'Patel', 'Data Scientist'),
        ('ryan.taylor@gmail.com', 'Ryan', 'Taylor', 'UX/UI Designer'),
        ('sophia.garcia@gmail.com', 'Sophia', 'Garcia', 'DevOps Engineer'),
        ('daniel.kim@gmail.com', 'Daniel', 'Kim', 'Machine Learning Engineer'),
        ('olivia.brown@gmail.com', 'Olivia', 'Brown', 'Product Manager'),
        ('william.johnson@gmail.com', 'William', 'Johnson', 'Frontend Developer'),
        ('emma.wilson@gmail.com', 'Emma', 'Wilson', 'Backend Developer'),
        ('noah.anderson@gmail.com', 'Noah', 'Anderson', 'Cloud Architect'),
        ('ava.thompson@gmail.com', 'Ava', 'Thompson', 'AI Research Scientist'),
        ('liam.davis@gmail.com', 'Liam', 'Davis', 'Full Stack Developer'),
        ('mia.white@gmail.com', 'Mia', 'White', 'Data Engineer'),
        ('ethan.moore@gmail.com', 'Ethan', 'Moore', 'Mobile Developer'),
        ('isabella.lee@gmail.com', 'Isabella', 'Lee', 'Cybersecurity Analyst'),
        ('jacob.harris@gmail.com', 'Jacob', 'Harris', 'Software Engineer'),
    ]
    
    candidates = []
    for email, first, last, headline in candidate_data:
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                email=email,
                username=email.split('@')[0],
                first_name=first,
                last_name=last,
                role='candidate',
                is_email_verified=True,
                is_active=True
            )
            user.set_password('Candidate@123')
            db.session.add(user)
            db.session.flush()
        
        profile = CandidateProfile.query.filter_by(user_id=user.id).first()
        if not profile:
            profile = CandidateProfile(
                user_id=user.id,
                headline=headline,
                bio=f'Experienced {headline.lower()} with a passion for building innovative solutions.',
                is_open_to_work=True,
                preferred_employment_type=random.choice(['full-time', 'contract', 'full-time']),
                preferred_work_mode=random.choice(['remote', 'hybrid', 'on-site']),
                preferred_salary_min=80000,
                preferred_salary_max=100000,
                education=[{
                    'degree': random.choice(['B.S.', 'M.S.', 'Ph.D.']),
                    'field': random.choice(['Computer Science', 'Engineering', 'Data Science', 'Design']),
                    'institution': random.choice(['MIT', 'Stanford', 'UC Berkeley', 'CMU', 'Georgia Tech']),
                    'graduation_year': random.randint(2015, 2023)
                }],
                experience=[{
                    'title': headline,
                    'company': random.choice(['Google', 'Microsoft', 'Amazon', 'Meta', 'Apple', 'Startup']),
                    'start_date': '2020-01',
                    'end_date': 'Present' if random.random() > 0.3 else '2023-06',
                    'description': f'Worked as {headline.lower()} on various projects'
                }],
                projects=[{
                    'name': random.choice(['AI Chat Platform', 'E-commerce App', 'Data Pipeline', 'Design System']),
                    'description': 'A full-stack project built with modern technologies',
                    'technologies': random.sample(['React', 'Python', 'AWS', 'Docker', 'TensorFlow'], 3)
                }]
            )
            
            # Fix salary
            salary_min = random.choice([80000, 100000, 120000, 150000])
            profile.preferred_salary_min = salary_min
            profile.preferred_salary_max = salary_min + random.choice([20000, 30000, 50000])
            
            db.session.add(profile)
            db.session.flush()
            
            # Add random skills to candidate
            sample_skills = random.sample(list(skills_map.keys()), random.randint(5, 12))
            for skill_name in sample_skills:
                skill = skills_map[skill_name]
                candidate_skill = CandidateSkill(
                    candidate_id=profile.id,
                    skill_id=skill.id,
                    proficiency=random.randint(3, 5),
                    years_experience=random.randint(1, 8),
                    is_top_skill=random.random() > 0.7
                )
                db.session.add(candidate_skill)
        
        candidates.append(user)
    
    db.session.commit()
    print(f'Created {len(candidate_data)} candidates')
    
    # Create jobs
    job_templates = [
        ('Senior Full Stack Developer', 'We are looking for an experienced full stack developer...',
         'full-time', 'remote', 'senior', 5, 8, 120000, 180000),
        ('Data Scientist', 'Join our data science team to work on cutting-edge ML models...',
         'full-time', 'hybrid', 'mid', 3, 6, 100000, 160000),
        ('UX/UI Designer', 'Create beautiful and intuitive user experiences...',
         'full-time', 'remote', 'mid', 3, 5, 90000, 140000),
        ('DevOps Engineer', 'Manage and improve our cloud infrastructure...',
         'full-time', 'remote', 'senior', 4, 7, 110000, 170000),
        ('Machine Learning Engineer', 'Develop and deploy ML models at scale...',
         'full-time', 'hybrid', 'senior', 4, 8, 130000, 200000),
        ('Frontend Developer', 'Build responsive and performant web applications...',
         'full-time', 'remote', 'mid', 2, 5, 80000, 130000),
        ('Backend Developer', 'Design and implement scalable backend services...',
         'full-time', 'remote', 'mid', 3, 6, 100000, 150000),
        ('Product Manager', 'Lead product strategy and execution...',
         'full-time', 'hybrid', 'senior', 5, 8, 130000, 180000),
        ('Data Engineer', 'Build and maintain data pipelines...',
         'contract', 'remote', 'mid', 3, 6, 110000, 160000),
        ('AI Research Scientist', 'Push the boundaries of AI research...',
         'full-time', 'on-site', 'senior', 5, 10, 150000, 250000),
        ('iOS Developer', 'Develop native iOS applications...',
         'full-time', 'hybrid', 'mid', 2, 5, 90000, 140000),
        ('Cybersecurity Analyst', 'Protect our systems and data...',
         'full-time', 'on-site', 'mid', 3, 6, 100000, 155000),
    ]
    
    jobs = []
    for title, desc, emp_type, work_mode, exp_level, min_exp, max_exp, sal_min, sal_max in job_templates:
        company = random.choice(companies)
        recruiter = random.choice(recruiters)
        
        job = Job.query.filter_by(
            title=title,
            company_id=company.id,
            posted_by=recruiter.id
        ).first()
        
        if not job:
            job = Job(
                company_id=company.id,
                posted_by=recruiter.id,
                title=title,
                description=desc,
                requirements='- Strong problem-solving skills\n- Excellent communication\n- Team player\n- Self-motivated',
                responsibilities='- Design and implement features\n- Code review and mentoring\n- Collaborate with cross-functional teams\n- Write technical documentation',
                category=random.choice(['Engineering', 'Design', 'Data', 'Product', 'Security']),
                employment_type=emp_type,
                work_mode=work_mode,
                experience_level=exp_level,
                min_experience=min_exp,
                max_experience=max_exp,
                location=f'{random.choice(["San Francisco", "New York", "Austin", "Seattle", "Remote"])}, {random.choice(["CA", "NY", "TX", "WA"])}',
                salary_min=sal_min,
                salary_max=sal_max,
                show_salary=True,
                required_skills=json.dumps(random.sample(list(skills_map.keys()), random.randint(5, 8))),
                status='active',
                is_featured=random.random() > 0.7,
                positions_available=random.randint(1, 3),
                published_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))
            )
            db.session.add(job)
            db.session.flush()
            
            # Create some applications
            num_applicants = random.randint(2, 6)
            applicants = random.sample(candidates, min(num_applicants, len(candidates)))
            
            for applicant in applicants:
                if applicant.candidate_profile:
                    existing_app = Application.query.filter_by(
                        job_id=job.id,
                        candidate_id=applicant.candidate_profile.id
                    ).first()
                    
                    if not existing_app:
                        status = random.choice(['pending', 'reviewing', 'shortlisted', 'rejected'])
                        app = Application(
                            job_id=job.id,
                            candidate_id=applicant.candidate_profile.id,
                            status=status,
                            applied_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 15))
                        )
                        db.session.add(app)
                        job.applications_count = (job.applications_count or 0) + 1
        
        jobs.append(job)
    
    db.session.commit()
    print(f'Created {len(job_templates)} jobs with applications')
    
    # Create sample notifications
    for user in candidates + recruiters + [admin]:
        for _ in range(random.randint(1, 3)):
            notification = Notification(
                user_id=user.id,
                type=random.choice(['system', 'application_received', 'application_status']),
                title=random.choice([
                    'Welcome to HireFlow AI!',
                    'Your profile is 80% complete',
                    'New job recommendations available',
                    'Application status updated',
                    'Interview invitation received'
                ]),
                message='Check your dashboard for more details.',
                icon=random.choice(['fa-bell', 'fa-star', 'fa-envelope', 'fa-calendar']),
                color='#667eea',
                is_read=random.random() > 0.5,
                is_email_sent=False
            )
            db.session.add(notification)
    
    db.session.commit()
    print('Created sample notifications')
    print('\n*** Database seeding completed successfully! ***')
    print('\nSample Login Credentials:')
    print('  Admin:     admin@hireflow.ai / Admin@123')
    print('  Recruiter: sarah.johnson@techcorp.com / Recruiter@123')
    print('  Candidate: alex.martinez@gmail.com / Candidate@123')
