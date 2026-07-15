/*===========================================================
  HireFlow AI - Jobs Module
  Job listing, detail, and application management
===========================================================*/

const Jobs = {
    currentPage: 1,
    jobsCache: null,

    async renderJobList(query = '') {
        Pages.render(`
            <div class="page-header animate-fade-in">
                <h1 class="page-title">Browse Jobs</h1>
                <p class="page-subtitle">Find your next opportunity</p>
            </div>

            <div class="search-filter-bar animate-fade-in-up">
                <div class="search-box">
                    <i class="fas fa-search"></i>
                    <input type="text" placeholder="Search jobs..." 
                           value="${UI.escapeHtml(query)}" 
                           onkeyup="Jobs.handleSearch(event)" id="jobSearch">
                </div>
                <select class="form-select" style="width: auto;" onchange="Jobs.filterChanged()" id="filterType">
                    <option value="">All Types</option>
                    <option value="full-time">Full-time</option>
                    <option value="part-time">Part-time</option>
                    <option value="contract">Contract</option>
                    <option value="internship">Internship</option>
                </select>
                <select class="form-select" style="width: auto;" onchange="Jobs.filterChanged()" id="filterRemote">
                    <option value="">All Modes</option>
                    <option value="remote">Remote</option>
                    <option value="hybrid">Hybrid</option>
                    <option value="on-site">On-site</option>
                </select>
                <select class="form-select" style="width: auto;" onchange="Jobs.filterChanged()" id="filterLevel">
                    <option value="">All Levels</option>
                    <option value="entry">Entry Level</option>
                    <option value="mid">Mid Level</option>
                    <option value="senior">Senior</option>
                    <option value="lead">Lead</option>
                </select>
                <select class="form-select" style="width: auto;" onchange="Jobs.filterChanged()" id="filterSalary">
                    <option value="">Any Salary</option>
                    <option value="0-500000">Under ₹5 Lakhs</option>
                    <option value="500000-1000000">₹5 - 10 Lakhs</option>
                    <option value="1000000-2000000">₹10 - 20 Lakhs</option>
                    <option value="2000000-5000000">₹20 - 50 Lakhs</option>
                    <option value="5000000+">₹50 Lakhs+</option>
                </select>
            </div>

            <div id="jobsContainer" class="animate-fade-in-up">
                <div class="loading-center">
                    <div class="spinner"></div>
                    <div class="loading-text">Finding jobs for you...</div>
                </div>
            </div>

            <div id="pagination" class="pagination" style="display: none;"></div>
        `);

        await this.loadJobs(query);
    },

    async loadJobs(query = '', page = 1) {
        const container = document.getElementById('jobsContainer');
        if (!container) return;

        try {
            const params = { page, per_page: 12 };
            const searchInput = document.getElementById('jobSearch');
            if (searchInput?.value) params.search = searchInput.value;
            
            const typeFilter = document.getElementById('filterType');
            if (typeFilter?.value) params.employment_type = typeFilter.value;
            
            const remoteFilter = document.getElementById('filterRemote');
            if (remoteFilter?.value) params.work_mode = remoteFilter.value;
            
            const levelFilter = document.getElementById('filterLevel');
            if (levelFilter?.value) params.experience_level = levelFilter.value;
            
            const salaryFilter = document.getElementById('filterSalary');
            if (salaryFilter?.value) {
                const parts = salaryFilter.value.split('-');
                if (parts[0]) params.salary_min = parseInt(parts[0]);
                if (parts[1]) params.salary_max = parseInt(parts[1]);
            }

            const result = await API.getJobs(params);
            const jobs = result.data || [];
            const meta = result.meta || {};

            if (jobs.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon"><i class="fas fa-search"></i></div>
                        <h3>No Jobs Found</h3>
                        <p class="empty-state-text">Try adjusting your search or filters</p>
                    </div>
                `;
                return;
            }

            container.innerHTML = `
                <div style="margin-bottom: 1rem;">
                    <span style="color: var(--text-secondary);">${meta.total || jobs.length} jobs found</span>
                </div>
                <div class="jobs-grid">
                    ${jobs.map(job => this.renderJobCard(job)).join('')}
                </div>
            `;

            // Pagination
            this.renderPagination(meta);

        } catch (error) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon"><i class="fas fa-exclamation-triangle"></i></div>
                    <h3>Failed to Load Jobs</h3>
                    <p class="empty-state-text">${error.message}</p>
                    <button class="btn btn-primary" onclick="Jobs.loadJobs()">Retry</button>
                </div>
            `;
        }
    },

    renderJobCard(job) {
        const companyName = job.company?.name || 'Unknown Company';
        const initial = companyName.charAt(0).toUpperCase();
        const salary = UI.formatSalary(job.salary_min, job.salary_max, job.salary_period);

        return `
            <div class="job-card" onclick="Jobs.showJobDetail(${job.id})">
                <div class="job-card-header">
                    <div class="job-card-company">
                        <div class="company-logo">${initial}</div>
                        <div>
                            <div class="job-card-title">${UI.escapeHtml(job.title)}</div>
                            <div class="job-card-company-name">${UI.escapeHtml(companyName)}</div>
                        </div>
                    </div>
                    ${job.is_featured ? '<span class="badge badge-primary">Featured</span>' : ''}
                </div>

                <div class="job-card-details">
                    ${job.location ? `
                    <span class="job-detail-tag">
                        <i class="fas fa-map-marker-alt"></i> ${UI.escapeHtml(job.location)}
                    </span>` : ''}
                    ${job.employment_type ? `
                    <span class="job-detail-tag">
                        <i class="fas fa-clock"></i> ${job.employment_type}
                    </span>` : ''}
                    ${job.work_mode ? `
                    <span class="job-detail-tag">
                        <i class="fas fa-wifi"></i> ${job.work_mode}
                    </span>` : ''}
                    ${job.experience_level ? `
                    <span class="job-detail-tag">
                        <i class="fas fa-layer-group"></i> ${job.experience_level}
                    </span>` : ''}
                </div>

                ${job.required_skills ? `
                <div style="margin-bottom: 1rem; display: flex; flex-wrap: wrap; gap: 0.25rem;">
                    ${(() => {
                        try {
                            const skills = typeof job.required_skills === 'string' 
                                ? JSON.parse(job.required_skills) 
                                : (job.required_skills || []);
                            return skills.slice(0, 4).map(s => 
                                `<span class="skill-tag" style="font-size: 0.75rem;">${s}</span>`
                            ).join('');
                        } catch { return ''; }
                    })()}
                </div>` : ''}

                <div class="job-card-footer">
                    <div class="job-card-salary">${salary}</div>
                    <div class="job-card-date">${UI.formatDate(job.created_at)}</div>
                </div>
            </div>
        `;
    },

    renderPagination(meta) {
        const paginationEl = document.getElementById('pagination');
        if (!paginationEl || !meta || meta.total_pages <= 1) return;

        paginationEl.style.display = 'flex';
        let html = `
            <button ${meta.page <= 1 ? 'disabled' : ''} onclick="Jobs.loadJobs('', ${meta.page - 1})">
                <i class="fas fa-chevron-left"></i>
            </button>
        `;

        for (let i = 1; i <= meta.total_pages; i++) {
            if (i === 1 || i === meta.total_pages || (i >= meta.page - 1 && i <= meta.page + 1)) {
                html += `<button class="${i === meta.page ? 'active' : ''}" 
                              onclick="Jobs.loadJobs('', ${i})">${i}</button>`;
            } else if (i === meta.page - 2 || i === meta.page + 2) {
                html += `<button disabled>...</button>`;
            }
        }

        html += `
            <button ${meta.page >= meta.total_pages ? 'disabled' : ''} 
                    onclick="Jobs.loadJobs('', ${meta.page + 1})">
                <i class="fas fa-chevron-right"></i>
            </button>
        `;

        paginationEl.innerHTML = html;
    },

    handleSearch(event) {
        if (event.key === 'Enter') {
            this.currentPage = 1;
            this.loadJobs();
        }
    },

    filterChanged() {
        this.currentPage = 1;
        this.loadJobs();
    },

    async showJobDetail(jobId) {
        Pages.render(`
            <div class="page-header animate-fade-in">
                <a href="#jobs" class="btn btn-ghost btn-sm"><i class="fas fa-arrow-left"></i> Back to Jobs</a>
            </div>
            <div id="jobDetailContent" class="animate-fade-in-up">
                <div class="loading-center">
                    <div class="spinner"></div>
                    <div class="loading-text">Loading job details...</div>
                </div>
            </div>
        `);

        try {
            const result = await API.getJob(jobId);
            const job = result.data;
            
            const companyName = job.company?.name || 'Unknown';
            const salary = UI.formatSalary(job.salary_min, job.salary_max, job.salary_period);

            let skills = [];
            try {
                skills = typeof job.required_skills === 'string' 
                    ? JSON.parse(job.required_skills) 
                    : (job.required_skills || []);
            } catch { skills = []; }

            const container = document.getElementById('jobDetailContent');
            container.innerHTML = `
                <div class="glass-card" style="margin-bottom: 1.5rem;">
                    <div class="job-card-header" style="margin-bottom: 1.5rem;">
                        <div class="job-card-company">
                            <div class="company-logo" style="width: 64px; height: 64px; font-size: 1.5rem;">
                                ${companyName.charAt(0).toUpperCase()}
                            </div>
                            <div>
                                <h2 style="margin-bottom: 0.25rem;">${UI.escapeHtml(job.title)}</h2>
                                <p style="color: var(--text-secondary); margin: 0;">${UI.escapeHtml(companyName)}</p>
                            </div>
                        </div>
                        <div style="display: flex; gap: 0.5rem;">
                            ${API.getToken() ? `
                            <button class="btn btn-primary" onclick="Jobs.applyForJob(${job.id})">
                                <i class="fas fa-paper-plane"></i> Apply Now
                            </button>
                            <button class="btn btn-ghost btn-icon" onclick="Jobs.saveJob(${job.id})">
                                <i class="far fa-bookmark"></i>
                            </button>` : `
                            <a href="#login" class="btn btn-primary">Sign in to Apply</a>`}
                        </div>
                    </div>

                    <div class="job-card-details" style="margin-bottom: 1.5rem;">
                        ${job.location ? `<span class="job-detail-tag"><i class="fas fa-map-marker-alt"></i> ${UI.escapeHtml(job.location)}</span>` : ''}
                        ${job.employment_type ? `<span class="job-detail-tag"><i class="fas fa-clock"></i> ${job.employment_type}</span>` : ''}
                        ${job.work_mode ? `<span class="job-detail-tag"><i class="fas fa-wifi"></i> ${job.work_mode}</span>` : ''}
                        ${job.experience_level ? `<span class="job-detail-tag"><i class="fas fa-layer-group"></i> ${job.experience_level}</span>` : ''}
                        ${salary ? `<span class="job-detail-tag" style="color: var(--accent-green);"><i class="fas fa-rupee-sign"></i> ${salary}</span>` : ''}
                        ${job.min_experience ? `<span class="job-detail-tag"><i class="fas fa-briefcase"></i> ${job.min_experience}-${job.max_experience || '∞'} yrs</span>` : ''}
                    </div>

                    <div style="display: grid; gap: 1.5rem;">
                        <div>
                            <h4>Description</h4>
                            <p style="color: var(--text-secondary); line-height: 1.7;">${UI.escapeHtml(job.description)}</p>
                        </div>

                        ${job.responsibilities ? `
                        <div>
                            <h4>Responsibilities</h4>
                            <p style="color: var(--text-secondary); white-space: pre-line;">${UI.escapeHtml(job.responsibilities)}</p>
                        </div>` : ''}

                        ${job.requirements ? `
                        <div>
                            <h4>Requirements</h4>
                            <p style="color: var(--text-secondary); white-space: pre-line;">${UI.escapeHtml(job.requirements)}</p>
                        </div>` : ''}

                        ${skills.length > 0 ? `
                        <div>
                            <h4>Required Skills</h4>
                            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                                ${skills.map(s => `<span class="skill-tag">${UI.escapeHtml(s)}</span>`).join('')}
                            </div>
                        </div>` : ''}

                        ${job.benefits ? `
                        <div>
                            <h4>Benefits</h4>
                            <p style="color: var(--text-secondary); white-space: pre-line;">${UI.escapeHtml(job.benefits)}</p>
                        </div>` : ''}
                    </div>

                    <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid var(--border-color);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="color: var(--text-muted); font-size: 0.875rem;">
                                    Posted ${UI.formatDate(job.created_at)} • ${job.views_count || 0} views
                                </span>
                            </div>
                            ${API.getToken() ? `
                            <button class="btn btn-primary" onclick="Jobs.applyForJob(${job.id})">
                                <i class="fas fa-paper-plane"></i> Apply Now
                            </button>` : `
                            <a href="#login" class="btn btn-primary">Sign in to Apply</a>`}
                        </div>
                    </div>
                </div>
            `;

            window.location.hash = `job-detail-${jobId}`;

        } catch (error) {
            document.getElementById('jobDetailContent').innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon"><i class="fas fa-exclamation-triangle"></i></div>
                    <h3>Failed to Load Job</h3>
                    <p class="empty-state-text">${error.message}</p>
                </div>
            `;
        }
    },

    async applyForJob(jobId) {
        try {
            // Get user's resumes
            const resumes = await API.getResumes();
            
            let modalHtml = `
                <div class="modal">
                    <div class="modal-header">
                        <h3 class="modal-title">Apply for this Job</h3>
                        <button class="modal-close" onclick="UI.closeModal()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <form id="applyForm">
                            <input type="hidden" name="job_id" value="${jobId}">
                            
                            <div class="form-group">
                                <label class="form-label">Resume</label>
                                ${resumes.data?.length > 0 ? `
                                <select class="form-select" name="resume_id">
                                    ${resumes.data.map((r, i) => `
                                        <option value="${r.id}" ${r.is_default ? 'selected' : ''}>
                                            ${UI.escapeHtml(r.title || r.original_filename)}
                                        </option>
                                    `).join('')}
                                </select>` : `
                                <p class="text-muted" style="font-size: 0.875rem;">
                                    No resumes uploaded. 
                                    <a href="#profile">Upload one first</a>
                                </p>
                                <input type="hidden" name="resume_id" value="">`}
                            </div>

                            <div class="form-group">
                                <label class="form-label">Cover Letter (Optional)</label>
                                <textarea class="form-input" name="cover_letter" 
                                          placeholder="Tell the employer why you're a great fit..." 
                                          rows="5"></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
                        <button class="btn btn-primary" onclick="Jobs.submitApplication()">
                            <i class="fas fa-paper-plane"></i> Submit Application
                        </button>
                    </div>
                </div>
            `;

            UI.showModal(modalHtml);

        } catch (error) {
            UI.showToast(error.message, 'error');
        }
    },

    async submitApplication() {
        const form = document.getElementById('applyForm');
        if (!form) return;

        const data = new FormData(form);
        UI.showLoading(true);

        try {
            const result = await API.apply({
                job_id: parseInt(data.get('job_id')),
                resume_id: data.get('resume_id') ? parseInt(data.get('resume_id')) : null,
                cover_letter: data.get('cover_letter'),
            });
            UI.showToast('Application submitted successfully!', 'success');
            UI.closeModal();
        } catch (error) {
            UI.showToast(error.message, 'error');
        } finally {
            UI.showLoading(false);
        }
    },

    async saveJob(jobId) {
        try {
            const result = await API.saveJob(jobId);
            UI.showToast(result.data?.saved ? 'Job saved!' : 'Job unsaved', 'success');
        } catch (error) {
            UI.showToast(error.message, 'error');
        }
    },

    async renderApplications() {
        Pages.render(`
            <div class="page-header animate-fade-in">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h1 class="page-title">My Applications</h1>
                        <p class="page-subtitle">Track your job applications</p>
                    </div>
                    <div class="export-dropdown">
                        <button class="btn btn-ghost btn-sm" onclick="this.nextElementSibling.classList.toggle('show')">
                            <i class="fas fa-download"></i> Export
                        </button>
                        <div class="export-menu">
                            <button class="export-item" onclick="Jobs.exportData('csv')">
                                <i class="fas fa-file-csv"></i> Export as CSV
                            </button>
                            <button class="export-item" onclick="Jobs.exportData('json')">
                                <i class="fas fa-file-code"></i> Export as JSON
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div id="appsContent" class="animate-fade-in-up">
                <div class="loading-center">
                    <div class="spinner"></div>
                    <div class="loading-text">Loading applications...</div>
                </div>
            </div>
        `);

        try {
            const result = await API.getApplications({ per_page: 20 });
            const apps = result.data || [];

            const container = document.getElementById('appsContent');
            if (apps.length === 0) {
                container.innerHTML = `
                    <div class="glass-card">
                        <div class="empty-state">
                            <div class="empty-state-icon"><i class="fas fa-paper-plane"></i></div>
                            <h3>No Applications Yet</h3>
                            <p class="empty-state-text">Start applying to jobs that match your skills!</p>
                            <a href="#jobs" class="btn btn-primary">Browse Jobs</a>
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
                                    <th>Position</th>
                                    <th>Company</th>
                                    <th>Status</th>
                                    <th>Applied</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${apps.map(app => `
                                <tr>
                                    <td data-label="Position">
                                        <strong>${UI.escapeHtml(app.job?.title || 'N/A')}</strong>
                                    </td>
                                    <td data-label="Company">${UI.escapeHtml(app.job?.company?.name || 'N/A')}</td>
                                    <td data-label="Status">${UI.renderBadge(app.status)}</td>
                                    <td data-label="Applied">${UI.formatDate(app.created_at)}</td>
                                    <td data-label="Actions">
                                        <div class="timeline" style="padding: 0;">
                                            <div class="timeline-item" style="padding-bottom: 0.5rem;">
                                                <div class="timeline-dot" style="width: 10px; height: 10px; left: 0;"></div>
                                                <div style="padding-left: 1.5rem;">
                                                    <div class="timeline-title" style="font-size: 0.8rem;">
                                                        ${app.status.charAt(0).toUpperCase() + app.status.slice(1)}
                                                    </div>
                                                    <div class="timeline-date">${UI.formatDate(app[app.status + '_at'] || app.created_at)}</div>
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                </tr>`).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>

                ${result.meta?.total_pages > 1 ? `
                <div class="pagination">
                    ${Array.from({length: result.meta.total_pages}, (_, i) => i + 1).map(p => `
                        <button class="${p === (result.meta.page || 1) ? 'active' : ''}" 
                                onclick="Jobs.renderApplications()">${p}</button>
                    `).join('')}
                </div>` : ''}
            `;

        } catch (error) {
            document.getElementById('appsContent').innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon"><i class="fas fa-exclamation-triangle"></i></div>
                    <h3>Failed to Load Applications</h3>
                    <p class="empty-state-text">${error.message}</p>
                    <button class="btn btn-primary" onclick="Jobs.renderApplications()">Retry</button>
                </div>
            `;
        }
    },

    async exportData(format) {
        // Close export menu
        document.querySelector('.export-menu.show')?.classList.remove('show');
        
        try {
            UI.showLoading(true);
            
            if (format === 'csv') {
                // Generate CSV from current data
                const result = await API.getApplications({ per_page: 100 });
                const apps = result.data || [];
                
                let csv = 'Job Title,Company,Status,Applied Date\n';
                apps.forEach(app => {
                    const title = (app.job?.title || 'N/A').replace(/,/g, ' ');
                    const company = (app.job?.company?.name || 'N/A').replace(/,/g, ' ');
                    csv += `${title},${company},${app.status},${app.created_at || ''}\n`;
                });
                
                // Download
                const blob = new Blob([csv], { type: 'text/csv' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'my-applications.csv';
                a.click();
                URL.revokeObjectURL(url);
            } else {
                // JSON export
                const result = await API.getApplications({ per_page: 100 });
                const blob = new Blob([JSON.stringify(result.data, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'my-applications.json';
                a.click();
                URL.revokeObjectURL(url);
            }
            
            UI.showToast(`Exported as ${format.toUpperCase()}`, 'success');
        } catch (error) {
            UI.showToast('Export failed: ' + error.message, 'error');
        } finally {
            UI.showLoading(false);
        }
    },

    async renderSavedJobs() {
        Pages.render(`
            <div class="page-header animate-fade-in">
                <h1 class="page-title">Saved Jobs</h1>
                <p class="page-subtitle">Jobs you've saved for later</p>
            </div>
            <div id="savedJobsContent" class="animate-fade-in-up">
                <div class="loading-center">
                    <div class="spinner"></div>
                    <div class="loading-text">Loading saved jobs...</div>
                </div>
            </div>
        `);

        try {
            const result = await API.getSavedJobs();
            const savedJobs = result.data || [];

            const container = document.getElementById('savedJobsContent');
            if (savedJobs.length === 0) {
                container.innerHTML = `
                    <div class="glass-card">
                        <div class="empty-state">
                            <div class="empty-state-icon"><i class="far fa-bookmark"></i></div>
                            <h3>No Saved Jobs</h3>
                            <p class="empty-state-text">Save jobs you're interested in to review them later.</p>
                            <a href="#jobs" class="btn btn-primary">Browse Jobs</a>
                        </div>
                    </div>
                `;
                return;
            }

            container.innerHTML = `
                <div class="jobs-grid">
                    ${savedJobs.map(sj => sj.job ? this.renderJobCard(sj.job) : '').join('')}
                </div>
            `;

        } catch (error) {
            document.getElementById('savedJobsContent').innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon"><i class="fas fa-exclamation-triangle"></i></div>
                    <h3>Failed to Load Saved Jobs</h3>
                    <p class="empty-state-text">${error.message}</p>
                </div>
            `;
        }
    }
};
