/* Update Keseluruhan Sistem PPDB SMKN 1 Sorong (27 Juli 2026) */
window.switchPage = function(pageId) {
    document.querySelectorAll('.page-content').forEach(page => page.classList.remove('active'));
    document.getElementById(pageId).classList.add('active');
    
    // Sembunyikan navbar jika masuk ke halaman chatbot
    const navbar = document.getElementById('navbar');
    if (navbar) {
        if (pageId === 'page-home') {
            navbar.style.display = 'block';
        } else {
            navbar.style.display = 'none';
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    // --- ELEMENTS ---
    const chatArea = document.getElementById('chat-area');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const sendIcon = document.getElementById('send-icon');
    const stopIcon = document.getElementById('stop-icon');
    const clearBtn = document.getElementById('clear-btn');
    const autoAskBoxes = document.querySelectorAll('.auto-ask');
    const historyList = document.getElementById('history-list');
    const voiceBtn = document.getElementById('voice-btn');
    
    // --- STATE ---
    let currentSessionId = null;
    let sessions = JSON.parse(localStorage.getItem('chat_sessions')) || [];
    let abortController = null;

    // --- VOICE RECOGNITION SETUP ---
    let recognition;
    let isRecording = false;
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = 'id-ID';
        recognition.interimResults = true;
        recognition.continuous = true;
        recognition.maxAlternatives = 1;

        recognition.onstart = function() {
            isRecording = true;
            if (voiceBtn) {
                voiceBtn.classList.add('text-red-600', 'bg-red-100', 'animate-pulse');
                voiceBtn.classList.remove('text-slate-600', 'bg-slate-100', 'hover:bg-slate-200', 'hover:text-sekolah-blue');
            }
            userInput.placeholder = "Mendengarkan...";
            userInput.value = ""; // Bersihkan kolom input saat mulai mendengarkan
        };

        recognition.onresult = function(event) {
            let transcript = '';
            for (let i = 0; i < event.results.length; ++i) {
                transcript += event.results[i][0].transcript;
            }
            userInput.value = transcript;
        };

        recognition.onerror = function(event) {
            console.error("Speech recognition error", event.error);
            stopRecordingUI();
        };

        recognition.onend = function() {
            stopRecordingUI();
            if (userInput.value.trim() !== '') {
                handleSendMessage();
            }
        };
    } else {
        if(voiceBtn) voiceBtn.style.display = 'none';
    }

    function stopRecordingUI() {
        isRecording = false;
        if(voiceBtn) {
            voiceBtn.classList.remove('text-red-600', 'bg-red-100', 'animate-pulse');
            voiceBtn.classList.add('text-slate-600', 'bg-slate-100', 'hover:bg-slate-200', 'hover:text-sekolah-blue');
        }
        userInput.placeholder = "Tanyakan seputar PPDB SMKN 1...";
    }

    if (voiceBtn) {
        voiceBtn.addEventListener('click', () => {
            if (isRecording) {
                recognition.stop();
            } else {
                if (recognition) recognition.start();
            }
        });
    }

    // --- HISTORY MANAGEMENT ---
    
    
    // --- SIDEBAR TOGGLE ---
    const openSidebarBtn = document.getElementById('open-sidebar-btn');
    const closeSidebarBtn = document.getElementById('close-sidebar-btn');
    const sidebar = document.getElementById('sidebar');
    
    function toggleSidebar() {
        if (!sidebar) return;
        const isMobile = window.innerWidth < 768;
        
        if (isMobile) {
            // Mobile: toggle translate
            if (sidebar.classList.contains('translate-x-0')) {
                sidebar.classList.remove('translate-x-0');
                sidebar.classList.add('-translate-x-full');
                if (openSidebarBtn) openSidebarBtn.classList.remove('hidden');
            } else {
                sidebar.classList.remove('-translate-x-full');
                sidebar.classList.add('translate-x-0');
                if (openSidebarBtn) openSidebarBtn.classList.add('hidden');
            }
        } else {
            // Desktop: toggle negative margin
            if (sidebar.classList.contains('md:-ml-[20rem]')) {
                sidebar.classList.remove('md:-ml-[20rem]');
                if (openSidebarBtn) openSidebarBtn.classList.add('md:hidden');
            } else {
                sidebar.classList.add('md:-ml-[20rem]');
                if (openSidebarBtn) openSidebarBtn.classList.remove('md:hidden');
            }
        }
    }

    if (openSidebarBtn) openSidebarBtn.addEventListener('click', toggleSidebar);
    if (closeSidebarBtn) closeSidebarBtn.addEventListener('click', toggleSidebar);

    // Menutup sidebar jika pengguna menekan area luar sidebar (Mobile)
    document.addEventListener('click', (e) => {
        const isMobile = window.innerWidth < 768;
        if (isMobile && sidebar && !sidebar.classList.contains('-translate-x-full')) {
            const clickedInsideSidebar = sidebar.contains(e.target);
            const clickedOpenBtn = openSidebarBtn && openSidebarBtn.contains(e.target);
            
            if (!clickedInsideSidebar && !clickedOpenBtn) {
                toggleSidebar();
            }
        }
    });
    function renderHistory() {
        if (!historyList) return;
        historyList.innerHTML = '';
        
        const sortedSessions = [...sessions].reverse();
        
        if (sortedSessions.length === 0) {
            historyList.innerHTML = '<div class="text-xs text-slate-400 text-center py-4">Belum ada riwayat percakapan</div>';
            return;
        }
        
        let todayHtml = '<div><h4 class="text-[10px] font-bold text-slate-400 mb-3 px-1 uppercase tracking-widest">Riwayat</h4><div class="space-y-1.5">';
        
        sortedSessions.forEach(session => {
            const isActive = session.id === currentSessionId;
            const bgClass = isActive ? 'bg-blue-50 text-blue-700 border-blue-100 shadow-sm' : 'text-slate-600 hover:bg-slate-200/50 border-transparent';
            const iconClass = isActive ? 'text-blue-500' : 'text-slate-400 group-hover:text-slate-600';
            
            todayHtml += `
                <button onclick="loadSession('${session.id}')" class="w-full text-left px-4 py-2.5 text-sm font-medium border ${bgClass} rounded-xl truncate transition-colors flex items-center justify-between group">
                    <div class="flex items-center gap-3 truncate">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-4 w-4 ${iconClass} flex-shrink-0 transition-colors"><path fill-rule="evenodd" d="M4.804 21.644A6.707 6.707 0 006 21.75a6.721 6.721 0 003.583-1.029c.774.182 1.584.279 2.417.279 5.322 0 9.75-3.97 9.75-9 0-5.03-4.428-9-9.75-9s-9.75 3.97-9.75 9c0 2.409 1.025 4.587 2.674 6.192.232.226.277.428.254.543a3.73 3.73 0 01-.814 1.686.75.75 0 00.44 1.223zM8.25 10.875a1.125 1.125 0 100 2.25 1.125 1.125 0 000-2.25zM10.875 12a1.125 1.125 0 112.25 0 1.125 1.125 0 01-2.25 0zm4.875-1.125a1.125 1.125 0 100 2.25 1.125 1.125 0 000-2.25z" clip-rule="evenodd" /></svg>
                        <span class="truncate">${session.title}</span>
                    </div>
                    <div onclick="deleteSession(event, '${session.id}')" class="p-1.5 text-slate-400 bg-slate-100/50 hover:bg-red-100 hover:text-red-600 rounded-md transition-all shadow-sm group-hover:bg-red-50 group-hover:text-red-500" title="Hapus Riwayat">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-4 w-4"><path fill-rule="evenodd" d="M16.5 4.478v.227a48.816 48.816 0 013.878.512.75.75 0 11-.256 1.478l-.209-.035-1.005 13.07a3 3 0 01-2.991 2.77H8.084a3 3 0 01-2.991-2.77L4.087 6.66l-.209.035a.75.75 0 01-.256-1.478A48.567 48.567 0 017.5 4.705v-.227c0-1.564 1.213-2.9 2.816-2.951a52.662 52.662 0 013.369 0c1.603.051 2.815 1.387 2.815 2.951zm-6.136-1.452a51.196 51.196 0 013.273 0C14.39 3.05 15 3.684 15 4.478v.113a49.488 49.488 0 00-6 0v-.113c0-.794.609-1.428 1.364-1.452zm-.355 5.945a.75.75 0 10-1.5.058l.347 9a.75.75 0 101.499-.058l-.346-9zm5.48.058a.75.75 0 10-1.498-.058l-.347 9a.75.75 0 001.5.058l.345-9z" clip-rule="evenodd" /></svg>
                    </div>
                </button>
            `;
        });
        
        todayHtml += '</div></div>';
        historyList.innerHTML = todayHtml;
    }

    window.loadSession = function(id) {
        const session = sessions.find(s => s.id === id);
        if (!session) return;
        
        currentSessionId = id;
        renderHistory();
        
        chatArea.innerHTML = '';
        const chatWelcome = document.getElementById('chat-welcome');
        const suggestedPrompts = document.getElementById('suggested-prompts');
        const chatContainer = document.getElementById('chat-container');
        
        if (chatWelcome) chatWelcome.classList.add('hidden');
        if (suggestedPrompts) suggestedPrompts.classList.add('hidden');
        if (chatContainer) {
            chatContainer.classList.remove('hidden');
            chatContainer.classList.add('flex');
        }
        
        session.messages.forEach(msg => {
            appendMessage(msg.role, msg.text, false);
        });
    };

    window.deleteSession = function(e, id) {
        e.stopPropagation();
        sessions = sessions.filter(s => s.id !== id);
        localStorage.setItem('chat_sessions', JSON.stringify(sessions));
        if (currentSessionId === id) {
            startNewChat();
        } else {
            renderHistory();
        }
    };

    function saveMessageToSession(role, text) {
        if (!currentSessionId) {
            currentSessionId = 'session_' + Date.now();
            let title = text.substring(0, 30);
            if (text.length > 30) title += '...';
            
            sessions.push({
                id: currentSessionId,
                title: title,
                messages: []
            });
        }
        
        const session = sessions.find(s => s.id === currentSessionId);
        if (session) {
            session.messages.push({ role, text });
            localStorage.setItem('chat_sessions', JSON.stringify(sessions));
            renderHistory();
        }
    }

    function startNewChat() {
        currentSessionId = null;
        chatArea.innerHTML = '';
        renderHistory();
        
        const chatWelcome = document.getElementById('chat-welcome');
        const suggestedPrompts = document.getElementById('suggested-prompts');
        const chatContainer = document.getElementById('chat-container');
        
        if (chatWelcome) chatWelcome.classList.remove('hidden');
        if (suggestedPrompts) suggestedPrompts.classList.remove('hidden');
        if (chatContainer) {
            chatContainer.classList.add('hidden');
            chatContainer.classList.remove('flex');
        }
    }

    // Initial Render
    renderHistory();

    // --- AUTO-ASK ---
    autoAskBoxes.forEach(box => {
        box.addEventListener('click', () => {
            const question = box.getAttribute('data-question');
            setTimeout(() => {
                userInput.value = question;
                handleSendMessage(); 
            }, 300);
        });
    });

    // --- CHAT LOGIC ---
    function appendMessage(role, text, save = true) {
        const msgWrapper = document.createElement('div');
        msgWrapper.className = 'flex items-start gap-4 ' + (role === 'user' ? 'flex-row-reverse' : '');

        const iconDiv = document.createElement('div');
        iconDiv.className = `w-11 h-11 rounded-full flex-shrink-0 flex items-center justify-center text-white mt-1 shadow-md ${role === 'user' ? 'bg-sekolah-orange' : 'bg-sekolah-blue'}`;
        iconDiv.innerHTML = role === 'user' 
            ? `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-6 w-6"><path fill-rule="evenodd" d="M7.5 6a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM3.751 20.105a8.25 8.25 0 0116.498 0 .75.75 0 01-.437.695A18.683 18.683 0 0112 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 01-.437-.695z" clip-rule="evenodd" /></svg>` 
            : `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-6 w-6"><path fill-rule="evenodd" d="M9 4.5a.75.75 0 01.721.544l.813 2.846a3.75 3.75 0 002.576 2.576l2.846.813a.75.75 0 010 1.442l-2.846.813a3.75 3.75 0 00-2.576 2.576l-.813 2.846a.75.75 0 01-1.442 0l-.813-2.846a3.75 3.75 0 00-2.576-2.576l-2.846-.813a.75.75 0 010-1.442l2.846-.813A3.75 3.75 0 007.466 7.89l.813-2.846A.75.75 0 019 4.5zM18 1.5a.75.75 0 01.728.568l.258 1.036c.236.94.97 1.674 1.91 1.91l1.036.258a.75.75 0 010 1.456l-1.036.258c-.94.236-1.674.97-1.91 1.91l-.258 1.036a.75.75 0 01-1.456 0l-.258-1.036a2.625 2.625 0 00-1.91-1.91l-1.036-.258a.75.75 0 010-1.456l1.036-.258a2.625 2.625 0 001.91-1.91l.258-1.036A.75.75 0 0118 1.5zM16.5 15a.75.75 0 01.712.513l.394 1.183c.15.447.5.799.948.948l1.183.395a.75.75 0 010 1.422l-1.183.395c-.447.15-.799.5-.948.948l-.395 1.183a.75.75 0 01-1.422 0l-.395-1.183a1.5 1.5 0 00-.948-.948l-1.183-.395a.75.75 0 010-1.422l1.183-.395c.447-.15.799-.5.948-.948l.395-1.183A.75.75 0 0116.5 15z" clip-rule="evenodd" /></svg>`;

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = role === 'user' 
            ? 'bg-sekolah-blue text-white px-4 py-3 rounded-2xl rounded-tr-sm text-[14px] leading-relaxed shadow-sm max-w-[85%] sm:max-w-[75%] w-fit' 
            : 'bg-gray-100 text-sekolah-dark px-4 py-3 rounded-2xl rounded-tl-sm text-[14px] leading-relaxed shadow-sm max-w-[85%] sm:max-w-[75%] relative w-fit';

        const textContent = document.createElement('div');
        textContent.className = role === 'user' 
            ? 'prose prose-sm prose-invert max-w-none prose-p:my-1' 
            : 'prose prose-sm prose-slate max-w-none prose-p:my-1 prose-ul:my-1 prose-li:my-0.5 prose-headings:text-sekolah-dark prose-headings:mb-2 prose-headings:mt-3 prose-a:text-sekolah-blue prose-a:underline prose-a:font-semibold prose-a:underline-offset-2 hover:prose-a:text-opacity-80 prose-strong:text-sekolah-dark prose-strong:font-semibold marker:text-sekolah-dark marker:font-bold';
        
        textContent.innerHTML = marked.parse(text);
        bubbleDiv.appendChild(textContent);
        
        if (role === 'bot') {
            const copyWrapper = document.createElement('div');
            copyWrapper.className = 'flex justify-end mt-0.5';
            
            const copyBtn = document.createElement('button');
            copyBtn.className = 'p-1 rounded-md text-slate-400 hover:text-sekolah-blue hover:bg-slate-200/50 transition-all flex items-center gap-1 text-[11px] font-medium';
            copyBtn.title = 'Salin pesan';
            copyBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg> Salin`;
            copyBtn.onclick = () => {
                navigator.clipboard.writeText(textContent.innerText);
                copyBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-500" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg> Tersalin`;
                setTimeout(() => { copyBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg> Salin`; }, 2000);
            };
            copyWrapper.appendChild(copyBtn);
            bubbleDiv.appendChild(copyWrapper);
        }

        msgWrapper.appendChild(iconDiv);
        msgWrapper.appendChild(bubbleDiv);
        
        chatArea.appendChild(msgWrapper);
        chatArea.scrollTo({ top: chatArea.scrollHeight, behavior: 'smooth' });

        if (save) {
            saveMessageToSession(role, text);
        }
    }

    function showTypingIndicator() {
        const msgWrapper = document.createElement('div');
        msgWrapper.id = 'typing-indicator-wrapper';
        msgWrapper.className = 'flex items-start gap-4';

        const iconDiv = document.createElement('div');
        iconDiv.className = `w-11 h-11 rounded-full flex-shrink-0 flex items-center justify-center text-white mt-1 shadow-md bg-sekolah-blue`;
        iconDiv.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-6 w-6"><path fill-rule="evenodd" d="M9 4.5a.75.75 0 01.721.544l.813 2.846a3.75 3.75 0 002.576 2.576l2.846.813a.75.75 0 010 1.442l-2.846.813a3.75 3.75 0 00-2.576 2.576l-.813 2.846a.75.75 0 01-1.442 0l-.813-2.846a3.75 3.75 0 00-2.576-2.576l-2.846-.813a.75.75 0 010-1.442l2.846-.813A3.75 3.75 0 007.466 7.89l.813-2.846A.75.75 0 019 4.5zM18 1.5a.75.75 0 01.728.568l.258 1.036c.236.94.97 1.674 1.91 1.91l1.036.258a.75.75 0 010 1.456l-1.036.258c-.94.236-1.674.97-1.91 1.91l-.258 1.036a.75.75 0 01-1.456 0l-.258-1.036a2.625 2.625 0 00-1.91-1.91l-1.036-.258a.75.75 0 010-1.456l1.036-.258a2.625 2.625 0 001.91-1.91l.258-1.036A.75.75 0 0118 1.5zM16.5 15a.75.75 0 01.712.513l.394 1.183c.15.447.5.799.948.948l1.183.395a.75.75 0 010 1.422l-1.183.395c-.447.15-.799.5-.948.948l-.395 1.183a.75.75 0 01-1.422 0l-.395-1.183a1.5 1.5 0 00-.948-.948l-1.183-.395a.75.75 0 010-1.422l1.183-.395c.447-.15.799-.5.948-.948l.395-1.183A.75.75 0 0116.5 15z" clip-rule="evenodd" /></svg>`;

        const textDiv = document.createElement('div');
        textDiv.className = 'bg-gray-100 text-slate-800 px-5 py-4 rounded-3xl rounded-tl-sm shadow-sm max-w-[80%]';
        textDiv.innerHTML = `
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        msgWrapper.appendChild(iconDiv);
        msgWrapper.appendChild(textDiv);
        
        chatArea.appendChild(msgWrapper);
        chatArea.scrollTo({ top: chatArea.scrollHeight, behavior: 'smooth' });
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator-wrapper');
        if (indicator) indicator.remove();
    }

    function resetSendButton() {
        if (sendIcon && stopIcon && sendBtn) {
            stopIcon.classList.add('hidden');
            sendIcon.classList.remove('hidden');
            sendBtn.classList.replace('bg-red-500', 'bg-sekolah-blue');
        }
    }

    async function handleSendMessage() {
        if (abortController) {
            abortController.abort();
            abortController = null;
            resetSendButton();
            return;
        }

        const message = userInput.value.trim();
        if (!message) return;
        
        // UI Transition on first message
        const chatWelcome = document.getElementById('chat-welcome');
        const suggestedPrompts = document.getElementById('suggested-prompts');
        const chatContainer = document.getElementById('chat-container');
        
        if (chatWelcome && !chatWelcome.classList.contains('hidden')) {
            chatWelcome.classList.add('hidden');
            if (suggestedPrompts) suggestedPrompts.classList.add('hidden');
            if (chatContainer) chatContainer.classList.remove('hidden');
            chatContainer.classList.add('flex');
        }

        appendMessage('user', message);
        userInput.value = '';
        
        if (sendIcon && stopIcon && sendBtn) {
            sendIcon.classList.add('hidden');
            stopIcon.classList.remove('hidden');
            sendBtn.classList.replace('bg-sekolah-blue', 'bg-red-500');
        }
        userInput.disabled = true;
        
        showTypingIndicator();
        
        abortController = new AbortController();

        try {
            // Ambil riwayat percakapan sebelumnya untuk memori chatbot (Maks 4 chat terakhir)
            const currentSession = sessions.find(s => s.id === currentSessionId);
            let history = [];
            if (currentSession && currentSession.messages) {
                // Ambil pesan sebelumnya, tidak termasuk pesan user yang baru saja disubmit
                history = currentSession.messages.slice(0, -1).slice(-4);
            }
            
            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ message, history }),
                signal: abortController.signal
            });
            
            removeTypingIndicator();
            
            // Siapkan balasan stream AI
            const reader = res.body.getReader();
            const decoder = new TextDecoder("utf-8");
            
            // Buat DOM Element untuk balon percakapan bot
            const msgWrapper = document.createElement('div');
            msgWrapper.className = 'flex items-start gap-4';

            const iconDiv = document.createElement('div');
            iconDiv.className = `w-11 h-11 rounded-full flex-shrink-0 flex items-center justify-center text-white mt-1 shadow-md bg-sekolah-blue`;
            iconDiv.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-6 w-6"><path fill-rule="evenodd" d="M9 4.5a.75.75 0 01.721.544l.813 2.846a3.75 3.75 0 002.576 2.576l2.846.813a.75.75 0 010 1.442l-2.846.813a3.75 3.75 0 00-2.576 2.576l-.813 2.846a.75.75 0 01-1.442 0l-.813-2.846a3.75 3.75 0 00-2.576-2.576l-2.846-.813a.75.75 0 010-1.442l2.846-.813A3.75 3.75 0 007.466 7.89l.813-2.846A.75.75 0 019 4.5zM18 1.5a.75.75 0 01.728.568l.258 1.036c.236.94.97 1.674 1.91 1.91l1.036.258a.75.75 0 010 1.456l-1.036.258c-.94.236-1.674.97-1.91 1.91l-.258 1.036a.75.75 0 01-1.456 0l-.258-1.036a2.625 2.625 0 00-1.91-1.91l-1.036-.258a.75.75 0 010-1.456l1.036-.258a2.625 2.625 0 001.91-1.91l.258-1.036A.75.75 0 0118 1.5zM16.5 15a.75.75 0 01.712.513l.394 1.183c.15.447.5.799.948.948l1.183.395a.75.75 0 010 1.422l-1.183.395c-.447.15-.799.5-.948.948l-.395 1.183a.75.75 0 01-1.422 0l-.395-1.183a1.5 1.5 0 00-.948-.948l-1.183-.395a.75.75 0 010-1.422l1.183-.395c.447-.15.799-.5.948-.948l.395-1.183A.75.75 0 0116.5 15z" clip-rule="evenodd" /></svg>`;

            const bubbleDiv = document.createElement('div');
            bubbleDiv.className = 'bg-gray-100 text-sekolah-dark px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm max-w-[85%] sm:max-w-[75%] relative w-fit';

            const textContent = document.createElement('div');
            textContent.className = 'prose prose-sm prose-slate max-w-none prose-p:my-1 prose-ul:my-1 prose-li:my-0.5 prose-headings:text-sekolah-dark prose-headings:mb-2 prose-headings:mt-3 prose-a:text-sekolah-blue prose-a:underline prose-a:font-semibold prose-a:underline-offset-2 hover:prose-a:text-opacity-80 prose-strong:text-sekolah-dark prose-strong:font-semibold marker:text-sekolah-dark marker:font-bold';
            
            const copyWrapper = document.createElement('div');
            copyWrapper.className = 'hidden justify-end mt-0.5';
            
            const copyBtn = document.createElement('button');
            copyBtn.className = 'p-1 rounded-md text-slate-400 hover:text-sekolah-blue hover:bg-slate-200/50 transition-all flex items-center gap-1 text-[11px] font-medium';
            copyBtn.title = 'Salin pesan';
            copyBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg> Salin`;
            
            copyWrapper.appendChild(copyBtn);
            bubbleDiv.appendChild(textContent);
            bubbleDiv.appendChild(copyWrapper);
            
            msgWrapper.appendChild(iconDiv);
            msgWrapper.appendChild(bubbleDiv);
            chatArea.appendChild(msgWrapper);
            
            let fullReply = "";
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                // Terjemahkan potongan byte menjadi string teks
                fullReply += decoder.decode(value, { stream: true });
                textContent.innerHTML = marked.parse(fullReply);
                chatArea.scrollTo({ top: chatArea.scrollHeight, behavior: 'smooth' });
            }
            
            // Selesai streaming, barulah simpan ke riwayat penyimpanan lokal (Local Storage)
            saveMessageToSession('bot', fullReply);
            
            // Tampilkan dan fungsikan tombol salin di dalam bubble
            copyWrapper.classList.remove('hidden');
            copyWrapper.classList.add('flex');
            copyBtn.onclick = () => {
                navigator.clipboard.writeText(textContent.innerText);
                copyBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-500" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg> Tersalin`;
                setTimeout(() => { copyBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg> Salin`; }, 2000);
            };
            
        } catch (e) { 
            removeTypingIndicator();
            if (e.name === 'AbortError') {
                console.log('Stream aborted by user');
            } else {
                appendMessage('bot', "Koneksi terputus. Mohon coba lagi."); 
            }
        } finally {
            abortController = null;
            resetSendButton();
            userInput.disabled = false;
            userInput.focus();
        }
    }

    if (sendBtn) {
        sendBtn.addEventListener('click', handleSendMessage);
        userInput.addEventListener('keypress', (e) => { 
            if (e.key === 'Enter') {
                if (abortController) {
                    // Do nothing or prevent default when generating
                    e.preventDefault();
                } else {
                    handleSendMessage();
                }
            } 
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            startNewChat();
        });
    }


});
