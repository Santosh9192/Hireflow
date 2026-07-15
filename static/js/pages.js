/*===========================================================
  HireFlow AI - Page Rendering Engine
  Renders pages dynamically based on route
===========================================================*/

const Pages = {
    container: null,

    init() {
        this.container = document.getElementById('pageContent');
    },

    render(html) {
        if (this.container) {
            this.container.innerHTML = html;
        }
    },

    showError(message = 'An error occurred') {
        this.render(`
            <div class="empty-state animate-fade-in">
                <div class="empty-state-icon"><i class="fas fa-exclamation-circle"></i></div>
                <h2>Oops!</h2>
                <p class="empty-state-text">${message}</p>
                <button class="btn btn-primary" onclick="window.location.reload()">Retry</button>
            </div>
        `);
    },

    showNotFound() {
        this.render(`
            <div class="empty-state animate-fade-in" style="padding: 4rem 2rem;">
                <div class="empty-state-icon"><i class="fas fa-map-signs"></i></div>
                <h2>Page Not Found</h2>
                <p class="empty-state-text">The page you're looking for doesn't exist.</p>
                <button class="btn btn-primary" onclick="App.navigateTo('dashboard')">Go to Dashboard</button>
            </div>
        `);
    },

    async loadPage(pageName, params = {}) {
        try {
            UI.showSkeleton(this.container);
            // Each page renders itself via the Router
        } catch (error) {
            this.showError(error.message);
        }
    },

    createElement(tag, attrs = {}, ...children) {
        const el = document.createElement(tag);
        Object.entries(attrs).forEach(([key, value]) => {
            if (key.startsWith('on') && typeof value === 'function') {
                el.addEventListener(key.slice(2).toLowerCase(), value);
            } else if (key === 'className') {
                el.className = value;
            } else if (key === 'style' && typeof value === 'object') {
                Object.assign(el.style, value);
            } else if (key === 'dataset') {
                Object.entries(value).forEach(([k, v]) => el.dataset[k] = v);
            } else {
                el.setAttribute(key, value);
            }
        });
        children.forEach(child => {
            if (typeof child === 'string') {
                el.appendChild(document.createTextNode(child));
            } else if (child instanceof Node) {
                el.appendChild(child);
            }
        });
        return el;
    }
};


// Initialize Pages immediately (routes registered before App.init runs)
document.addEventListener('DOMContentLoaded', () => {
    Pages.init();
});

// Register ALL routes IMMEDIATELY (not inside DOMContentLoaded)
// This ensures routes are ready before Router.init() is called

// Dashboard routes
Router.register('dashboard', async (route) => {
    const user = Store.get('user');
    if (!user) { App.navigateTo('login'); return; }
    
    if (user.role === 'candidate') {
        await Dashboard.renderCandidateDashboard();
    } else if (user.role === 'recruiter') {
        await Dashboard.renderRecruiterDashboard();
    } else if (user.role === 'admin') {
        await Dashboard.renderAdminDashboard();
    }
});

// Login route
Router.register('login', () => {
    if (API.getToken()) {
        App.navigateTo('dashboard');
        return;
    }
    // Direct to auth page
    Pages.render(AuthPages.loginPage());
});

Router.register('register', () => {
    Pages.render(AuthPages.registerPage());
});

Router.register('forgot-password', () => {
    Pages.render(AuthPages.forgotPasswordPage());
});

Router.register('reset-password', () => {
    const token = new URLSearchParams(window.location.hash.split('?')[1]).get('token');
    Pages.render(AuthPages.resetPasswordPage(token));
});

// Jobs routes
Router.register('jobs', async () => {
    await Jobs.renderJobList();
});

Router.register('job-detail', async () => {
    const id = window.location.hash.split('-').pop();
    await Jobs.renderJobDetail(id);
});

Router.register('applications', async () => {
    await Jobs.renderApplications();
});

Router.register('saved-jobs', async () => {
    await Jobs.renderSavedJobs();
});

// Recruiter routes
Router.register('recruiter-jobs', async () => {
    await Recruiter.renderJobList();
});

Router.register('recruiter-applications', async () => {
    await Recruiter.renderApplications();
});

Router.register('recruiter-interviews', async () => {
    await Recruiter.renderInterviews();
});

Router.register('post-job', async () => {
    await Recruiter.renderPostJob();
});

Router.register('edit-job', async () => {
    const id = window.location.hash.split('-').pop();
    await Recruiter.renderEditJob(id);
});

// Admin routes
Router.register('admin-dashboard', async () => {
    await Admin.renderDashboard();
});

Router.register('admin-users', async () => {
    await Admin.renderUsers();
});

Router.register('admin-jobs', async () => {
    await Admin.renderJobs();
});

Router.register('admin-logs', async () => {
    await Admin.renderLogs();
});

// Profile route (with error handling)
Router.register('profile', async () => {
    try {
        const user = Store.get('user');
        if (!user) { App.navigateTo('login'); return; }
        if (user?.role === 'candidate') {
            await Profile.renderCandidateProfile();
        } else {
            await Profile.renderGeneralProfile();
        }
    } catch (error) {
        console.error('Profile route error:', error);
        Pages.showError(error.message || 'Failed to load profile');
    }
});

// Settings route
Router.register('settings', async () => {
    await Profile.renderSettings();
});

// AI Chat route
Router.register('ai-chat', async () => {
    const user = Store.get('user');
    if (!user) { App.navigateTo('login'); return; }
    await AIChat.renderChat();
});

// Search route
Router.register('search', async () => {
    const params = new URLSearchParams(window.location.hash.split('?')[1]);
    const query = params.get('q') || '';
    await Jobs.renderJobList(query);
});
