/*===========================================================
  HireFlow AI - Dashboard Module
  Renders interactive dashboards for all user roles
===========================================================*/

const Dashboard = {
    charts: {},

    async renderCandidateDashboard() {
        Pages.render(`
            <div class="page-header animate-fade-in">
                <h1 class="page-title">Candidate Dashboard</h1>
                <p class="page-subtitle">Track your job applications and profile status</p>
            </div>
            <div id="dashboardContent" class="animate-fade-in-up">
                <div class="loading-center">
                    <div class="spinner"></div>
                    <div class="loading-text">Loading dashboard...</div>
                </div>
            </div>
        `);

        try {
            const [analytics, apps, skills] = await Promise.all([
                API.getDashboardAnalytics(),
                API.getApplications({ per_page: 5 }),
                API.getCandidateSkills(),
            ]);

            const data = analytics.data;
            const applications = apps.data || [];
            const userSkills = skills.data || [];

            const container = document.getElementById('dashboardContent');
            container.innerHTML = `
                <!-- Stats -->
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon purple">
                            <i class="fas fa-file-alt"></i>
                        </div>
                        <div class="stat-value">${data.total_applications || 0}</div>
                        <div class="stat-label">Total Applications</div>
                        <div class="stat-change positive">
                            <i class="fas fa-arrow-up"></i> ${data.recent_applications_count || 0} this month
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon green">
                            <i class="fas fa-calendar-check"></i>
                        </div>
                        <div class="stat-value">${data.interviews_count || 0}</div>
                        <div class="stat-label">Interviews</div>
                        <div class="stat-change ${(data.pending_interviews || 0) > 0 ? 'positive' : ''}">
                            ${data.pending_interviews || 0} pending
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon blue">
                            <i class="fas fa-star"></i>
                        </div>
                        <div class="stat-value">${userSkills.length}</div>
                        <div class="stat-label">Skills Listed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon yellow">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="stat-value">${data.profile_completion || 0}%</div>
                        <div class="stat-label">Profile Completion</div>
                        <div class="progress-bar" style="margin-top: 0.5rem;">
                            <div class="progress-bar-fill" style="width: ${data.profile_completion || 0}%"></div>
                        </div>
                    </div>
                </div>

                <div class="dashboard-grid">
                    <!-- Recent Applications -->
                    <div class="glass-card">
                        <div class="card-header">
                            <h3 class="card-title">Recent Applications</h3>
                            <a href="#applications" class="btn btn-ghost btn-sm">View All</a>
                        </div>
                        ${applications.length > 0 ? `
                        <div class="table-container" style="border: none;">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Position</th>
                                        <th>Company</th>
                                        <th>Status</th>
                                        <th>Date</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${applications.slice(0, 5).map(app => `
                                    <tr onclick="App.navigateTo('applications')" style="cursor: pointer;">
                                        <td><strong>${UI.escapeHtml(app.job?.title || 'N/A')}</strong></td>
                                        <td>${UI.escapeHtml(app.job?.company?.name || 'N/A')}</td>
                                        <td>${UI.renderBadge(app.status)}</td>
                                        <td>${UI.formatDate(app.created_at)}</td>
                                    </tr>`).join('')}
                                </tbody>
                            </table>
                        </div>` : `
                        <div class="empty-state">
                            <div class="empty-state-icon"><i class="fas fa-paper-plane"></i></div>
                            <h3>No Applications Yet</h3>
                            <p class="empty-state-text">Start applying to jobs that match your skills!</p>
                            <a href="#jobs" class="btn btn-primary"><i class="fas fa-search"></i> Browse Jobs</a>
                        </div>`}
                    </div>

                    <!-- Application Status Chart -->
                    <div class="glass-card">
                        <div class="card-header">
                            <h3 class="card-title">Application Status</h3>
                        </div>
                        <div class="chart-wrapper">
                            <canvas id="appStatusChart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Application Progress Timeline -->
                ${data.total_applications > 0 ? `
                <div class="glass-card" style="margin-top: 1.5rem;">
                    <div class="card-header">
                        <h3 class="card-title">Application Progress</h3>
                    </div>
                    <div style="display: flex; gap: 0; margin: 1rem 0; flex-wrap: wrap;">
                        ${(() => {
                            const statuses = ['pending', 'reviewing', 'shortlisted', 'interviewed', 'offered', 'accepted'];
                            const labels = {pending:'Applied', reviewing:'Reviewing', shortlisted:'Shortlisted', interviewed:'Interviewed', offered:'Offered', accepted:'Accepted'};
                            const colors = {pending:'#f59e0b', reviewing:'#3b82f6', shortlisted:'#8b5cf6', interviewed:'#06b6d4', offered:'#10b981', accepted:'#059669'};
                            const visible = statuses.filter(s => (data.applications_by_status || {})[s] > 0);
                            return visible.map((status, idx) => {
                                const count = (data.applications_by_status || {})[status] || 0;
                                const total = data.total_applications || 1;
                                const pct = Math.round((count / total) * 100);
                                return `
                                <div style="flex: ${Math.max(pct, 5)}; min-width: 60px; text-align: center; padding: 0.5rem;">
                                    <div style="height: 8px; background: ${colors[status]}; border-radius: 4px; margin-bottom: 0.5rem;
                                                ${idx === 0 ? 'border-radius: 4px 0 0 4px;' : ''} ${idx === visible.length - 1 ? 'border-radius: 0 4px 4px 0;' : ''} ${idx > 0 && idx < visible.length - 1 ? 'border-radius: 0;' : ''}">
                                    </div>
                                    <div style="font-size: 0.75rem; font-weight: 600;">${count}</div>
                                    <div style="font-size: 0.65rem; color: var(--text-muted);">${labels[status]}</div>
                                </div>`;
                            }).join('');
                        })()}
                    </div>
                </div>` : ''}

                <!-- Skills Radar Chart -->
                ${userSkills.length >= 3 ? `
                <div class="dashboard-grid" style="margin-top: 1.5rem;">
                    <div class="glass-card">
                        <div class="card-header">
                            <h3 class="card-title">Skills Distribution</h3>
                        </div>
                        <div class="skill-radar-container">
                            <canvas id="skillsRadarChart"></canvas>
                        </div>
                    </div>
                    <div class="glass-card">
                        <div class="card-header">
                            <h3 class="card-title">Profile Strength</h3>
                        </div>
                        <div class="ats-gauge-container">
                            <div class="ats-gauge">
                                <svg width="200" height="200" viewBox="0 0 200 200">
                                    <defs>
                                        <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                            <stop offset="0%" stop-color="#7c3aed" />
                                            <stop offset="100%" stop-color="#10b981" />
                                        </linearGradient>
                                    </defs>
                                    <circle class="bg" cx="100" cy="100" r="85" />
                                    <circle class="progress" id="profileGauge" cx="100" cy="100" r="85" 
                                            stroke-dasharray="534" stroke-dashoffset="534" />
                                </svg>
                                <div class="ats-gauge-value">
                                    <div class="ats-gauge-number" id="profileGaugeScore">${data.profile_completion || 0}</div>
                                    <div class="ats-gauge-label">Profile Score</div>
                                </div>
                            </div>
                        </div>
                        <div style="display: grid; gap: 0.75rem; padding: 0 1rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                                <span style="color: var(--text-secondary);">Skills Added</span>
                                <span style="font-weight: 600;">${userSkills.length}/10</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-bar-fill" style="width: ${Math.min((userSkills.length / 10) * 100, 100)}%"></div>
                            </div>
                            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-top: 0.5rem;">
                                <span style="color: var(--text-secondary);">Applications</span>
                                <span style="font-weight: 600;">${data.total_applications || 0}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                                <span style="color: var(--text-secondary);">Profile Complete</span>
                                <span style="font-weight: 600;">${data.profile_completion || 0}%</span>
                            </div>
                        </div>
                    </div>
                </div>` : ''}

                <!-- Skills Section -->
                ${userSkills.length > 0 ? `
                <div class="glass-card" style="margin-top: 1.5rem;">
                    <div class="card-header">
                        <h3 class="card-title">Your Skills (${userSkills.length})</h3>
                        <a href="#profile" class="btn btn-ghost btn-sm">Manage</a>
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        ${userSkills.slice(0, 10).map(s => `<span class="skill-tag">${UI.escapeHtml(s.skill?.name || '')}</span>`).join('')}
                        ${userSkills.length > 10 ? `<span class="skill-tag">+${userSkills.length - 10} more</span>` : ''}
                    </div>
                </div>` : ''}
            `;

            // Render charts
            this.renderApplicationStatusChart(data.applications_by_status || {});
            this.renderSkillsRadarChart(userSkills);
            this.renderProfileGauge(data.profile_completion || 0);

        } catch (error) {
            document.getElementById('dashboardContent').innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon"><i class="fas fa-exclamation-triangle"></i></div>
                    <h3>Failed to Load Dashboard</h3>
                    <p class="empty-state-text">${error.message}</p>
                    <button class="btn btn-primary" onclick="Dashboard.renderCandidateDashboard()">Retry</button>
                </div>
            `;
        }
    },

    async renderRecruiterDashboard() {
        Pages.render(`
            <div class="page-header animate-fade-in">
                <h1 class="page-title">Recruiter Dashboard</h1>
                <p class="page-subtitle">Manage your job postings and candidates</p>
            </div>
            <div id="dashboardContent" class="animate-fade-in-up">
                <div class="loading-center">
                    <div class="spinner"></div>
                    <div class="loading-text">Loading dashboard...</div>
                </div>
            </div>
        `);

        try {
            const data = (await API.getRecruiterDashboard()).data;
            const container = document.getElementById('dashboardContent');

            container.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon purple">
                            <i class="fas fa-briefcase"></i>
                        </div>
                        <div class="stat-value">${data.total_jobs || 0}</div>
                        <div class="stat-label">Total Jobs</div>
                        <div class="stat-change positive">${data.active_jobs || 0} active</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon blue">
                            <i class="fas fa-users"></i>
                        </div>
                        <div class="stat-value">${data.total_applications || 0}</div>
                        <div class="stat-label">Applications</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon yellow">
                            <i class="fas fa-hourglass-half"></i>
                        </div>
                        <div class="stat-value">${data.pending_applications || 0}</div>
                        <div class="stat-label">Pending Review</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon green">
                            <i class="fas fa-calendar"></i>
                        </div>
                        <div class="stat-value">${data.interview_count || 0}</div>
                        <div class="stat-label">Interviews</div>
                    </div>
                </div>

                <div class="dashboard-grid">
                    <div class="glass-card">
                        <div class="card-header">
                            <h3 class="card-title">Recent Applications</h3>
                            <a href="#recruiter-applications" class="btn btn-ghost btn-sm">View All</a>
                        </div>
                        ${data.recent_applications?.length > 0 ? `
                        <div class="table-container" style="border: none;">
                            <table>
                                <thead>
                                    <tr><th>Candidate</th><th>Position</th><th>Status</th><th>Date</th></tr>
                                </thead>
                                <tbody>
                                    ${data.recent_applications.slice(0, 5).map(app => `
                                    <tr onclick="App.navigateTo('recruiter-applications')" style="cursor: pointer;">
                                        <td>${UI.escapeHtml(app.candidate?.user?.full_name || 'N/A')}</td>
                                        <td>${UI.escapeHtml(app.job?.title || 'N/A')}</td>
                                        <td>${UI.renderBadge(app.status)}</td>
                                        <td>${UI.formatDate(app.created_at)}</td>
                                    </tr>`).join('')}
                                </tbody>
                            </table>
                        </div>` : `
                        <div class="empty-state">
                            <div class="empty-state-icon"><i class="fas fa-inbox"></i></div>
                            <h3>No Applications Yet</h3>
                            <p class="empty-state-text">When candidates apply, they'll appear here.</p>
                        </div>`}
                    </div>

                    <div class="glass-card">
                        <div class="card-header">
                            <h3 class="card-title">Job Statistics</h3>
                        </div>
                        <div class="chart-wrapper">
                            <canvas id="jobStatsChart"></canvas>
                        </div>
                    </div>
                </div>

                <div class="glass-card" style="margin-top: 1.5rem;">
                    <div class="card-header">
                        <h3 class="card-title">Your Job Postings</h3>
                        <a href="#post-job" class="btn btn-primary btn-sm"><i class="fas fa-plus"></i> Post New Job</a>
                    </div>
                    ${data.jobs?.length > 0 ? `
                    <div class="table-container" style="border: none;">
                        <table>
                            <thead>
                                <tr><th>Title</th><th>Applications</th><th>Status</th><th>Posted</th><th></th></tr>
                            </thead>
                            <tbody>
                                ${data.jobs.map(job => `
                                <tr>
                                    <td><strong>${UI.escapeHtml(job.title)}</strong></td>
                                    <td>${job.applications_count || 0}</td>
                                    <td>${UI.renderBadge(job.status)}</td>
                                    <td>${UI.formatDate(job.created_at)}</td>
                                    <td>
                                        <button class="btn btn-ghost btn-sm" onclick="App.navigateTo('edit-job-${job.id}')">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                    </td>
                                </tr>`).join('')}
                            </tbody>
                        </table>
                    </div>` : `
                    <div class="empty-state">
                        <div class="empty-state-icon"><i class="fas fa-plus-circle"></i></div>
                        <h3>No Jobs Posted</h3>
                        <p class="empty-state-text">Post your first job to start receiving applications.</p>
                        <a href="#post-job" class="btn btn-primary">Post a Job</a>
                    </div>`}
                </div>
            `;

            this.renderJobStatsChart(data.jobs);

        } catch (error) {
            document.getElementById('dashboardContent').innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon"><i class="fas fa-exclamation-triangle"></i></div>
                    <h3>Failed to Load Dashboard</h3>
                    <p class="empty-state-text">${error.message}</p>
                    <button class="btn btn-primary" onclick="Dashboard.renderRecruiterDashboard()">Retry</button>
                </div>
            `;
        }
    },

    async renderAdminDashboard() {
        Pages.render(`
            <div class="page-header animate-fade-in">
                <h1 class="page-title">Admin Dashboard</h1>
                <p class="page-subtitle">System overview and analytics</p>
            </div>
            <div id="dashboardContent" class="animate-fade-in-up">
                <div class="loading-center">
                    <div class="spinner"></div>
                    <div class="loading-text">Loading system data...</div>
                </div>
            </div>
        `);

        try {
            const data = (await API.getAdminDashboard()).data;
            const container = document.getElementById('dashboardContent');

            container.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon purple"><i class="fas fa-users"></i></div>
                        <div class="stat-value">${data.total_users || 0}</div>
                        <div class="stat-label">Total Users</div>
                        <div class="stat-change positive">+${data.today_users || 0} today</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon blue"><i class="fas fa-briefcase"></i></div>
                        <div class="stat-value">${data.total_jobs || 0}</div>
                        <div class="stat-label">Total Jobs</div>
                        <div class="stat-change positive">${data.total_active_jobs || 0} active</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon green"><i class="fas fa-file-alt"></i></div>
                        <div class="stat-value">${data.total_applications || 0}</div>
                        <div class="stat-label">Applications</div>
                        <div class="stat-change positive">+${data.today_applications || 0} today</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon yellow"><i class="fas fa-building"></i></div>
                        <div class="stat-value">${data.total_companies || 0}</div>
                        <div class="stat-label">Companies</div>
                    </div>
                </div>

                <div class="dashboard-grid">
                    <div class="glass-card">
                        <div class="card-header">
                            <h3 class="card-title">System Overview</h3>
                        </div>
                        <div style="display: grid; gap: 1rem;">
                            <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid var(--border-light);">
                                <span style="color: var(--text-secondary);">Candidates</span>
                                <span><strong>${data.total_candidates || 0}</strong></span>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid var(--border-light);">
                                <span style="color: var(--text-secondary);">Recruiters</span>
                                <span><strong>${data.total_recruiters || 0}</strong></span>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding: 0.75rem 0;">
                                <span style="color: var(--text-secondary);">Active Users</span>
                                <span><strong>${data.total_active_users || 0}</strong></span>
                            </div>
                        </div>
                    </div>

                    <div class="glass-card">
                        <div class="card-header">
                            <h3 class="card-title">Recent Activity</h3>
                        </div>
                        ${data.recent_activities?.length > 0 ? `
                        <div class="activity-list">
                            ${data.recent_activities.slice(0, 6).map(a => `
                            <div class="activity-item">
                                <div class="activity-icon" style="background: rgba(124,58,237,0.1); color: var(--primary-light);">
                                    <i class="fas fa-circle"></i>
                                </div>
                                <div class="activity-content">
                                    <div class="activity-title">${UI.escapeHtml(a.action || 'Activity')}</div>
                                    <div class="activity-time">${UI.formatDate(a.created_at)}</div>
                                </div>
                            </div>`).join('')}
                        </div>` : `
                        <div class="empty-state" style="padding: 1rem;">
                            <div class="empty-state-icon" style="font-size: 2rem;"><i class="fas fa-history"></i></div>
                            <div class="empty-state-title">No Recent Activity</div>
                        </div>`}
                    </div>
                </div>

                <div class="dashboard-grid-3" style="margin-top: 1.5rem;">
                    <div class="glass-card">
                        <div class="card-header"><h3 class="card-title">Users by Role</h3></div>
                        <div class="chart-wrapper" style="height: 250px;">
                            <canvas id="usersByRoleChart"></canvas>
                        </div>
                    </div>
                    <div class="glass-card">
                        <div class="card-header"><h3 class="card-title">Job Status</h3></div>
                        <div class="chart-wrapper" style="height: 250px;">
                            <canvas id="jobStatusChart"></canvas>
                        </div>
                    </div>
                    <div class="glass-card">
                        <div class="card-header"><h3 class="card-title">Monthly Growth</h3></div>
                        <div class="chart-wrapper" style="height: 250px;">
                            <canvas id="growthChart"></canvas>
                        </div>
                    </div>
                </div>
            `;

            // Render charts
            this.renderUsersByRoleChart(data.total_candidates, data.total_recruiters, data.total_users);
            this.renderJobStatusChart(data.job_statuses);

        } catch (error) {
            document.getElementById('dashboardContent').innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon"><i class="fas fa-exclamation-triangle"></i></div>
                    <h3>Failed to Load Dashboard</h3>
                    <p class="empty-state-text">${error.message}</p>
                    <button class="btn btn-primary" onclick="Dashboard.renderAdminDashboard()">Retry</button>
                </div>
            `;
        }
    },

    renderSkillsRadarChart(userSkills) {
        const ctx = document.getElementById('skillsRadarChart');
        if (!ctx || !userSkills || userSkills.length < 3) return;

        const topSkills = userSkills.slice(0, 8);
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: topSkills.map(s => s.skill?.name || 'Skill'),
                datasets: [{
                    label: 'Proficiency',
                    data: topSkills.map(s => (s.proficiency || 3) * 20),
                    backgroundColor: 'rgba(124, 58, 237, 0.15)',
                    borderColor: '#8b5cf6',
                    borderWidth: 2,
                    pointBackgroundColor: '#8b5cf6',
                    pointBorderColor: '#1a1a2e',
                    pointRadius: 4,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { display: false },
                        grid: { color: 'rgba(148, 163, 184, 0.15)' },
                        pointLabels: { color: '#94a3b8', font: { size: 11 } }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    },

    renderProfileGauge(score) {
        const gauge = document.getElementById('profileGauge');
        if (!gauge) return;
        
        const circumference = 2 * Math.PI * 85; // 534
        const offset = circumference - (score / 100) * circumference;
        
        // Animate the gauge
        setTimeout(() => {
            gauge.style.strokeDashoffset = offset;
        }, 500);
    },

    renderApplicationStatusChart(statusCounts) {
        const ctx = document.getElementById('appStatusChart');
        if (!ctx) return;

        const labels = {
            pending: 'Pending', reviewing: 'Reviewing', shortlisted: 'Shortlisted',
            interviewed: 'Interviewed', rejected: 'Rejected', offered: 'Offered', accepted: 'Accepted'
        };
        const colors = {
            pending: '#f59e0b', reviewing: '#3b82f6', shortlisted: '#8b5cf6',
            interviewed: '#06b6d4', rejected: '#ef4444', offered: '#10b981', accepted: '#10b981'
        };

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(statusCounts).map(k => labels[k] || k),
                datasets: [{
                    data: Object.values(statusCounts),
                    backgroundColor: Object.keys(statusCounts).map(k => colors[k] || '#64748b'),
                    borderWidth: 2,
                    borderColor: '#1a1a2e',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 16 } }
                }
            }
        });
    },

    renderJobStatsChart(jobs) {
        const ctx = document.getElementById('jobStatsChart');
        if (!ctx || !jobs) return;

        const statusCounts = {};
        jobs.forEach(j => {
            statusCounts[j.status] = (statusCounts[j.status] || 0) + 1;
        });

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(statusCounts),
                datasets: [{
                    label: 'Jobs',
                    data: Object.values(statusCounts),
                    backgroundColor: ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444'],
                    borderRadius: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true, ticks: { color: '#64748b', stepSize: 1 } },
                    x: { ticks: { color: '#94a3b8' } }
                }
            }
        });
    },

    renderUsersByRoleChart(candidates, recruiters, total) {
        const ctx = document.getElementById('usersByRoleChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Candidates', 'Recruiters'],
                datasets: [{
                    data: [candidates || 0, recruiters || 0],
                    backgroundColor: ['#8b5cf6', '#3b82f6'],
                    borderWidth: 2,
                    borderColor: '#1a1a2e',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 16 } }
                }
            }
        });
    },

    renderJobStatusChart(jobStatuses) {
        const ctx = document.getElementById('jobStatusChart');
        if (!ctx || !jobStatuses) return;

        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(jobStatuses).map(k => k.charAt(0).toUpperCase() + k.slice(1)),
                datasets: [{
                    data: Object.values(jobStatuses),
                    backgroundColor: ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#64748b'],
                    borderWidth: 2,
                    borderColor: '#1a1a2e',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 16 } }
                }
            }
        });
    }
};
