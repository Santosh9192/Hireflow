/*===========================================================
  HireFlow AI - Main JavaScript Application
  API Client | State Management | UI Utilities | Routing
===========================================================*/

// ----- API Client -----
const API = {
  BASE_URL: '/api',
  TOKEN_KEY: 'hireflow_token',
  USER_KEY: 'hireflow_user',

  getHeaders(includeAuth = true) {
    const headers = {
      'Content-Type': 'application/json',
    };
    if (includeAuth) {
      const token = this.getToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }
    return headers;
  },

  getToken() {
    return localStorage.getItem(this.TOKEN_KEY) || sessionStorage.getItem(this.TOKEN_KEY);
  },

  setToken(token, remember = false) {
    const storage = remember ? localStorage : sessionStorage;
    storage.setItem(this.TOKEN_KEY, token);
  },

  getUser() {
    try {
      const user = localStorage.getItem(this.USER_KEY);
      return user ? JSON.parse(user) : null;
    } catch {
      return null;
    }
  },

  setUser(user) {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  },

  clearAuth() {
    localStorage.removeItem(this.TOKEN_KEY);
    sessionStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  },

  async request(endpoint, options = {}) {
    const url = `${this.BASE_URL}${endpoint}`;
    const config = {
      ...options,
      headers: {
        ...this.getHeaders(!options.public),
        ...options.headers,
      },
    };

    // Remove Content-Type for FormData
    if (options.body instanceof FormData) {
      delete config.headers['Content-Type'];
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        if (response.status === 401) {
          this.clearAuth();
          window.location.hash = '#login';
          throw new Error(data.message || 'Session expired. Please login again.');
        }
        throw new Error(data.message || 'An error occurred');
      }

      return data;
    } catch (error) {
      if (error.name === 'TypeError') {
        throw new Error('Network error. Please check your connection.');
      }
      throw error;
    }
  },

  // Auth endpoints
  async login(email, password, remember = false) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
      public: true,
    });
    this.setToken(data.data.tokens.access_token, remember);
    this.setUser(data.data.user);
    return data.data;
  },

  async register(userData) {
    const data = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
      public: true,
    });
    this.setToken(data.data.tokens.access_token);
    this.setUser(data.data.user);
    return data.data;
  },

  async logout() {
    try {
      await this.request('/auth/logout', { method: 'POST' });
    } finally {
      this.clearAuth();
    }
  },

  async getProfile() {
    return this.request('/auth/profile');
  },

  async updateProfile(data) {
    return this.request('/auth/update-profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async changePassword(data) {
    return this.request('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async forgotPassword(email) {
    return this.request('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
      public: true,
    });
  },

  async resetPassword(data) {
    return this.request('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify(data),
      public: true,
    });
  },

  // Jobs endpoints
  async getJobs(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/jobs?${query}`, { public: true });
  },

  async getJob(jobId) {
    return this.request(`/jobs/${jobId}`, { public: true });
  },

  async createJob(data) {
    return this.request('/jobs', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateJob(jobId, data) {
    return this.request(`/jobs/${jobId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async deleteJob(jobId) {
    return this.request(`/jobs/${jobId}`, { method: 'DELETE' });
  },

  async saveJob(jobId) {
    return this.request(`/jobs/${jobId}/save`, { method: 'POST' });
  },

  async getSavedJobs(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/jobs/saved?${query}`);
  },

  async getJobCategories() {
    return this.request('/jobs/categories', { public: true });
  },

  // Applications endpoints
  async apply(data) {
    return this.request('/applications', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getApplications(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/applications?${query}`);
  },

  async getApplication(appId) {
    return this.request(`/applications/${appId}`);
  },

  async updateApplicationStatus(appId, data) {
    return this.request(`/applications/${appId}/status`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async getApplicationStats() {
    return this.request('/applications/stats');
  },

  // Candidate endpoints
  async getCandidateProfile() {
    return this.request('/candidates/profile');
  },

  async updateCandidateProfile(data) {
    return this.request('/candidates/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async getCandidateSkills() {
    return this.request('/candidates/skills');
  },

  async updateCandidateSkills(data) {
    return this.request('/candidates/skills', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async searchCandidates(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/candidates/search?${query}`);
  },

  // Recruiter endpoints
  async getRecruiterDashboard() {
    return this.request('/recruiters/dashboard');
  },

  async getCompanyProfile() {
    return this.request('/recruiters/company');
  },

  async updateCompanyProfile(data) {
    return this.request('/recruiters/company', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async getRecruiterJobs(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/recruiters/jobs?${query}`);
  },

  async getRecruiterApplications(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/recruiters/applications?${query}`);
  },

  async createInterview(data) {
    return this.request('/recruiters/interviews', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getInterviews() {
    return this.request('/recruiters/interviews');
  },

  // Resumes endpoints
  async getResumes() {
    return this.request('/resumes');
  },

  async uploadResume(formData) {
    return this.request('/resumes', {
      method: 'POST',
      body: formData,
      headers: {}, // Let the request function handle FormData
    });
  },

  async deleteResume(resumeId) {
    return this.request(`/resumes/${resumeId}`, { method: 'DELETE' });
  },

  async setDefaultResume(resumeId) {
    return this.request(`/resumes/${resumeId}/default`, { method: 'POST' });
  },

  async analyzeResume(resumeId) {
    return this.request(`/resumes/${resumeId}/analyze`, { method: 'POST' });
  },

  // AI endpoints
  async parseResume(resumeText, resumeId) {
    return this.request('/ai/parse-resume', {
      method: 'POST',
      body: JSON.stringify({ resume_text: resumeText, resume_id: resumeId }),
    });
  },

  async getATSScore(resumeText, jobDescription, resumeId, jobId) {
    return this.request('/ai/ats-score', {
      method: 'POST',
      body: JSON.stringify({
        resume_text: resumeText,
        job_description: jobDescription,
        resume_id: resumeId,
        job_id: jobId,
      }),
    });
  },

  async generateInterviewQuestions(jobTitle, jobDescription, skills) {
    return this.request('/ai/interview-questions', {
      method: 'POST',
      body: JSON.stringify({ job_title: jobTitle, job_description: jobDescription, skills }),
    });
  },

  async generateCoverLetter(data) {
    return this.request('/ai/cover-letter', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async generateProfessionalSummary(resumeText) {
    return this.request('/ai/professional-summary', {
      method: 'POST',
      body: JSON.stringify({ resume_text: resumeText }),
    });
  },

  async analyzeSkillGap(candidateSkills, requiredSkills) {
    return this.request('/ai/skill-gap', {
      method: 'POST',
      body: JSON.stringify({ candidate_skills: candidateSkills, required_skills: requiredSkills }),
    });
  },

  async optimizeKeywords(resumeText, jobDescription) {
    return this.request('/ai/keyword-optimize', {
      method: 'POST',
      body: JSON.stringify({ resume_text: resumeText, job_description: jobDescription }),
    });
  },

  async analyzeJob(jobDescription) {
    return this.request('/ai/analyze-job', {
      method: 'POST',
      body: JSON.stringify({ job_description: jobDescription }),
    });
  },

  // Notifications endpoints
  async getNotifications(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/notifications?${query}`);
  },

  async getUnreadCount() {
    return this.request('/notifications/unread-count');
  },

  async markNotificationRead(id) {
    return this.request(`/notifications/${id}/read`, { method: 'POST' });
  },

  async markAllNotificationsRead() {
    return this.request('/notifications/read-all', { method: 'POST' });
  },

  // Analytics endpoints
  async getDashboardAnalytics() {
    return this.request('/analytics/dashboard');
  },

  // Admin endpoints
  async getAdminDashboard() {
    return this.request('/admin/dashboard');
  },

  async getAdminUsers(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/admin/users?${query}`);
  },

  async updateUser(userId, data) {
    return this.request(`/admin/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async deleteUser(userId) {
    return this.request(`/admin/users/${userId}`, { method: 'DELETE' });
  },

  async getAdminJobs(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/admin/jobs?${query}`);
  },

  async getSystemLogs(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/admin/logs?${query}`);
  },

  async getReports(type = 'summary') {
    return this.request(`/admin/reports?type=${type}`);
  },

  // Search endpoints
  async globalSearch(query) {
    return this.request(`/search?q=${encodeURIComponent(query)}`, { public: true });
  },

  async getSearchSuggestions(query) {
    return this.request(`/search/suggestions?q=${encodeURIComponent(query)}`, { public: true });
  },

  // Skills endpoints
  async getSkills(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/skills?${query}`, { public: true });
  },

  async getTopSkills() {
    return this.request('/skills/top', { public: true });
  },

  // Upload endpoints
  async uploadProfilePhoto(formData) {
    return this.request('/uploads/profile-photo', {
      method: 'POST',
      body: formData,
      headers: {},
    });
  },

  async deleteProfilePhoto() {
    return this.request('/uploads/profile-photo', { method: 'DELETE' });
  },
};


// ----- State Management -----
const Store = {
  state: {
    user: null,
    token: null,
    loading: false,
    notifications: [],
    unreadCount: 0,
  },

  listeners: {},

  get(key) {
    return this.state[key];
  },

  set(key, value) {
    this.state[key] = value;
    this.notify(key, value);
  },

  on(key, callback) {
    if (!this.listeners[key]) {
      this.listeners[key] = [];
    }
    this.listeners[key].push(callback);
  },

  notify(key, value) {
    if (this.listeners[key]) {
      this.listeners[key].forEach(cb => cb(value));
    }
  },

  init() {
    const user = API.getUser();
    if (user) {
      this.set('user', user);
    }
  },
};


// ----- UI Utilities -----
const UI = {
  showToast(message, type = 'info', title = '') {
    const container = document.querySelector('.toast-container');
    if (!container) return;

    const icons = {
      success: 'fa-check-circle',
      error: 'fa-times-circle',
      warning: 'fa-exclamation-circle',
      info: 'fa-info-circle',
    };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <div class="toast-icon"><i class="fas ${icons[type] || icons.info}"></i></div>
      <div class="toast-content">
        <div class="toast-title">${title || type.charAt(0).toUpperCase() + type.slice(1)}</div>
        <div class="toast-message">${message}</div>
      </div>
      <button class="toast-close" onclick="this.parentElement.remove()">
        <i class="fas fa-times"></i>
      </button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.animation = 'slideOutRight 0.3s ease forwards';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  },

  showLoading(show = true) {
    const existing = document.querySelector('.loading-overlay');
    if (show) {
      if (!existing) {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
          <div class="spinner spinner-lg"></div>
          <div style="margin-top: 1rem; color: var(--text-secondary);">Loading...</div>
        `;
        overlay.style.cssText = `
          position: fixed; top: 0; left: 0; width: 100%; height: 100%;
          background: rgba(15, 15, 26, 0.6); backdrop-filter: blur(4px);
          display: flex; flex-direction: column; align-items: center;
          justify-content: center; z-index: 9999;
        `;
        document.body.appendChild(overlay);
      }
    } else if (existing) {
      existing.remove();
    }
  },

  showModal(html) {
    const overlay = document.querySelector('.modal-overlay') || document.createElement('div');
    overlay.className = 'modal-overlay active';
    overlay.innerHTML = html;
    document.body.appendChild(overlay);

    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.remove();
      }
    });
  },

  closeModal() {
    const overlay = document.querySelector('.modal-overlay');
    if (overlay) overlay.remove();
  },

  formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
    if (days < 365) return `${Math.floor(days / 30)} months ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  },

  formatSalary(min, max, period = 'yearly', currency = 'INR') {
    if (!min && !max) return '';
    const fmt = (n) => {
      if (!n) return '';
      if (currency === 'INR') {
        // Indian numbering: lakhs and crores
        if (n >= 10000000) return `₹${(n / 10000000).toFixed(1)} Cr`;
        if (n >= 100000) return `₹${(n / 100000).toFixed(1)} L`;
        if (n >= 1000) return `₹${(n / 1000).toFixed(0)}K`;
        return `₹${n}`;
      }
      if (n >= 1000) return `$${Math.round(n / 1000)}k`;
      return `$${n}`;
    };
    const periodLabel = period === 'yearly' ? '/yr' : period === 'monthly' ? '/mo' : '/hr';
    if (min && max) return `${fmt(min)} - ${fmt(max)}${periodLabel}`;
    if (min) return `From ${fmt(min)}${periodLabel}`;
    if (max) return `Up to ${fmt(max)}${periodLabel}`;
    return '';
  },

  escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  },

  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  renderSkills(skills, max = 5) {
    if (!skills || skills.length === 0) return '<span class="text-muted">No skills listed</span>';
    const display = skills.slice(0, max);
    const remaining = skills.length - max;
    return display.map(s => `<span class="skill-tag">${this.escapeHtml(s.name || s)}</span>`).join(' ') +
      (remaining > 0 ? `<span class="skill-tag">+${remaining} more</span>` : '');
  },

  renderBadge(status) {
    const colors = {
      active: 'badge-success',
      pending: 'badge-warning',
      reviewing: 'badge-info',
      shortlisted: 'badge-primary',
      interviewed: 'badge-info',
      rejected: 'badge-danger',
      offered: 'badge-success',
      accepted: 'badge-success',
      withdrawn: 'badge-secondary',
      closed: 'badge-secondary',
      draft: 'badge-secondary',
    };
    return `<span class="badge ${colors[status] || 'badge-secondary'}">${status}</span>`;
  },

  showSkeleton(container, count = 3) {
    if (typeof container === 'string') {
      container = document.querySelector(container);
    }
    if (!container) return;

    container.innerHTML = '';
    for (let i = 0; i < count; i++) {
      const skeleton = document.createElement('div');
      skeleton.className = 'skeleton skeleton-card';
      skeleton.style.marginBottom = '1rem';
      container.appendChild(skeleton);
    }
  },
};


// ----- Notification Manager -----
const NotificationManager = {
  async loadNotifications() {
    try {
      const result = await API.getNotifications({ per_page: 5, unread_only: 'true' });
      Store.set('notifications', result.data);
      Store.set('unreadCount', result.meta?.total || 0);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    }
  },

  async refreshUnreadCount() {
    try {
      const result = await API.getUnreadCount();
      Store.set('unreadCount', result.data?.unread_count || 0);
    } catch (error) {
      console.error('Failed to get unread count:', error);
    }
  },

  startPolling(interval = 30000) {
    this.refreshUnreadCount();
    return setInterval(() => this.refreshUnreadCount(), interval);
  },

  renderNotifications(container) {
    const notifications = Store.get('notifications');
    if (!notifications || notifications.length === 0) {
      container.innerHTML = `
        <div class="empty-state" style="padding: 2rem;">
          <div class="empty-state-icon"><i class="far fa-bell"></i></div>
          <div class="empty-state-title">No notifications</div>
          <div class="empty-state-text">You're all caught up!</div>
        </div>
      `;
      return;
    }

    container.innerHTML = notifications.map(n => `
      <div class="activity-item" onclick="NotificationManager.markRead(${n.id})">
        <div class="activity-icon" style="background: rgba(124, 58, 237, 0.1); color: var(--primary-light);">
          <i class="fas ${n.icon || 'fa-bell'}"></i>
        </div>
        <div class="activity-content">
          <div class="activity-title">${UI.escapeHtml(n.title)}</div>
          <div class="activity-time">${UI.formatDate(n.created_at)}</div>
        </div>
      </div>
    `).join('');
  },

  async markRead(id) {
    try {
      await API.markNotificationRead(id);
      this.loadNotifications();
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  },

  async markAllRead() {
    try {
      await API.markAllNotificationsRead();
      Store.set('unreadCount', 0);
      this.loadNotifications();
      UI.showToast('All notifications marked as read', 'success');
    } catch (error) {
      UI.showToast('Failed to mark all as read', 'error');
    }
  },
};


// ----- Router (fixed: handles missing routes gracefully) -----
const Router = {
  currentRoute: null,
  routes: {},
  _pendingRoute: null,
  _ready: false,

  register(name, handler) {
    this.routes[name] = handler;
    // If we had a pending navigation, retry now
    if (this._pendingRoute && this.routes[this._pendingRoute.split('/')[0]]) {
      const route = this._pendingRoute;
      this._pendingRoute = null;
      this.navigate('#' + route);
    }
  },

  navigate(hash) {
    const route = hash.replace('#', '') || 'dashboard';
    
    // If routes aren't registered yet, queue this navigation
    if (!this.routes[route.split('/')[0]] && route !== 'login') {
      this._pendingRoute = route;
      return;
    }
    
    this.currentRoute = route;
    this._pendingRoute = null;

    // Update active nav
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.toggle('active', item.dataset.route === route.split('/')[0]);
    });

    // Call route handler
    if (this.routes[route.split('/')[0]]) {
      this.routes[route.split('/')[0]](route);
    }
  },

  init() {
    window.addEventListener('hashchange', () => this.navigate(window.location.hash));
    if (!window.location.hash) {
      window.location.hash = '#dashboard';
    }
    this.navigate(window.location.hash);
  },
};


// ----- App Initialization -----
const App = {
  async    init() {
    Store.init();
    this.initTheme();
    this.initSidebar();
    this.initSearch();
    this.initNotifications();
    this.initAuthCheck();
    this.initGlobalShortcuts();
    this.initScrollToTop();
    Router.init();
  },

  initTheme() {
    // Apply saved theme or default to dark
    const savedTheme = localStorage.getItem('hireflow_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    this.updateThemeIcon(savedTheme);
  },

  toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const newTheme = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('hireflow_theme', newTheme);
    this.updateThemeIcon(newTheme);
    // Only show toast on first toggle per session
    if (!window._themeToggled) {
      UI.showToast(`Switched to ${newTheme} mode`, 'success');
      window._themeToggled = true;
    }
  },

  updateThemeIcon(theme) {
    const btn = document.getElementById('themeToggleBtn');
    if (btn) {
      btn.innerHTML = theme === 'dark' 
        ? '<i class="fas fa-moon"></i>' 
        : '<i class="fas fa-sun"></i>';
    }
  },

  initSidebar() {
    const toggleBtn = document.querySelector('.sidebar-toggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        document.querySelector('.sidebar')?.classList.toggle('collapsed');
        document.querySelector('.main-content')?.classList.toggle('expanded');
        document.querySelector('.navbar')?.classList.toggle('expanded');
      });
    }

    // Mobile toggle
    const mobileBtn = document.querySelector('.mobile-toggle');
    if (mobileBtn) {
      mobileBtn.addEventListener('click', () => {
        document.querySelector('.sidebar')?.classList.toggle('open');
      });
    }
  },

  initSearch() {
    const searchInput = document.querySelector('.navbar-search input');
    if (searchInput) {
      const debouncedSearch = UI.debounce(async (query) => {
        if (query.length < 2) return;
        try {
          const result = await API.getSearchSuggestions(query);
          // Show suggestions dropdown
          this.showSearchSuggestions(result.data);
        } catch (error) {
          console.error('Search failed:', error);
        }
      }, 300);

      searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        if (query.length >= 2) {
          debouncedSearch(query);
        }
      });

      searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          const query = e.target.value.trim();
          if (query) {
            window.location.hash = `#search?q=${encodeURIComponent(query)}`;
          }
        }
      });
    }
  },

  showSearchSuggestions(suggestions) {
    if (!suggestions || suggestions.length === 0) return;
    
    const searchBox = document.querySelector('.navbar-search');
    if (!searchBox) return;
    
    let dropdown = document.getElementById('searchSuggestions');
    if (!dropdown) {
      dropdown = document.createElement('div');
      dropdown.id = 'searchSuggestions';
      dropdown.style.cssText = `
        position: absolute; top: 100%; left: 0; right: 0;
        background: var(--bg-secondary); border: 1px solid var(--border-color);
        border-radius: var(--radius-lg); margin-top: 4px;
        box-shadow: var(--shadow-lg); z-index: 3000;
        max-height: 300px; overflow-y: auto;
      `;
      searchBox.style.position = 'relative';
      searchBox.appendChild(dropdown);
    }
    
    dropdown.innerHTML = suggestions.slice(0, 8).map(s => 
      `<div style="padding: 0.625rem 1rem; cursor: pointer; font-size: 0.875rem;
            color: var(--text-secondary); transition: background 0.15s;"
           onmouseover="this.style.background='var(--bg-hover)'"
           onmouseout="this.style.background='transparent'"
           onclick="document.getElementById('globalSearch').value='${UI.escapeHtml(s)}'; 
                    document.getElementById('searchSuggestions')?.remove();
                    App.navigateTo('search?q=${encodeURIComponent(s)}')">
        <i class="fas fa-search" style="margin-right: 0.5rem; font-size: 0.75rem;"></i>
        ${UI.escapeHtml(s)}
      </div>`
    ).join('');
    
    // Remove dropdown on outside click
    if (!window._searchDropdownHandler) {
      window._searchDropdownHandler = (e) => {
        if (!e.target.closest('.navbar-search')) {
          document.getElementById('searchSuggestions')?.remove();
        }
      };
      document.addEventListener('click', window._searchDropdownHandler);
    }
  },

  toggleNotificationPanel() {
    const panel = document.querySelector('.notification-panel');
    if (panel) {
      const isOpen = panel.classList.contains('open');
      panel.classList.toggle('open');
      if (!isOpen && API.getToken()) {
        NotificationManager.loadNotifications();
      }
    }
  },

  initNotifications() {
    const notificationBtn = document.querySelector('.notification-btn');
    if (notificationBtn) {
      notificationBtn.addEventListener('click', () => this.toggleNotificationPanel());
    }

    // Start polling for notifications if user is logged in
    if (API.getToken()) {
      NotificationManager.startPolling();
    }
  },

  initGlobalShortcuts() {
    // Ctrl+K or Cmd+K to focus search
    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('.navbar-search input');
        if (searchInput) {
          searchInput.focus();
          searchInput.select();
        }
      }
      // Escape to close dropdowns and modals
      if (e.key === 'Escape') {
        const openDropdown = document.querySelector('.dropdown-menu.show');
        if (openDropdown) openDropdown.classList.remove('show');
        const openPanel = document.querySelector('.notification-panel.open');
        if (openPanel) openPanel.classList.remove('open');
        UI.closeModal();
      }
    });
    
    // Add keyboard hint to search placeholder
    const searchInput = document.querySelector('.navbar-search input');
    if (searchInput) {
      searchInput.placeholder = 'Search jobs, skills, companies...  (Ctrl+K)';
    }
  },

  initScrollToTop() {
    // Create scroll-to-top button
    const btn = document.createElement('button');
    btn.id = 'scrollToTop';
    btn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    btn.style.cssText = `
      position: fixed; bottom: 2rem; right: 2rem; z-index: 999;
      width: 44px; height: 44px; border-radius: 50%;
      background: var(--primary-gradient); color: white; border: none;
      cursor: pointer; box-shadow: var(--shadow-lg);
      display: none; align-items: center; justify-content: center;
      font-size: 1.125rem; transition: all 0.3s ease;
    `;
    btn.onmouseover = () => { btn.style.transform = 'translateY(-3px)'; btn.style.boxShadow = 'var(--shadow-glow-strong)'; };
    btn.onmouseout = () => { btn.style.transform = ''; btn.style.boxShadow = ''; };
    btn.onclick = () => window.scrollTo({ top: 0, behavior: 'smooth' });
    document.body.appendChild(btn);
    
    const scrollThreshold = Math.min(400, window.innerHeight * 0.5);
    window.addEventListener('scroll', () => {
      btn.style.display = window.scrollY > scrollThreshold ? 'flex' : 'none';
    });
  },

  initAuthCheck() {
    const token = API.getToken();
    const user = API.getUser();
    const currentHash = window.location.hash || '#dashboard';

    // Protected routes
    const protectedRoutes = ['dashboard', 'profile', 'applications', 'saved-jobs', 'recruiter', 'admin'];
    const isProtected = protectedRoutes.some(r => currentHash.includes(r));

    if (!token && isProtected) {
      window.location.hash = '#login';
    }

    if (token && user) {
      this.updateUIForUser(user);
    }
  },

  updateUIForUser(user) {
    // Update user avatar in navbar
    const avatarContainer = document.querySelector('.navbar-user');
    if (avatarContainer) {
      const initials = `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`.toUpperCase();
      avatarContainer.innerHTML = `
        <div class="dropdown">
          <button class="btn btn-ghost btn-icon" onclick="this.nextElementSibling.classList.toggle('show')">
            <div class="user-avatar-placeholder">${initials}</div>
          </button>
          <div class="dropdown-menu" id="userDropdown">
            <button class="dropdown-item" onclick="App.navigateTo('profile')">
              <i class="fas fa-user"></i> Profile
            </button>
            <button class="dropdown-item" onclick="App.navigateTo('settings')">
              <i class="fas fa-cog"></i> Settings
            </button>
            <div class="dropdown-divider"></div>
            <button class="dropdown-item" onclick="App.handleLogout()">
              <i class="fas fa-sign-out-alt"></i> Logout
            </button>
          </div>
        </div>
      `;
    }

    // Update notification badge
    const badge = document.querySelector('.notification-badge');
    if (badge) {
      Store.on('unreadCount', (count) => {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
      });
    }

    // Show/hide role-specific nav items
    const role = user.role;
    document.querySelectorAll('[data-role]').forEach(el => {
      const roles = el.dataset.role.split(',');
      el.style.display = roles.includes(role) ? '' : 'none';
    });
  },

  navigateTo(route) {
    document.querySelector('.dropdown-menu.show')?.classList.remove('show');
    window.location.hash = `#${route}`;
  },

  async handleLogout() {
    try {
      await API.logout();
      UI.showToast('Logged out successfully', 'success');
      window.location.hash = '#login';
      window.location.reload();
    } catch (error) {
      UI.showToast('Failed to logout', 'error');
    }
  },

  async checkAuth() {
    const token = API.getToken();
    if (!token) return null;

    try {
      const result = await API.getProfile();
      API.setUser(result.data);
      Store.set('user', result.data);
      return result.data;
    } catch (error) {
      API.clearAuth();
      return null;
    }
  },
};


// ----- Form Validation -----
const Validator = {
  email(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  },

  password(password) {
    const errors = [];
    if (password.length < 8) errors.push('At least 8 characters');
    if (!/[A-Z]/.test(password)) errors.push('One uppercase letter');
    if (!/[a-z]/.test(password)) errors.push('One lowercase letter');
    if (!/[0-9]/.test(password)) errors.push('One number');
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) errors.push('One special character');
    return errors;
  },

  required(value, fieldName) {
    return value && value.trim() ? null : `${fieldName} is required`;
  },

  minLength(value, min, fieldName) {
    return value && value.length >= min ? null : `${fieldName} must be at least ${min} characters`;
  },

  showErrors(errors, form) {
    document.querySelectorAll('.form-error').forEach(el => el.remove());
    document.querySelectorAll('.form-input.error').forEach(el => el.classList.remove('error'));

    Object.entries(errors).forEach(([field, message]) => {
      const input = form.querySelector(`[name="${field}"]`);
      if (input) {
        input.classList.add('error');
        const error = document.createElement('div');
        error.className = 'form-error';
        error.textContent = message;
        input.parentNode.appendChild(error);
      }
    });
  },

  clearErrors(form) {
    document.querySelectorAll('.form-error').forEach(el => el.remove());
    document.querySelectorAll('.form-input.error').forEach(el => el.classList.remove('error'));
  },
};


// Global error handler for uncaught promise rejections
window.addEventListener('unhandledrejection', (event) => {
  console.warn('Unhandled Promise Rejection:', event.reason);
  event.preventDefault();
  
  const msg = event.reason?.message || 'Something went wrong. Please try again.';
  if (!msg.includes('login') && !msg.includes('redirect')) {
    // Use the existing UI utility
    if (typeof UI !== 'undefined' && UI.showToast) {
      UI.showToast(msg, 'error', 'Error');
    }
  }
});

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => App.init());
