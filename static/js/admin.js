/*===========================================================
  HireFlow AI - Admin Module
  System administration and management features
===========================================================*/

const Admin = {
    async renderUsers() {
        Pages.render(`
            <div class="page-header animate-fade-in">
                <h1 class="page-title">User Management</h1>
                <p class="page-subtitle">Manage all platform users</p>
            </div>
            <div class="search-filter-bar animate-fade-in-up">
                <div class="search-box">
                    <i class="fas fa-search"></i>
                    <input type="text" placeholder="Search users..." id="userSearch"
                           onkeyup="if(event.key==='Enter') Admin.loadUsers()">
                </div>
                <select class="form-select" style="width: auto;" onchange="Admin.loadUsers()" id="roleFilter">
                    <option value="">All Roles</option>
                    <option value="candidate">Candidates</option>
                    <option value="recruiter">Recruiters</option>
                    <option value="admin">Admins</option>
                </select>
            </div>
            <div id="usersContent" class="animate-fade-in-up">
                <div class="loading-center"><div class="spinner"></div><div class="loading-text">Loading users...</div></div>
            </div>
        `);
        await this.loadUsers();
    },

    async loadUsers() {
        try {
            const search = document.getElementById('userSearch')?.value;
            const role = document.getElementById('roleFilter')?.value;
            const params = { per_page: 50 };
            if (search) params.search = search;
            if (role) params.role = role;

            const result = await API.getAdminUsers(params);
            const users = result.data || [];
            const container = document.getElementById('usersContent');

            container.innerHTML = `
                <div class="glass-card">
                    <div class="table-container" style="border: none;">
                        <table class="responsive-table">
                            <thead>
                                <tr><th>User</th><th>Email</th><th>Role</th><th>Status</th><th>Joined</th><th>Actions</th></tr>
                            </thead>
                            <tbody>
                                ${users.map(user => `
                                <tr>
                                    <td data-label="User">
                                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                                            <div class="user-avatar-placeholder" style="width: 32px; height: 32px; font-size: 0.75rem;">
                                                ${(user.first_name?.[0] || '') + (user.last_name?.[0] || '')}
                                            </div>
                                            <strong>${UI.escapeHtml(user.full_name || 'Unknown')}</strong>
                                        </div>
                                    </td>
                                    <td data-label="Email">${UI.escapeHtml(user.email)}</td>
                                    <td data-label="Role"><span class="badge badge-primary">${user.role}</span></td>
                                    <td data-label="Status">
                                        <span class="badge ${user.is_active ? 'badge-success' : 'badge-danger'}">
                                            ${user.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td data-label="Joined">${UI.formatDate(user.created_at)}</td>
                                    <td data-label="Actions">
                                        <button class="btn btn-ghost btn-sm" onclick="Admin.toggleUserStatus(${user.id}, ${!user.is_active})">
                                            <i class="fas ${user.is_active ? 'fa-ban' : 'fa-check'}" 
                                               style="color: ${user.is_active ? 'var(--accent-red)' : 'var(--accent-green)'}"></i>
                                        </button>
                                    </td>
                                </tr>`).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        } catch (error) {
            document.getElementById('usersContent').innerHTML = `
                <div class="empty-state"><div class="empty-state-icon"><i class="fas fa-exclamation-triangle"></i></div>
                <h3>Failed to Load Users</h3><p class="empty-state-text">${error.message}</p></div>`;
        }
    },

    async toggleUserStatus(userId, newStatus) {
        try {
            await API.updateUser(userId, { is_active: newStatus });
            UI.showToast(`User ${newStatus ? 'activated' : 'deactivated'}`, 'success');
            this.loadUsers();
        } catch (error) {
            UI.showToast(error.message, 'error');
        }
    },

    async renderJobs() {
        Pages.render(`
            <div class="page-header animate-fade-in">
                <h1 class="page-title">All Jobs</h1>
                <p class="page-subtitle">Manage all platform job listings</p>
            </div>
            <div id="jobsContent" class="animate-fade-in-up">
                <div class="loading-center"><div class="spinner"></div><div class="loading-text">Loading jobs...</div></div>
            </div>
        `);

        try {
            const result = await API.getAdminJobs({ per_page: 50 });
            const jobs = result.data || [];
            const container = document.getElementById('jobsContent');

            container.innerHTML = `
                <div class="glass-card">
                    <div class="table-container" style="border: none;">
                        <table class="responsive-table">
                            <thead>
                                <tr><th>Title</th><th>Company</th><th>Posted By</th><th>Status</th><th>Posted</th><th>Actions</th></tr>
                            </thead>
                            <tbody>
                                ${jobs.map(job => `
                                <tr>
                                    <td data-label="Title"><strong>${UI.escapeHtml(job.title)}</strong></td>
                                    <td data-label="Company">${UI.escapeHtml(job.company?.name || 'N/A')}</td>
                                    <td data-label="Posted By">${UI.escapeHtml(job.poster_name?.full_name || 'N/A')}</td>
                                    <td data-label="Status">${UI.renderBadge(job.status)}</td>
                                    <td data-label="Posted">${UI.formatDate(job.created_at)}</td>
                                    <td data-label="Actions">
                                        <button class="btn btn-ghost btn-sm" onclick="Admin.toggleJobStatus(${job.id}, '${job.status === 'active' ? 'closed' : 'active'}')">
                                            <i class="fas ${job.status === 'active' ? 'fa-ban' : 'fa-check'}" 
                                               style="color: ${job.status === 'active' ? 'var(--accent-red)' : 'var(--accent-green)'}"></i>
                                        </button>
                                    </td>
                                </tr>`).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        } catch (error) {
            document.getElementById('jobsContent').innerHTML = `
                <div class="empty-state"><div class="empty-state-icon"><i class="fas fa-exclamation-triangle"></i></div>
                <h3>Failed to Load Jobs</h3><p class="empty-state-text">${error.message}</p></div>`;
        }
    },

    async toggleJobStatus(jobId, newStatus) {
        try {
            await API.updateJob(jobId, { status: newStatus });
            UI.showToast(`Job ${newStatus}`, 'success');
            this.renderJobs();
        } catch (error) {
            UI.showToast(error.message, 'error');
        }
    },

    async renderLogs() {
        Pages.render(`
            <div class="page-header animate-fade-in">
                <h1 class="page-title">Activity Logs</h1>
                <p class="page-subtitle">System audit trail</p>
            </div>
            <div class="search-filter-bar animate-fade-in-up">
                <div class="search-box">
                    <i class="fas fa-search"></i>
                    <input type="text" placeholder="Search logs..." id="logSearch"
                           onkeyup="if(event.key==='Enter') Admin.loadLogs()">
                </div>
            </div>
            <div id="logsContent" class="animate-fade-in-up">
                <div class="loading-center"><div class="spinner"></div><div class="loading-text">Loading logs...</div></div>
            </div>
        `);
        await this.loadLogs();
    },

    async loadLogs() {
        try {
            const result = await API.getSystemLogs({ per_page: 100 });
            const logs = result.data || [];
            const container = document.getElementById('logsContent');

            if (logs.length === 0) {
                container.innerHTML = `
                    <div class="glass-card"><div class="empty-state">
                        <div class="empty-state-icon"><i class="fas fa-history"></i></div>
                        <h3>No Logs</h3></div></div>`;
                return;
            }

            container.innerHTML = `
                <div class="glass-card">
                    <div class="table-container" style="border: none;">
                        <table class="responsive-table">
                            <thead>
                                <tr><th>Time</th><th>User</th><th>Action</th><th>Resource</th><th>IP</th></tr>
                            </thead>
                            <tbody>
                                ${logs.map(log => `
                                <tr>
                                    <td data-label="Time">${UI.formatDate(log.created_at)}</td>
                                    <td data-label="User">${UI.escapeHtml(log.user?.full_name || 'System')}</td>
                                    <td data-label="Action"><span class="badge badge-info">${log.action}</span></td>
                                    <td data-label="Resource">${log.resource_type || '-'} #${log.resource_id || ''}</td>
                                    <td data-label="IP" style="font-family: monospace; font-size: 0.8rem;">${log.ip_address || '-'}</td>
                                </tr>`).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        } catch (error) {
            document.getElementById('logsContent').innerHTML = `
                <div class="empty-state"><div class="empty-state-icon"><i class="fas fa-exclamation-triangle"></i></div>
                <h3>Failed to Load Logs</h3><p class="empty-state-text">${error.message}</p></div>`;
        }
    }
};
