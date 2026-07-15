"""
HireFlow AI - Email Service
Handles all email communications including notifications and alerts
"""

from flask import current_app, render_template
from flask_mail import Message
from threading import Thread


class EmailService:
    """Service for sending emails"""

    def __init__(self, mail_instance):
        self.mail = mail_instance

    def send_async_email(self, app, msg):
        """Send email asynchronously"""
        with app.app_context():
            try:
                self.mail.send(msg)
                current_app.logger.info(f'Email sent to {msg.recipients}')
            except Exception as e:
                current_app.logger.error(f'Failed to send email: {str(e)}')

    def send_email(self, subject, recipients, html_body, sender=None):
        """Send an email"""
        msg = Message(
            subject=subject,
            recipients=recipients if isinstance(recipients, list) else [recipients],
            html=html_body,
            sender=sender or current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        
        # Send async
        app = current_app._get_current_object()
        Thread(target=self.send_async_email, args=(app, msg)).start()

    def send_welcome_email(self, user):
        """Send welcome email to new users"""
        subject = 'Welcome to HireFlow AI!'
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Welcome to HireFlow AI!</h1>
            </div>
            <div style="padding: 30px; background: #f9f9f9; border-radius: 0 0 10px 10px;">
                <h2>Hi {user.first_name}!</h2>
                <p>Thank you for joining HireFlow AI - your intelligent recruitment platform.</p>
                <p>With HireFlow AI, you can:</p>
                <ul>
                    <li>Create a professional profile</li>
                    <li>Upload and analyze your resume with AI</li>
                    <li>Find and apply to matching jobs</li>
                    <li>Track your applications</li>
                </ul>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{current_app.config.get('FRONTEND_URL', '#')}/login"
                       style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                              color: white; padding: 12px 30px; text-decoration: none;
                              border-radius: 5px; font-weight: bold;">
                        Get Started
                    </a>
                </div>
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    If you didn't create this account, please ignore this email.
                </p>
            </div>
        </div>
        """
        self.send_email(subject, user.email, html)

    def send_password_reset_email(self, user, reset_token):
        """Send password reset email"""
        reset_url = f"{current_app.config.get('FRONTEND_URL', '#')}/reset-password?token={reset_token}"
        subject = 'Reset Your HireFlow AI Password'
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Password Reset</h1>
            </div>
            <div style="padding: 30px; background: #f9f9f9;">
                <h2>Hi {user.first_name}!</h2>
                <p>We received a request to reset your password.</p>
                <p>Click the button below to reset it:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}"
                       style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                              color: white; padding: 12px 30px; text-decoration: none;
                              border-radius: 5px; font-weight: bold;">
                        Reset Password
                    </a>
                </div>
                <p style="color: #666; font-size: 14px;">
                    This link will expire in 1 hour.
                </p>
                <p style="color: #666; font-size: 12px;">
                    If you didn't request this, please ignore this email.
                </p>
            </div>
        </div>
        """
        self.send_email(subject, user.email, html)

    def send_application_received(self, candidate, job):
        """Send confirmation email when application is received"""
        subject = f'Application Received - {job.title}'
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h2 style="color: white; margin: 0;">Application Received!</h2>
            </div>
            <div style="padding: 30px; background: #f9f9f9;">
                <h2>Hi {candidate.first_name}!</h2>
                <p>Your application for <strong>{job.title}</strong> at <strong>{job.company.name if job.company else 'Company'}</strong>
                   has been received successfully.</p>
                <p>What happens next:</p>
                <ol>
                    <li>The recruiter will review your application</li>
                    <li>If shortlisted, you'll receive an interview invitation</li>
                    <li>You can track your application status in your dashboard</li>
                </ol>
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    Best of luck with your application!
                </p>
            </div>
        </div>
        """
        self.send_email(subject, candidate.email, html)

    def send_application_status_update(self, user, application, new_status):
        """Send email when application status changes"""
        status_emoji = {
            'reviewing': '🔍', 'shortlisted': '⭐', 'rejected': '💔',
            'interviewed': '🤝', 'offered': '🎉', 'accepted': '✅'
        }
        emoji = status_emoji.get(new_status, '📝')
        subject = f'{emoji} Application Update - {application.job.title}'
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h2 style="color: white; margin: 0;">Application Update</h2>
            </div>
            <div style="padding: 30px; background: #f9f9f9;">
                <h2>Hi {user.first_name}!</h2>
                <p>Your application for <strong>{application.job.title}</strong>
                   has been updated to: <strong>{new_status.upper()}</strong></p>
                <p>Log in to your dashboard for more details.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{current_app.config.get('FRONTEND_URL', '#')}/candidate/applications"
                       style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                              color: white; padding: 12px 30px; text-decoration: none;
                              border-radius: 5px; font-weight: bold;">
                        View Applications
                    </a>
                </div>
            </div>
        </div>
        """
        self.send_email(subject, user.email, html)

    def send_interview_invitation(self, candidate, interview):
        """Send interview invitation email"""
        subject = f'🎯 Interview Invitation - {interview.title}'
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h2 style="color: white; margin: 0;">Interview Invitation</h2>
            </div>
            <div style="padding: 30px; background: #f9f9f9;">
                <h2>Congratulations {candidate.first_name}!</h2>
                <p>You've been invited for an interview:</p>
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;
                            border-left: 4px solid #667eea;">
                    <h3>{interview.title}</h3>
                    <p><strong>Type:</strong> {interview.interview_type}</p>
                    <p><strong>Date:</strong> {interview.proposed_date}</p>
                    <p><strong>Time:</strong> {interview.proposed_time}</p>
                    <p><strong>Duration:</strong> {interview.duration_minutes} minutes</p>
                    {'<p><strong>Meeting Link:</strong> <a href="' + interview.meeting_link + '">' + interview.meeting_link + '</a></p>' if interview.meeting_link else ''}
                </div>
                <p>Please log in to your dashboard to confirm or reschedule.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{current_app.config.get('FRONTEND_URL', '#')}/candidate/interviews"
                       style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                              color: white; padding: 12px 30px; text-decoration: none;
                              border-radius: 5px; font-weight: bold;">
                        View Interview Details
                    </a>
                </div>
            </div>
        </div>
        """
        self.send_email(subject, candidate.email, html)

    def send_new_application_notification(self, recruiter, candidate, job):
        """Notify recruiter about new application"""
        subject = f'📬 New Application - {job.title}'
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h2 style="color: white; margin: 0;">New Application Received</h2>
            </div>
            <div style="padding: 30px; background: #f9f9f9;">
                <h2>Hi {recruiter.first_name}!</h2>
                <p><strong>{candidate.first_name} {candidate.last_name}</strong> has applied for
                   <strong>{job.title}</strong></p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{current_app.config.get('FRONTEND_URL', '#')}/recruiter/applications"
                       style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                              color: white; padding: 12px 30px; text-decoration: none;
                              border-radius: 5px; font-weight: bold;">
                        View Applications
                    </a>
                </div>
            </div>
        </div>
        """
        self.send_email(subject, recruiter.email, html)
