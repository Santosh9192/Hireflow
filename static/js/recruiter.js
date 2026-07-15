/*===========================================================
  HireFlow AI - Recruiter Module
  Job posting management, application review, interviews
===========================================================*/

const Recruiter = {
    async renderJobList() {
        Pages.render(`
            <div class="page-header animate-fade-in">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h1 class="page-title">My Jobs</h1>
                        <p class="page-subtitle">Manage your job postings</p>
                    </div>
                    <a href="#post-job" class="btn btn-primary"><i class="fas fa-plus"></i> Post New Job</a>
                </div>
            </div>
            <div id="jobsContent" class="animate-fade-in-up">
                <div class="loading-center"><div class="spinner"></div><div class="loading-text">Loading jobs...</div></div>
            </div>
        `);

        try {
            const result = await API.getRecruiterJobs({ per_page: 50 });
            const jobs = result.data || [];
            const container = document.getElementById('jobsContent');

            if (jobs.length === 0) {
                container.innerHTML = `
                    <div class="glass-card">
                        <div class="empty-state">
                            <div class="empty-state-icon"><i class="fas fa-briefcase"></i></div>
                            <h3>No Jobs Posted</h3>
                            <p class="empty-state-text">Post your first job to start receiving applications.</p>
                        </div>
                    </div>
                `;
                return;
            }

            container.innerHTML = `
                <div class="glass-card">
                    <div class="table-container" style="border: none;">
                        <table class="responsive-table">
                            <thead>
                                <tr>
                                    <th>Title</th>
                                    <th>Status</th>
                                    <th>Applications</th>
                                    <th>Views</th>
                                    <th>Posted</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${jobs.map(job => `
                                <tr>
                                    <td data-label="Title"><strong>${UI.escapeHtml(job.title)}</strong></td>
                                    <td data-label="Status">${UI.renderBadge(job.status)}</td>
                                    <td data-label="Applications">${job.applications_count || 0}</td>
                                    <td data-label="Views">${job.views_count || 0}</td>
                                    <td data-label="Posted">${UI.formatDate(job.created_at)}</td>
                                    <td data-label="Actions">
                                        <div style="display: flex; gap: 0.25rem;">
                                            <button class="btn btn-ghost btn-sm" onclick="App.navigateTo('edit-job-${job.id}')">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                            <button class="btn btn-ghost btn-sm" onclick="Recruiter.deleteJob(${job.id})">
                                                <i class="fas fa-trash" style="color: var(--accent-red);"></i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>`).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        } catch (error) {
            document.getElementById('jobsContent').innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon"><i class="fas fa-exclamation-triangle"></i></div>
                    <h3>Failed to Load Jobs</h3>
                    <p class="empty-state-text">${error.message}</p>
                </div>
            `;
        }
    },

    async renderPostJob() {
        Pages.render(`
            <div class="page-header animate-fade-in">
                <h1 class="page-title">Post a New Job</h1>
                <p class="page-subtitle">Create a job listing to attract top talent</p>
            </div>
            <div class="glass-card animate-fade-in-up" style="max-width: 800px;">
                <form id="postJobForm" onsubmit="return Recruiter.handlePostJob(event)">
                    <div class="form-group">
                        <label class="form-label">Job Title *</label>
                        <input type="text" class="form-input" name="title" placeholder="e.g. Senior Full Stack Developer" required>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Employment Type</label>
                            <select class="form-select" name="employment_type">
                                <option value="full-time">Full-time</option>
                                <option value="part-time">Part-time</option>
                                <option value="contract">Contract</option>
                                <option value="internship">Internship</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Work Mode</label>
                            <select class="form-select" name="work_mode">
                                <option value="remote">Remote</option>
                                <option value="hybrid">Hybrid</option>
                                <option value="on-site">On-site</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Experience Level</label>
                            <select class="form-select" name="experience_level">
                                <option value="entry">Entry Level</option>
                                <option value="mid" selected>Mid Level</option>
                                <option value="senior">Senior</option>
                                <option value="lead">Lead</option>
                                <option value="executive">Executive</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Category</label>
                            <select class="form-select" name="category">
                                <option value="Engineering">Engineering</option>
                                <option value="Design">Design</option>
                                <option value="Data">Data</option>
                                <option value="Product">Product</option>
                                <option value="Marketing">Marketing</option>
                                <option value="Sales">Sales</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Location</label>
                            <input type="text" class="form-input" name="location" placeholder="e.g. San Francisco, CA">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Min Experience (years)</label>
                            <input type="number" class="form-input" name="min_experience" placeholder="e.g. 3">
                        </div>
                    </div>                        <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Salary Min (₹/year)</label>
                            <input type="number" class="form-input" name="salary_min" placeholder="e.g. 800000">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Salary Max (₹/year)</label>
                            <input type="number" class="form-input" name="salary_max" placeholder="e.g. 2500000">
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Required Skills (comma separated)</label>
                        <input type="text" class="form-input" name="required_skills" placeholder="e.g. Python, React, AWS, Docker">
                    </div>

                    <div class="form-group">
                        <label class="form-label">Job Description *</label>
                        <textarea class="form-input" name="description" rows="6" 
                                  placeholder="Describe the role, responsibilities, and what makes this opportunity great..." required></textarea>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Requirements</label>
                        <textarea class="form-input" name="requirements" rows="4" 
                                  placeholder="List the key requirements and qualifications..."></textarea>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Benefits</label>
                        <textarea class="form-input" name="benefits" rows="3" 
                                  placeholder="Describe the benefits and perks..."></textarea>
                    </div>

                    <div style="display: flex; gap: 0.5rem; padding-top: 1rem; border-top: 1px solid var(--border-color);">
                        <button type="submit" class="btn btn-primary btn-lg">
                            <i class="fas fa-paper-plane"></i> Post Job
                        </button>
                        <button type="button" class="btn btn-secondary btn-lg" onclick="App.navigateTo('recruiter-jobs')">
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        `);
    },

    async handlePostJob(event) {
        event.preventDefault();
        const form = event.target;
        const data = new FormData(form);
        
        UI.showLoading(true);

        try {
            const jobData = {
                title: data.get('title'),
                description: data.get('description'),
                employment_type: data.get('employment_type'),
                work_mode: data.get('work_mode'),
                experience_level: data.get('experience_level'),
                category: data.get('category'),
                location: data.get('location'),
                min_experience: parseInt(data.get('min_experience')) || null,
                salary_min: parseInt(data.get('salary_min')) || null,
                salary_max: parseInt(data.get('salary_max')) || null,
                required_skills: data.get('required_skills'),
                requirements: data.get('requirements'),
                benefits: data.get('benefits'),
                status: 'active',
            };

            await API.createJob(jobData);
            UI.showToast('Job posted successfully!', 'success');
            App.navigateTo('recruiter-jobs');
        } catch (error) {
            UI.showToast(error.message, 'error');
        } finally {
            UI.showLoading(false);
        }

        return false;
    },

    async renderEditJob(jobId) {
        // Load job and show edit form
        try {
            const result = await API.getJob(jobId);
            const job = result.data;
            
            Pages.render(`
                <div class="page-header animate-fade-in">
                    <h1 class="page-title">Edit Job</h1>
                    <p class="page-subtitle">Update your job listing</p>
                </div>
                <div class="glass-card animate-fade-in-up" style="max-width: 800px;">
                    <form id="editJobForm" onsubmit="return Recruiter.handleEditJob(event, ${jobId})">
                        <!-- Same form as post job, pre-filled -->
                        ${this.renderJobEditForm(job)}
                    </form>
                </div>
            `);
        } catch (error) {
            UI.showToast(error.message, 'error');
            App.navigateTo('recruiter-jobs');
        }
    },

    renderJobEditForm(job) {
        return `
            <div class="form-group">
                <label class="form-label">Job Title *</label>
                <input type="text" class="form-input" name="title" value="${UI.escapeHtml(job.title || '')}" required>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Employment Type</label>
                    <select class="form-select" name="employment_type">
                        ${['full-time', 'part-time', 'contract', 'internship'].map(t => 
                            `<option value="${t}" ${job.employment_type === t ? 'selected' : ''}>${t}</option>`
                        ).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Work Mode</label>
                    <select class="form-select" name="work_mode">
                        ${['remote', 'hybrid', 'on-site'].map(m => 
                            `<option value="${m}" ${job.work_mode === m ? 'selected' : ''}>${m}</option>`
                        ).join('')}
                    </select>
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">Job Description *</label>
                <textarea class="form-input" name="description" rows="6" required>${UI.escapeHtml(job.description || '')}</textarea>
            </div>
            <div class="form-group">
                <label class="form-label">Status</label>
                <select class="form-select" name="status">
                    <option value="active" ${job.status === 'active' ? 'selected' : ''}>Active</option>
                    <option value="paused" ${job.status === 'paused' ? 'selected' : ''}>Paused</option>
                    <option value="closed" ${job.status === 'closed' ? 'selected' : ''}>Closed</option>
                </select>
            </div>
            <div style="display: flex; gap: 0.5rem; padding-top: 1rem; border-top: 1px solid var(--border-color);">
                <button type="submit" class="btn btn-primary"><i class="fas fa-save"></i> Save Changes</button>
                <button type="button" class="btn btn-secondary" onclick="App.navigateTo('recruiter-jobs')">Cancel</button>
            </div>
        `;
    },

    async handleEditJob(event, jobId) {
        event.preventDefault();
        const form = event.target;
        const data = new FormData(form);
        
        UI.showLoading(true);

        try {
            await API.updateJob(jobId, {
                title: data.get('title'),
                description: data.get('description'),
                employment_type: data.get('employment_type'),
                work_mode: data.get('work_mode'),
                status: data.get('status'),
            });
            UI.showToast('Job updated successfully!', 'success');
            App.navigateTo('recruiter-jobs');
        } catch (error) {
            UI.showToast(error.message, 'error');
        } finally {
            UI.showLoading(false);
        }

        return false;
    },

    async deleteJob(jobId) {
        if (!confirm('Are you sure you want to delete this job? This action cannot be undone.')) return;
        
        try {
            await API.deleteJob(jobId);
            UI.showToast('Job deleted successfully', 'success');
            this.renderJobList();
        } catch (error) {
            UI.showToast(error.message, 'error');
        }
    },

    async renderApplications() {
        Pages.render(`
            <div class="page-header animate-fade-in">
                <h1 class="page-title">Applications</h1>
                <p class="page-subtitle">Review and manage candidate applications</p>
            </div>
            <div class="search-filter-bar animate-fade-in-up">
                <select class="form-select" style="width: auto;" onchange="Recruiter.filterApplications()" id="appFilter">
                    <option value="">All Status</option>
                    <option value="pending">Pending</option>
                    <option value="reviewing">Reviewing</option>
                    <option value="shortlisted">Shortlisted</option>
                    <option value="rejected">Rejected</option>
                </select>
            </div>
            <div id="appsContent" class="animate-fade-in-up">
                <div class="loading-center"><div class="spinner"></div><div class="loading-text">Loading applications...</div></div>
            </div>
        `);
        await this.loadApplications();
    },

    async loadApplications() {
        try {
            const filter = document.getElementById('appFilter');
            const params = { per_page: 50 };
            if (filter?.value) params.status = filter.value;

            const result = await API.getRecruiterApplications(params);
            const apps = result.data || [];
            const container = document.getElementById('appsContent');

            if (apps.length === 0) {
                container.innerHTML = `
                    <div class="glass-card">
                        <div class="empty-state">
                            <div class="empty-state-icon"><i class="fas fa-inbox"></i></div>
                            <h3>No Applications</h3>
                            <p class="empty-state-text">Applications will appear here when candidates apply.</p>
                        </div>
                    </div>
                `;
                return;
            }

            container.innerHTML = `
                <div class="glass-card">
                    <div class="table-container" style="border: none;">
                        <table class="responsive-table">
                            <thead>
                                <tr><th>Candidate</th><th>Position</th><th>Status</th><th>Applied</th><th>Actions</th></tr>
                            </thead>
                            <tbody>
                                ${apps.map(app => `
                                <tr>
                                    <td data-label="Candidate">
                                        <strong>${UI.escapeHtml(app.candidate?.user?.full_name || 'Unknown')}</strong>
                                        <div style="font-size: 0.8rem; color: var(--text-muted);">
                                            ${UI.escapeHtml(app.candidate?.headline || '')}
                                        </div>
                                    </td>
                                    <td data-label="Position">${UI.escapeHtml(app.job?.title || 'N/A')}</td>
                                    <td data-label="Status">${UI.renderBadge(app.status)}</td>
                                    <td data-label="Applied">${UI.formatDate(app.created_at)}</td>
                                    <td data-label="Actions">
                                        <div style="display: flex; gap: 0.25rem; flex-wrap: wrap;">
                                            <button class="btn btn-sm ${app.status === 'shortlisted' ? 'btn-success' : 'btn-ghost'}" 
                                                    onclick="Recruiter.updateAppStatus(${app.id}, 'shortlisted')">
                                                <i class="fas fa-star"></i>
                                            </button>
                                            <button class="btn btn-sm ${app.status === 'rejected' ? 'btn-danger' : 'btn-ghost'}" 
                                                    onclick="Recruiter.updateAppStatus(${app.id}, 'rejected')">
                                                <i class="fas fa-times"></i>
                                            </button>
                                            <button class="btn btn-ghost btn-sm" onclick="Recruiter.scheduleInterview(${app.id})">
                                                <i class="fas fa-calendar"></i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>`).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        } catch (error) {
            document.getElementById('appsContent').innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon"><i class="fas fa-exclamation-triangle"></i></div>
                    <h3>Failed to Load Applications</h3>
                    <p class="empty-state-text">${error.message}</p>
                </div>
            `;
        }
    },

    filterApplications() {
        this.loadApplications();
    },

    async updateAppStatus(appId, status) {
        const reason = status === 'rejected' ? prompt('Rejection reason (optional):') : '';
        
        try {
            await API.updateApplicationStatus(appId, { status, rejection_reason: reason });
            UI.showToast(`Application ${status}`, 'success');
            this.loadApplications();
        } catch (error) {
            UI.showToast(error.message, 'error');
        }
    },

    async scheduleInterview(appId) {
        UI.showModal(`
            <div class="modal">
                <div class="modal-header">
                    <h3 class="modal-title">Schedule Interview</h3>
                    <button class="modal-close" onclick="UI.closeModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="interviewForm">
                        <input type="hidden" name="application_id" value="${appId}">
                        <div class="form-group">
                            <label class="form-label">Interview Title *</label>
                            <input type="text" class="form-input" name="title" placeholder="e.g. Technical Interview" required>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">Date *</label>
                                <input type="date" class="form-input" name="proposed_date" required>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Time *</label>
                                <input type="time" class="form-input" name="proposed_time" required>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Type</label>
                            <select class="form-select" name="interview_type">
                                <option value="video">Video Call</option>
                                <option value="phone">Phone Call</option>
                                <option value="in-person">In Person</option>
                                <option value="technical">Technical</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Meeting Link / Location</label>
                            <input type="text" class="form-input" name="meeting_link" placeholder="e.g. https://meet.google.com/...">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Duration (minutes)</label>
                            <input type="number" class="form-input" name="duration_minutes" value="60" min="15" step="15">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
                    <button class="btn btn-primary" onclick="Recruiter.sendInterview()">Send Invitation</button>
                </div>
            </div>
        `);
    },

    async sendInterview() {
        const form = document.getElementById('interviewForm');
        if (!form) return;
        
        const data = new FormData(form);
        UI.showLoading(true);

        try {
            await API.createInterview({
                application_id: parseInt(data.get('application_id')),
                title: data.get('title'),
                proposed_date: data.get('proposed_date'),
                proposed_time: data.get('proposed_time'),
                interview_type: data.get('interview_type'),
                meeting_link: data.get('meeting_link'),
                duration_minutes: parseInt(data.get('duration_minutes')) || 60,
            });
            UI.showToast('Interview invitation sent!', 'success');
            UI.closeModal();
        } catch (error) {
            UI.showToast(error.message, 'error');
        } finally {
            UI.showLoading(false);
        }
    },

    async renderInterviews() {
        Pages.render(`
            <div class="page-header animate-fade-in">
                <h1 class="page-title">Interviews</h1>
                <p class="page-subtitle">Manage interview invitations</p>
            </div>
            <div id="interviewsContent" class="animate-fade-in-up">
                <div class="loading-center"><div class="spinner"></div><div class="loading-text">Loading interviews...</div></div>
            </div>
        `);

        try {
            const result = await API.getInterviews();
            const interviews = result.data || [];
            const container = document.getElementById('interviewsContent');

            if (interviews.length === 0) {
                container.innerHTML = `
                    <div class="glass-card">
                        <div class="empty-state">
                            <div class="empty-state-icon"><i class="fas fa-calendar"></i></div>
                            <h3>No Interviews Scheduled</h3>
                            <p class="empty-state-text">Schedule interviews with shortlisted candidates.</p>
                        </div>
                    </div>
                `;
                return;
            }

            container.innerHTML = `
                <div style="display: grid; gap: 1rem;">
                    ${interviews.map(iv => `
                    <div class="glass-card interview-card ${iv.interview_type}">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <h4 style="margin-bottom: 0.25rem;">${UI.escapeHtml(iv.title)}</h4>
                                <p style="color: var(--text-secondary); margin: 0;">
                                    ${UI.escapeHtml(iv.candidate?.user?.full_name || 'Unknown')}
                                </p>
                            </div>
                            ${UI.renderBadge(iv.status)}
                        </div>
                        <div style="display: flex; gap: 1rem; margin-top: 1rem; flex-wrap: wrap;">
                            <span class="job-detail-tag"><i class="fas fa-calendar"></i> ${iv.proposed_date || ''}</span>
                            <span class="job-detail-tag"><i class="fas fa-clock"></i> ${iv.proposed_time || ''}</span>
                            <span class="job-detail-tag"><i class="fas fa-video"></i> ${iv.interview_type || ''}</span>
                            <span class="job-detail-tag"><i class="fas fa-hourglass"></i> ${iv.duration_minutes || 60} min</span>
                        </div>
                        ${iv.meeting_link ? `
                        <div style="margin-top: 0.75rem;">
                            <a href="${UI.escapeHtml(iv.meeting_link)}" target="_blank" class="btn btn-sm btn-primary">
                                <i class="fas fa-video"></i> Join Meeting
                            </a>
                        </div>` : ''}
                    </div>`).join('')}
                </div>
            `;
        } catch (error) {
            document.getElementById('interviewsContent').innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon"><i class="fas fa-exclamation-triangle"></i></div>
                    <h3>Failed to Load Interviews</h3>
                    <p class="empty-state-text">${error.message}</p>
                </div>
            `;
        }
    }
};
