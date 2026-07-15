/*===========================================================
  HireFlow AI - AI Chat Assistant
  Interactive career guidance, resume tips, interview prep
===========================================================*/

const AIChat = {
    messages: [],
    context: 'general',
    isProcessing: false,

    renderChat() {
        Pages.render(`
            <div class="page-header animate-fade-in">
                <h1 class="page-title">AI Career Assistant</h1>
                <p class="page-subtitle">Ask me anything about your career, resume, or job search</p>
            </div>

            <div class="chat-container animate-fade-in-up">
                <div class="chat-sidebar">
                    <div class="chat-context-selector">
                        <button class="chat-context-btn active" data-context="general" onclick="AIChat.setContext('general')">
                            <i class="fas fa-comments"></i> General
                        </button>
                        <button class="chat-context-btn" data-context="career" onclick="AIChat.setContext('career')">
                            <i class="fas fa-compass"></i> Career
                        </button>
                        <button class="chat-context-btn" data-context="resume" onclick="AIChat.setContext('resume')">
                            <i class="fas fa-file-alt"></i> Resume
                        </button>
                        <button class="chat-context-btn" data-context="interview" onclick="AIChat.setContext('interview')">
                            <i class="fas fa-users"></i> Interview
                        </button>
                    </div>
                    <div class="chat-quick-actions">
                        <div class="chat-section-label">Quick Actions</div>
                        <button class="chat-quick-btn" onclick="AIChat.sendQuick('Write a professional summary for my resume')">
                            <i class="fas fa-pen-fancy"></i> Write Summary
                        </button>
                        <button class="chat-quick-btn" onclick="AIChat.sendQuick('Generate interview questions for a software engineer role')">
                            <i class="fas fa-question-circle"></i> Practice Q&A
                        </button>
                        <button class="chat-quick-btn" onclick="AIChat.sendQuick('Give me tips to improve my resume for ATS')">
                            <i class="fas fa-chart-line"></i> ATS Tips
                        </button>
                        <button class="chat-quick-btn" onclick="AIChat.sendQuick('How should I negotiate my salary?')">
                            <i class="fas fa-hand-holding-usd"></i> Salary Tips
                        </button>
                        <button class="chat-quick-btn" onclick="AIChat.clearChat()">
                            <i class="fas fa-trash"></i> Clear Chat
                        </button>
                    </div>
                </div>

                <div class="chat-main">
                    <div class="chat-messages" id="chatMessages">
                        <div class="chat-welcome">
                            <div class="chat-avatar assistant">
                                <i class="fas fa-robot"></i>
                            </div>
                            <div class="chat-bubble assistant">
                                <div class="chat-bubble-header">HireFlow AI Assistant</div>
                                <p>Hi! I'm your AI career assistant. I can help you with:</p>
                                <ul style="margin: 0.5rem 0; padding-left: 1.5rem; color: var(--text-secondary);">
                                    <li>Resume writing and ATS optimization</li>
                                    <li>Interview preparation and practice</li>
                                    <li>Career path and skill development advice</li>
                                    <li>Job search strategies and tips</li>
                                    <li>Cover letter and professional summary writing</li>
                                </ul>
                                <p>What would you like help with today?</p>
                                <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.75rem;">
                                    <span class="chat-suggestion" onclick="AIChat.sendQuick('How can I improve my resume?')">Improve my resume</span>
                                    <span class="chat-suggestion" onclick="AIChat.sendQuick('Prepare me for an interview')">Interview prep</span>
                                    <span class="chat-suggestion" onclick="AIChat.sendQuick('What skills should I learn?')">Skill recommendations</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="chat-input-bar">
                        <div class="chat-context-indicator" id="chatContextIndicator">
                            <i class="fas fa-comments"></i> General
                        </div>
                        <input type="text" class="chat-input" id="chatInput" 
                               placeholder="Type your message here..." 
                               onkeydown="if(event.key==='Enter' && !event.shiftKey) { event.preventDefault(); AIChat.sendMessage(); }">
                        <button class="btn btn-primary btn-icon chat-send-btn" onclick="AIChat.sendMessage()" id="chatSendBtn">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        `);

        // Focus input
        setTimeout(() => document.getElementById('chatInput')?.focus(), 300);
    },

    setContext(context) {
        this.context = context;
        document.querySelectorAll('.chat-context-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.context === context);
        });
        const indicator = document.getElementById('chatContextIndicator');
        if (indicator) {
            const labels = { general: 'General', career: 'Career Advice', resume: 'Resume Help', interview: 'Interview Prep' };
            indicator.innerHTML = `<i class="fas fa-${context === 'general' ? 'comments' : context === 'career' ? 'compass' : context === 'resume' ? 'file-alt' : 'users'}"></i> ${labels[context] || 'General'}`;
        }
    },

    async sendMessage() {
        const input = document.getElementById('chatInput');
        if (!input) return;
        
        const message = input.value.trim();
        if (!message || this.isProcessing) return;

        input.value = '';
        this.isProcessing = true;
        
        // Disable send button
        const sendBtn = document.getElementById('chatSendBtn');
        if (sendBtn) sendBtn.disabled = true;

        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Show typing indicator
        this.showTyping();

        try {
            const result = await API.request('/ai/chat', {
                method: 'POST',
                body: JSON.stringify({
                    message: message,
                    context: this.context,
                    history: this.messages.slice(-10)
                })
            });

            // Remove typing indicator
            this.hideTyping();

            // Add AI response
            const reply = result.data?.reply || "I'm not sure how to respond to that. Could you please rephrase?";
            this.addMessage(reply, 'assistant');
            
            // Store in history
            this.messages.push({ role: 'user', content: message });
            this.messages.push({ role: 'assistant', content: reply });

        } catch (error) {
            this.hideTyping();
            this.addMessage(
                "I apologize, but I'm having trouble connecting right now. Please try again in a moment.",
                'assistant'
            );
        } finally {
            this.isProcessing = false;
            if (sendBtn) sendBtn.disabled = false;
            setTimeout(() => document.getElementById('chatInput')?.focus(), 100);
        }
    },

    sendQuick(text) {
        const input = document.getElementById('chatInput');
        if (input) {
            input.value = text;
            this.sendMessage();
        }
    },

    addMessage(content, role) {
        const container = document.getElementById('chatMessages');
        if (!container) return;

        // Remove welcome message if it exists
        const welcome = container.querySelector('.chat-welcome');
        if (welcome) welcome.remove();

        const div = document.createElement('div');
        div.className = `chat-message ${role}`;
        
        const formattedContent = this.formatContent(content);
        
        div.innerHTML = `
            <div class="chat-avatar ${role}">
                <i class="fas ${role === 'user' ? 'fa-user' : 'fa-robot'}"></i>
            </div>
            <div class="chat-bubble ${role}">
                <div class="chat-bubble-header">${role === 'user' ? 'You' : 'HireFlow AI'}</div>
                <div class="chat-bubble-content">${formattedContent}</div>
                <div class="chat-bubble-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
        `;

        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
        
        // Animate in
        requestAnimationFrame(() => div.classList.add('visible'));
    },

    formatContent(text) {
        if (!text) return '';
        
        // Escape HTML first
        const escaped = UI.escapeHtml(text);
        
        // Format bullet points
        let formatted = escaped.replace(/\n\s*\*\s+/g, '\n• ');
        
        // Format bold text (**text**)
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Format numbered lists
        formatted = formatted.replace(/(\d+)\.\s+/g, '<br><strong>$1.</strong> ');
        
        // Convert newlines to <br>
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    },

    showTyping() {
        const container = document.getElementById('chatMessages');
        if (!container) return;

        const typing = document.createElement('div');
        typing.className = 'chat-message assistant typing-indicator';
        typing.id = 'typingIndicator';
        typing.innerHTML = `
            <div class="chat-avatar assistant">
                <i class="fas fa-robot"></i>
            </div>
            <div class="chat-bubble assistant">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        container.appendChild(typing);
        container.scrollTop = container.scrollHeight;
    },

    hideTyping() {
        const typing = document.getElementById('typingIndicator');
        if (typing) typing.remove();
    },

    clearChat() {
        this.messages = [];
        const container = document.getElementById('chatMessages');
        if (container) {
            container.innerHTML = `
                <div class="chat-welcome">
                    <div class="chat-avatar assistant">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="chat-bubble assistant">
                        <div class="chat-bubble-header">HireFlow AI Assistant</div>
                        <p>Chat cleared! How can I help you today?</p>
                        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.75rem;">
                            <span class="chat-suggestion" onclick="AIChat.sendQuick('How can I improve my resume?')">Improve my resume</span>
                            <span class="chat-suggestion" onclick="AIChat.sendQuick('Prepare me for an interview')">Interview prep</span>
                            <span class="chat-suggestion" onclick="AIChat.sendQuick('What skills should I learn?')">Skill recommendations</span>
                        </div>
                    </div>
                </div>
            `;
        }
        UI.showToast('Chat cleared', 'success');
    }
};
