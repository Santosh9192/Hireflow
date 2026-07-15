/*===========================================================
  HireFlow AI - Profile Module
  User profile, resume management, and settings
===========================================================*/

const Profile = {
    async renderCandidateProfile() {
        Pages.render(`
            <div class="page-header animate-fade-in">
                <h1 class="page-title">My Profile</h1>
                <p class="page-subtitle">Manage your professional profile and resume</p>
            </div>
            <div id="profileContent" class="animate-fade-in-up">
                <div class="loading-center"><div class="spinner"></div><div class="loading-text">Loading profile...</div></div>
            </div>
        `);

        try {
            const [profileResult, resumesResult] = await Promise.all([
                API.getCandidateProfile().catch(err => { console.warn('Profile API error:', err); return { data: null }; }),
                API.getResumes().catch(err => { console.warn('Resumes API error:', err); return { data: [] }; })
            ]);

            const profile = profileResult?.data || {};
            const resumes = resumesResult?.data || [];
            const user = Store.get('user');
            const container = document.getElementById('profileContent');
            if (!container) return;

            // Safely get skills array
            const skills = Array.isArray(profile?.skills) ? profile.skills : [];

            container.innerHTML = `
                <!-- Profile Header -->
                <div class="profile-header glass-card" style="margin-bottom: 1.5rem;">
                    <div class="profile-avatar">
                        ${user?.profile_photo 
                            ? `<img src="${user.profile_photo}" alt="Profile Photo">`
                            : `<div class="user-avatar-placeholder" style="width: 100%; height: 100%; font-size: 2rem; border-radius: 50%;">
                                ${(user?.first_name?.[0] || '') + (user?.last_name?.[0] || '')}
                               </div>`}
                    </div>
                    <div class="profile-info">
                        <h2>${UI.escapeHtml(user?.full_name || 'User')}</h2>
                        <p>${UI.escapeHtml(profile?.headline || '')} ${profile?.headline ? '•' : ''} ${UI.escapeHtml(user?.email || '')}</p>
                        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                            ${profile?.is_open_to_work ? '<span class="badge badge-success">Open to Work</span>' : ''}
                            ${profile?.preferred_work_mode ? `<span class="badge badge-info">${UI.escapeHtml(profile.preferred_work_mode)}</span>` : ''}
                            ${profile?.preferred_employment_type ? `<span class="badge badge-primary">${UI.escapeHtml(profile.preferred_employment_type)}</span>` : ''}
                        </div>
                    </div>
                </div>

                <div class="dashboard-grid">
                    <!-- Profile Details -->
                    <div class="glass-card">
                        <div class="card-header">
                            <h3 class="card-title">Profile Information</h3>
                            <button class="btn btn-ghost btn-sm" onclick="Profile.showEditProfile()">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                        </div>
                        <div style="display: grid; gap: 1rem;">
                            <div>
                                <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.25rem;">Headline</div>
                                <div>${UI.escapeHtml(profile?.headline || 'Not set')}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.25rem;">Bio</div>
                                <div>${UI.escapeHtml(profile?.bio || 'No bio yet')}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.25rem;">Location Preference</div>
                                <div>${UI.escapeHtml(profile?.preferred_locations || 'Not specified')}</div>
                            </div>
                            ${profile?.preferred_salary_min ? `
                            <div>
                                <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.25rem;">Expected Salary</div>
                                <div>${UI.formatSalary(profile.preferred_salary_min, profile.preferred_salary_max, 'yearly', 'INR')}</div>
                            </div>` : ''}
                        </div>
                    </div>

                    <!-- Skills -->
                    <div class="glass-card">
                        <div class="card-header">
                            <h3 class="card-title">Skills (${skills.length})</h3>
                            <button class="btn btn-ghost btn-sm" onclick="Profile.showEditSkills()">
                                <i class="fas fa-plus"></i> Add
                            </button>
                        </div>
                        ${skills.length > 0 ? `
                        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                            ${skills.map(s => `<span class="skill-tag">${UI.escapeHtml(s?.skill?.name || '')}</span>`).join('')}
                        </div>` : `
                        <div class="empty-state" style="padding: 1rem;">
                            <div class="empty-state-text">No skills added yet</div>
                        </div>`}
                    </div>
                </div>

                <!-- Resumes -->
                <div class="glass-card" style="margin-top: 1.5rem;">
                    <div class="card-header">
                        <h3 class="card-title">Resumes</h3>
                        <button class="btn btn-primary btn-sm" onclick="Profile.showUploadResume()">
                            <i class="fas fa-upload"></i> Upload Resume
                        </button>
                    </div>
                    ${resumes.length > 0 ? `
                    <div style="display: grid; gap: 0.75rem;">
                        ${resumes.map(r => `
                        <div style="display: flex; justify-content: space-between; align-items: center; 
                                    padding: 1rem; background: var(--bg-card); border-radius: var(--radius-lg);">
                            <div style="display: flex; align-items: center; gap: 1rem;">
                                <div style="width: 40px; height: 40px; border-radius: var(--radius-lg);
                                            background: rgba(124,58,237,0.1); display: flex; align-items: center;
                                            justify-content: center; color: var(--primary-light);">
                                    <i class="fas fa-file-${r.file_type === 'pdf' ? 'pdf' : 'word'}"></i>
                                </div>
                                <div>
                                    <div style="font-weight: 500;">${UI.escapeHtml(r.title || r.original_filename)}</div>
                                    <div style="font-size: 0.8rem; color: var(--text-muted);">
                                        ${r.is_default ? '<span class="badge badge-success">Default</span>' : ''}
                                        ${r.ats_score ? `<span class="badge badge-primary">ATS: ${r.ats_score}</span>` : ''}
                                    </div>
                                </div>
                            </div>
                            <div style="display: flex; gap: 0.25rem;">
                                ${!r.is_default ? `<button class="btn btn-ghost btn-sm" onclick="Profile.setDefaultResume(${r.id})">
                                    <i class="fas fa-check"></i></button>` : ''}
                                <button class="btn btn-ghost btn-sm" onclick="Profile.deleteResume(${r.id})">
                                    <i class="fas fa-trash" style="color: var(--accent-red);"></i>
                                </button>
                            </div>
                        </div>`).join('')}
                    </div>` : `
                    <div class="empty-state">
                        <div class="empty-state-icon"><i class="fas fa-file-upload"></i></div>
                        <h3>No Resumes</h3>
                        <p class="empty-state-text">Upload your resume for AI-powered analysis and matching.</p>
                    </div>`}
                </div>
            `;

        } catch (error) {
            const container = document.getElementById('profileContent');
            if (container) {
                container.innerHTML = `
                    <div class="empty-state"><div class="empty-state-icon"><i class="fas fa-exclamation-triangle"></i></div>
                    <h3>Failed to Load Profile</h3><p class="empty-state-text">${UI.escapeHtml(error.message)}</p>
                    <button class="btn btn-primary" onclick="Profile.renderCandidateProfile()">Retry</button></div>`;
            }
        }
    },

    async renderGeneralProfile() {
        // For recruiter/admin profiles
        const user = Store.get('user');
        Pages.render(`
            <div class="page-header animate-fade-in">
                <h1 class="page-title">My Profile</h1>
            </div>
            <div class="glass-card animate-fade-in-up" style="max-width: 600px;">
                <div style="display: flex; align-items: center; gap: 1.5rem; margin-bottom: 2rem;">
                    <div class="profile-avatar" style="width: 80px; height: 80px;">
                        <div class="user-avatar-placeholder" style="width: 100%; height: 100%; font-size: 1.5rem;">
                            ${(user?.first_name?.[0] || '') + (user?.last_name?.[0] || '')}
                        </div>
                    </div>
                    <div>
                        <h2>${UI.escapeHtml(user?.full_name || 'User')}</h2>
                        <p style="color: var(--text-secondary);">${UI.escapeHtml(user?.email || '')}</p>
                        <span class="badge badge-primary">${user?.role}</span>
                    </div>
                </div>

                <form onsubmit="return Profile.handleUpdateProfile(event)">
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">First Name</label>
                            <input type="text" class="form-input" name="first_name" value="${UI.escapeHtml(user?.first_name || '')}">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Last Name</label>
                            <input type="text" class="form-input" name="last_name" value="${UI.escapeHtml(user?.last_name || '')}">
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Phone</label>
                        <input type="tel" class="form-input" name="phone" value="${UI.escapeHtml(user?.phone || '')}">
                    </div>
                    <button type="submit" class="btn btn-primary">Update Profile</button>
                </form>
            </div>
        `);
    },

    async handleUpdateProfile(event) {
        event.preventDefault();
        const data = new FormData(event.target);
        UI.showLoading(true);

        try {
            await API.updateProfile({
                first_name: data.get('first_name'),
                last_name: data.get('last_name'),
                phone: data.get('phone'),
            });
            UI.showToast('Profile updated!', 'success');
        } catch (error) {
            UI.showToast(error.message, 'error');
        } finally {
            UI.showLoading(false);
        }
        return false;
    },

    showEditProfile() {
        const user = Store.get('user');
        UI.showModal(`
            <div class="modal">
                <div class="modal-header">
                    <h3 class="modal-title">Edit Profile</h3>
                    <button class="modal-close" onclick="UI.closeModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="editProfileForm">
                        <div class="form-group">
                            <label class="form-label">Headline</label>
                            <input type="text" class="form-input" name="headline" placeholder="e.g. Senior Full Stack Developer">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Bio</label>
                            <textarea class="form-input" name="bio" rows="4" placeholder="Tell us about yourself..."></textarea>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Preferred Location</label>
                            <input type="text" class="form-input" name="preferred_locations" placeholder="e.g. San Francisco, CA">
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">LinkedIn URL</label>
                                <input type="url" class="form-input" name="linkedin_url" placeholder="https://linkedin.com/in/...">
                            </div>
                            <div class="form-group">
                                <label class="form-label">GitHub URL</label>
                                <input type="url" class="form-input" name="github_url" placeholder="https://github.com/...">
                            </div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
                    <button class="btn btn-primary" onclick="Profile.saveProfile()">Save Changes</button>
                </div>
            </div>
        `);

        // Pre-fill form
        API.getCandidateProfile().then(r => {
            const p = r.data;
            if (!p) return;
            document.querySelector('[name="headline"]').value = p.headline || '';
            document.querySelector('[name="bio"]').value = p.bio || '';
            document.querySelector('[name="preferred_locations"]').value = p.preferred_locations || '';
            document.querySelector('[name="linkedin_url"]').value = p.linkedin_url || '';
            document.querySelector('[name="github_url"]').value = p.github_url || '';
        }).catch(() => {});
    },

    async saveProfile() {
        const form = document.getElementById('editProfileForm');
        if (!form) return;
        
        const data = new FormData(form);
        UI.showLoading(true);

        try {
            await API.updateCandidateProfile({
                headline: data.get('headline'),
                bio: data.get('bio'),
                preferred_locations: data.get('preferred_locations'),
                linkedin_url: data.get('linkedin_url'),
                github_url: data.get('github_url'),
            });
            UI.showToast('Profile updated!', 'success');
            UI.closeModal();
            this.renderCandidateProfile();
        } catch (error) {
            UI.showToast(error.message, 'error');
        } finally {
            UI.showLoading(false);
        }
    },

    showEditSkills() {
        UI.showModal(`
            <div class="modal">
                <div class="modal-header">
                    <h3 class="modal-title">Edit Skills</h3>
                    <button class="modal-close" onclick="UI.closeModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label class="form-label">Add Skills</label>
                        <div style="display: flex; gap: 0.5rem;">
                            <input type="text" class="form-input" id="skillInput" 
                                   placeholder="Type a skill and press Enter"
                                   onkeypress="if(event.key==='Enter'){event.preventDefault();Profile.addSkill(this.value)}">
                        </div>
                    </div>
                    <div id="skillsContainer" style="display: flex; flex-wrap: wrap; gap: 0.5rem;"></div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
                    <button class="btn btn-primary" onclick="Profile.saveSkills()">Save Skills</button>
                </div>
            </div>
        `);

        // Load existing skills
        API.getCandidateSkills().then(r => {
            const container = document.getElementById('skillsContainer');
            if (!container) return;
            
            window._editingSkills = (r.data || []).map(s => s.skill?.name || '');
            container.innerHTML = window._editingSkills.map(s => `
                <span class="skill-tag">${UI.escapeHtml(s)}
                    <span class="remove-skill" onclick="Profile.removeSkill('${s}')">&times;</span>
                </span>
            `).join('');
        }).catch(() => {
            window._editingSkills = [];
        });
    },

    addSkill(name) {
        if (!name.trim()) return;
        if (!window._editingSkills) window._editingSkills = [];
        if (window._editingSkills.includes(name.trim())) return;
        
        window._editingSkills.push(name.trim());
        const container = document.getElementById('skillsContainer');
        if (container) {
            container.innerHTML = window._editingSkills.map(s => `
                <span class="skill-tag">${UI.escapeHtml(s)}
                    <span class="remove-skill" onclick="Profile.removeSkill('${s}')">&times;</span>
                </span>
            `).join('');
        }
        document.getElementById('skillInput').value = '';
    },

    removeSkill(name) {
        window._editingSkills = (window._editingSkills || []).filter(s => s !== name);
        const container = document.getElementById('skillsContainer');
        if (container) {
            container.innerHTML = window._editingSkills.map(s => `
                <span class="skill-tag">${UI.escapeHtml(s)}
                    <span class="remove-skill" onclick="Profile.removeSkill('${s}')">&times;</span>
                </span>
            `).join('');
        }
    },

    async saveSkills() {
        const skills = (window._editingSkills || []).map(name => ({
            name: name,
            proficiency: 3,
            is_top_skill: false,
        }));

        UI.showLoading(true);
        try {
            await API.updateCandidateSkills({ skills });
            UI.showToast('Skills updated!', 'success');
            UI.closeModal();
            this.renderCandidateProfile();
        } catch (error) {
            UI.showToast(error.message, 'error');
        } finally {
            UI.showLoading(false);
        }
    },

    showUploadResume() {
        UI.showModal(`
            <div class="modal">
                <div class="modal-header">
                    <h3 class="modal-title">Upload Resume</h3>
                    <button class="modal-close" onclick="UI.closeModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="file-upload" id="resumeUpload">
                        <div class="file-upload-icon"><i class="fas fa-cloud-upload-alt"></i></div>
                        <div class="file-upload-text">Drop your resume here or click to browse</div>
                        <div class="file-upload-hint">PDF or DOCX, max 16MB</div>
                        <input type="file" accept=".pdf,.docx,.doc" 
                               onchange="Profile.handleResumeUpload(event.target.files[0])">
                    </div>
                    <div id="uploadProgress" style="display: none; margin-top: 1rem;">
                        <div class="progress-bar"><div class="progress-bar-fill" style="width: 0%;" id="progressFill"></div></div>
                        <div style="text-align: center; margin-top: 0.5rem; color: var(--text-secondary);">Uploading...</div>
                    </div>
                </div>
            </div>
        `);
    },

    async handleResumeUpload(file) {
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', file.name.replace(/\.[^/.]+$/, ''));

        document.getElementById('uploadProgress').style.display = 'block';
        document.querySelector('.file-upload-icon i').className = 'fas fa-spinner fa-spin';

        try {
            await API.uploadResume(formData);
            UI.showToast('Resume uploaded successfully!', 'success');
            UI.closeModal();
            this.renderCandidateProfile();
        } catch (error) {
            UI.showToast(error.message, 'error');
            document.querySelector('.file-upload-icon i').className = 'fas fa-cloud-upload-alt';
        }
    },

    async setDefaultResume(resumeId) {
        try {
            await API.setDefaultResume(resumeId);
            UI.showToast('Default resume updated', 'success');
            this.renderCandidateProfile();
        } catch (error) {
            UI.showToast(error.message, 'error');
        }
    },

    async deleteResume(resumeId) {
        if (!confirm('Delete this resume?')) return;
        try {
            await API.deleteResume(resumeId);
            UI.showToast('Resume deleted', 'success');
            this.renderCandidateProfile();
        } catch (error) {
            UI.showToast(error.message, 'error');
        }
    },

    async renderSettings() {
        Pages.render(`
            <div class="page-header animate-fade-in">
                <h1 class="page-title">Settings</h1>
                <p class="page-subtitle">Manage your account settings</p>
            </div>
            <div class="glass-card animate-fade-in-up" style="max-width: 600px;">
                <h3 style="margin-bottom: 1.5rem;">Change Password</h3>
                <form onsubmit="return Profile.handleChangePassword(event)">
                    <div class="form-group">
                        <label class="form-label">Current Password</label>
                        <input type="password" class="form-input" name="current_password" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">New Password</label>
                        <input type="password" class="form-input" name="new_password" required
                               placeholder="At least 8 characters with uppercase, lowercase, number & special char">
                    </div>
                    <button type="submit" class="btn btn-primary">Change Password</button>
                </form>
            </div>
        `);
    },

    async handleChangePassword(event) {
        event.preventDefault();
        const data = new FormData(event.target);
        UI.showLoading(true);

        try {
            await API.changePassword({
                current_password: data.get('current_password'),
                new_password: data.get('new_password'),
            });
            UI.showToast('Password changed successfully!', 'success');
            event.target.reset();
        } catch (error) {
            UI.showToast(error.message, 'error');
        } finally {
            UI.showLoading(false);
        }
        return false;
    }
};
