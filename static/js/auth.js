/*===========================================================
  HireFlow AI - Authentication Pages
  Login, Register, Forgot Password, Reset Password
===========================================================*/

const AuthPages = {
    loginPage() {
        return `
            <div class="auth-page">
                <div class="auth-container animate-fade-in-up">
                    <div class="auth-header">
                        <div class="auth-logo">HF</div>
                        <h1 class="auth-title">Welcome Back</h1>
                        <p class="auth-subtitle">Sign in to your HireFlow AI account</p>
                    </div>

                    <form class="auth-form" id="loginForm" onsubmit="return AuthPages.handleLogin(event)">
                        <div class="form-group">
                            <label class="form-label">Email Address</label>
                            <input type="email" class="form-input" name="email" 
                                   placeholder="you@example.com" required>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Password</label>
                            <input type="password" class="form-input" name="password" 
                                   placeholder="Enter your password" required>
                        </div>

                        <div class="form-group" style="display: flex; justify-content: space-between; align-items: center;">
                            <label class="form-checkbox">
                                <input type="checkbox" name="remember">
                                <span>Remember me</span>
                            </label>
                            <a href="#forgot-password" style="font-size: 0.875rem;">Forgot Password?</a>
                        </div>

                        <button type="submit" class="btn btn-primary btn-lg" style="width: 100%;">
                            Sign In
                        </button>

                        <div class="auth-divider">Quick Login</div>

                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: var(--spacing-sm);">
                            <button type="button" class="btn btn-sm" style="background: rgba(124,58,237,0.15); color: var(--primary-light); border: 1px solid rgba(124,58,237,0.3); padding: 0.75rem 0.5rem; font-size: 0.75rem; cursor: pointer; border-radius: var(--radius-lg); transition: all 0.2s;" 
                                    onmouseover="this.style.background='rgba(124,58,237,0.25)'"
                                    onmouseout="this.style.background='rgba(124,58,237,0.15)'"
                                    onclick="AuthPages.quickLogin('alex.martinez@gmail.com', 'Candidate@123')">
                                <div style="font-weight: 600;">👤 Candidate</div>
                                <div style="font-size: 0.65rem; opacity: 0.7; margin-top: 2px;">Demo Account</div>
                            </button>
                            <button type="button" class="btn btn-sm" style="background: rgba(16,185,129,0.15); color: var(--accent-green); border: 1px solid rgba(16,185,129,0.3); padding: 0.75rem 0.5rem; font-size: 0.75rem; cursor: pointer; border-radius: var(--radius-lg); transition: all 0.2s;"
                                    onmouseover="this.style.background='rgba(16,185,129,0.25)'"
                                    onmouseout="this.style.background='rgba(16,185,129,0.15)'"
                                    onclick="AuthPages.quickLogin('sarah.johnson@techcorp.com', 'Recruiter@123')">
                                <div style="font-weight: 600;">💼 Recruiter</div>
                                <div style="font-size: 0.65rem; opacity: 0.7; margin-top: 2px;">Demo Account</div>
                            </button>
                            <button type="button" class="btn btn-sm" style="background: rgba(245,158,11,0.15); color: var(--accent-yellow); border: 1px solid rgba(245,158,11,0.3); padding: 0.75rem 0.5rem; font-size: 0.75rem; cursor: pointer; border-radius: var(--radius-lg); transition: all 0.2s;"
                                    onmouseover="this.style.background='rgba(245,158,11,0.25)'"
                                    onmouseout="this.style.background='rgba(245,158,11,0.15)'"
                                    onclick="AuthPages.quickLogin('admin@hireflow.ai', 'Admin@123')">
                                <div style="font-weight: 600;">👑 Admin</div>
                                <div style="font-size: 0.65rem; opacity: 0.7; margin-top: 2px;">Demo Account</div>
                            </button>
                        </div>

                        <div class="auth-footer" style="margin-top: 1rem;">
                            Don't have an account? <a href="#register">Create one</a>
                        </div>
                    </form>
                </div>
            </div>
        `;
    },

    registerPage() {
        return `
            <div class="auth-page">
                <div class="auth-container animate-fade-in-up">
                    <div class="auth-header">
                        <div class="auth-logo">HF</div>
                        <h1 class="auth-title">Create Account</h1>
                        <p class="auth-subtitle">Join HireFlow AI and accelerate your career</p>
                    </div>

                    <form class="auth-form" id="registerForm" onsubmit="return AuthPages.handleRegister(event)">
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">First Name</label>
                                <input type="text" class="form-input" name="first_name" 
                                       placeholder="John" required>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Last Name</label>
                                <input type="text" class="form-input" name="last_name" 
                                       placeholder="Doe" required>
                            </div>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Email Address</label>
                            <input type="email" class="form-input" name="email" 
                                   placeholder="you@example.com" required>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Role</label>
                            <select class="form-select" name="role" required>
                                <option value="candidate">Job Seeker / Candidate</option>
                                <option value="recruiter">Recruiter / Employer</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Password</label>
                            <input type="password" class="form-input" name="password" 
                                   placeholder="Create a strong password" required>
                            <div class="form-help">At least 8 characters with uppercase, lowercase, number & special char</div>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Confirm Password</label>
                            <input type="password" class="form-input" name="confirm_password" 
                                   placeholder="Repeat your password" required>
                        </div>

                        <button type="submit" class="btn btn-primary btn-lg" style="width: 100%;">
                            Create Account
                        </button>

                        <div class="auth-footer" style="margin-top: 1rem;">
                            Already have an account? <a href="#login">Sign in</a>
                        </div>
                    </form>
                </div>
            </div>
        `;
    },

    forgotPasswordPage() {
        return `
            <div class="auth-page">
                <div class="auth-container animate-fade-in-up">
                    <div class="auth-header">
                        <div class="auth-logo">HF</div>
                        <h1 class="auth-title">Forgot Password</h1>
                        <p class="auth-subtitle">Enter your email and we'll send you a reset link</p>
                    </div>

                    <form class="auth-form" id="forgotForm" onsubmit="return AuthPages.handleForgotPassword(event)">
                        <div class="form-group">
                            <label class="form-label">Email Address</label>
                            <input type="email" class="form-input" name="email" 
                                   placeholder="you@example.com" required>
                        </div>

                        <button type="submit" class="btn btn-primary btn-lg" style="width: 100%;">
                            Send Reset Link
                        </button>

                        <div class="auth-footer" style="margin-top: 1rem;">
                            Remember your password? <a href="#login">Sign in</a>
                        </div>
                    </form>
                </div>
            </div>
        `;
    },

    resetPasswordPage(token) {
        return `
            <div class="auth-page">
                <div class="auth-container animate-fade-in-up">
                    <div class="auth-header">
                        <div class="auth-logo">HF</div>
                        <h1 class="auth-title">Reset Password</h1>
                        <p class="auth-subtitle">Enter your new password</p>
                    </div>

                    <form class="auth-form" id="resetForm" onsubmit="return AuthPages.handleResetPassword(event)">
                        <input type="hidden" name="token" value="${token || ''}">
                        
                        <div class="form-group">
                            <label class="form-label">New Password</label>
                            <input type="password" class="form-input" name="password" 
                                   placeholder="Enter new password" required>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Confirm Password</label>
                            <input type="password" class="form-input" name="confirm_password" 
                                   placeholder="Confirm new password" required>
                        </div>

                        <button type="submit" class="btn btn-primary btn-lg" style="width: 100%;">
                            Reset Password
                        </button>

                        <div class="auth-footer" style="margin-top: 1rem;">
                            <a href="#login">Back to Sign In</a>
                        </div>
                    </form>
                </div>
            </div>
        `;
    },

    quickLogin(email, password) {
        // Fill the form fields and submit automatically
        const form = document.getElementById('loginForm');
        if (form) {
            form.querySelector('[name="email"]').value = email;
            form.querySelector('[name="password"]').value = password;
            // Dispatch submit event on the form so event.target is correct
            form.dispatchEvent(new Event('submit', { cancelable: true }));
        }
    },

    async handleLogin(event) {
        event.preventDefault();
        const form = event.target;
        const data = new FormData(form);
        
        Validator.clearErrors(form);
        UI.showLoading(true);
        
        try {
            const result = await API.login(
                data.get('email'),
                data.get('password'),
                data.get('remember') === 'on'
            );
            UI.showToast(`Welcome back, ${result.user.first_name}!`, 'success');
            Store.set('user', result.user);
            App.updateUIForUser(result.user);
            window.location.hash = '#dashboard';
        } catch (error) {
            UI.showToast(error.message, 'error', 'Login Failed');
        } finally {
            UI.showLoading(false);
        }
        
        return false;
    },

    async handleRegister(event) {
        event.preventDefault();
        const form = event.target;
        const data = new FormData(form);
        
        Validator.clearErrors(form);
        
        // Validate passwords match
        if (data.get('password') !== data.get('confirm_password')) {
            UI.showToast('Passwords do not match', 'error', 'Validation Error');
            return false;
        }
        
        UI.showLoading(true);
        
        try {
            const result = await API.register({
                email: data.get('email'),
                password: data.get('password'),
                first_name: data.get('first_name'),
                last_name: data.get('last_name'),
                role: data.get('role'),
            });
            UI.showToast(`Welcome to HireFlow AI, ${result.user.first_name}!`, 'success');
            Store.set('user', result.user);
            App.updateUIForUser(result.user);
            window.location.hash = '#dashboard';
        } catch (error) {
            UI.showToast(error.message, 'error', 'Registration Failed');
        } finally {
            UI.showLoading(false);
        }
        
        return false;
    },

    async handleForgotPassword(event) {
        event.preventDefault();
        const form = event.target;
        const data = new FormData(form);
        
        UI.showLoading(true);
        
        try {
            await API.forgotPassword(data.get('email'));
            form.innerHTML = `
                <div class="empty-state" style="padding: 2rem 0;">
                    <div class="empty-state-icon" style="color: var(--accent-green);">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <h3>Email Sent!</h3>
                    <p class="empty-state-text">Check your email for the password reset link.</p>
                    <a href="#login" class="btn btn-primary">Back to Sign In</a>
                </div>
            `;
        } catch (error) {
            UI.showToast(error.message, 'error');
        } finally {
            UI.showLoading(false);
        }
        
        return false;
    },

    async handleResetPassword(event) {
        event.preventDefault();
        const form = event.target;
        const data = new FormData(form);
        
        if (data.get('password') !== data.get('confirm_password')) {
            UI.showToast('Passwords do not match', 'error');
            return false;
        }
        
        UI.showLoading(true);
        
        try {
            await API.resetPassword({
                token: data.get('token'),
                password: data.get('password'),
            });
            UI.showToast('Password reset successful! Please login.', 'success');
            window.location.hash = '#login';
        } catch (error) {
            UI.showToast(error.message, 'error');
        } finally {
            UI.showLoading(false);
        }
        
        return false;
    }
};
