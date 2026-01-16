// State management
let currentChatId = null;
let chats = {};
let pendingAction = null;
let pendingState = null;
let originalQuery = null;

// API endpoint
const API_URL = 'http://127.0.0.1:8000';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadChatsFromStorage();
    if (Object.keys(chats).length === 0) {
        createNewChat();
    } else {
        const lastChatId = Object.keys(chats)[0];
        switchToChat(lastChatId);
    }
    renderChatList();
    
    // Event listeners
    document.getElementById('newChatBtn').addEventListener('click', createNewChat);
    document.getElementById('sendBtn').addEventListener('click', sendMessage);
    document.getElementById('userInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});

// Chat management
function createNewChat() {
    const chatId = 'chat_' + Date.now();
    chats[chatId] = {
        id: chatId,
        title: 'New Chat',
        messages: [],
        created: new Date().toISOString()
    };
    saveChatsToStorage();
    switchToChat(chatId);
    renderChatList();
}

function switchToChat(chatId) {
    // Don't do anything if already on this chat
    if (currentChatId === chatId) {
        return;
    }
    
    // Cancel any pending action when switching chats
    if (pendingAction) {
        addSystemMessage('Pending action cancelled.');
        pendingAction = null;
        pendingState = null;
        originalQuery = null;
    }
    
    currentChatId = chatId;
    renderMessages();
    renderChatList();
}

function renderChatList() {
    const chatList = document.getElementById('chatList');
    chatList.innerHTML = '';
    
    Object.values(chats).sort((a, b) => new Date(b.created) - new Date(a.created)).forEach(chat => {
        const item = document.createElement('div');
        item.className = 'chat-item' + (chat.id === currentChatId ? ' active' : '');
        
        const title = document.createElement('span');
        title.textContent = chat.title;
        title.addEventListener('click', () => switchToChat(chat.id));
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-chat-btn';
        deleteBtn.textContent = '×';
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteChat(chat.id);
        });
        
        item.appendChild(title);
        item.appendChild(deleteBtn);
        chatList.appendChild(item);
    });
}

function deleteChat(chatId) {
    if (Object.keys(chats).length === 1) {
        alert('Cannot delete the last chat');
        return;
    }
    
    delete chats[chatId];
    saveChatsToStorage();
    
    if (currentChatId === chatId) {
        const remainingChats = Object.keys(chats);
        switchToChat(remainingChats[0]);
    }
    
    renderChatList();
}

// Message rendering
function renderMessages() {
    const container = document.getElementById('chatMessages');
    container.innerHTML = '';
    
    const chat = chats[currentChatId];
    if (!chat) return;
    
    chat.messages.forEach(msg => {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${msg.role}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Format content with markdown-like bold and line breaks
        let formattedContent = msg.content;
        // Convert **text** to <strong>text</strong>
        formattedContent = formattedContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Convert bullet points
        formattedContent = formattedContent.replace(/^• /gm, '&bull; ');
        formattedContent = formattedContent.replace(/^- /gm, '&bull; ');
        // Convert line breaks
        formattedContent = formattedContent.replace(/\n/g, '<br>');
        
        contentDiv.innerHTML = formattedContent;
        
        if (msg.timestamp) {
            const timeDiv = document.createElement('div');
            timeDiv.className = 'timestamp';
            timeDiv.textContent = new Date(msg.timestamp).toLocaleTimeString();
            contentDiv.appendChild(timeDiv);
        }
        
        msgDiv.appendChild(contentDiv);
        container.appendChild(msgDiv);
    });
    
    container.scrollTop = container.scrollHeight;
}

function addMessage(role, content) {
    const chat = chats[currentChatId];
    if (!chat) return;
    
    const message = {
        role,
        content,
        timestamp: new Date().toISOString()
    };
    
    chat.messages.push(message);
    
    // Update chat title from first user message
    if (role === 'user' && chat.messages.filter(m => m.role === 'user').length === 1) {
        chat.title = content.substring(0, 30) + (content.length > 30 ? '...' : '');
        renderChatList();
    }
    
    saveChatsToStorage();
    renderMessages();
}

function addSystemMessage(content) {
    addMessage('system', content);
}

// Send message
async function sendMessage() {
    const input = document.getElementById('userInput');
    const query = input.value.trim();
    
    if (!query) return;
    
    input.value = '';
    addMessage('user', query);
    
    // Disable input while processing
    setInputEnabled(false);
    
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query,
                chat_id: currentChatId,
                conversation_history: chats[currentChatId].messages,
                pending_action: pendingAction,
                pending_state: pendingState,
                original_query: originalQuery
            })
        });
        
        const data = await response.json();
        handleResponse(data);
    } catch (error) {
        addMessage('assistant', 'Error: ' + error.message);
    } finally {
        setInputEnabled(true);
    }
}

// Handle API response
function handleResponse(data) {
    switch (data.type) {
        case 'INFO_QUERY':
            addMessage('assistant', data.content.answer);
            pendingAction = null;
            pendingState = null;
            originalQuery = null;
            break;
            
        case 'CONFIRMATION_NEEDED':
            addMessage('assistant', data.content.message);
            pendingAction = data.pending_action;
            pendingState = data.pending_state;
            originalQuery = data.original_query;
            break;
            
        case 'TICKET_GENERATED':
            // Show ticket as formatted message with bold labels
            const ticket = data.content;
            let ticketMsg = '**Generated Ticket:**\n\n';
            for (const [key, value] of Object.entries(ticket)) {
                const label = key.replace(/_/g, ' ').toUpperCase();
                ticketMsg += `**${label}:** ${value}\n\n`;
            }
            ticketMsg += 'Do you want to modify the ticket?';
            addMessage('assistant', ticketMsg);
            pendingAction = data.pending_action;
            pendingState = data.pending_state;
            originalQuery = data.original_query;
            break;
            
        case 'TICKET_UPDATED':
            // Show updated ticket with bold labels
            const updatedTicket = data.content;
            let updatedMsg = '**Updated Ticket:**\n\n';
            for (const [key, value] of Object.entries(updatedTicket)) {
                const label = key.replace(/_/g, ' ').toUpperCase();
                updatedMsg += `**${label}:** ${value}\n\n`;
            }
            updatedMsg += 'Do you want to modify the ticket?';
            addMessage('assistant', updatedMsg);
            pendingAction = data.pending_action;
            pendingState = data.pending_state;
            originalQuery = data.original_query;
            break;
            
        case 'TICKET_EXPORTED':
            addMessage('assistant', data.content.message);
            pendingAction = null;
            pendingState = null;
            originalQuery = null;
            break;
            
        case 'CUSTOM_DESC_PROMPT':
            addMessage('assistant', data.content.message);
            pendingAction = data.pending_action;
            pendingState = data.pending_state;
            originalQuery = data.original_query;
            break;
            
        case 'CLARIFICATION_NEEDED':
            addMessage('assistant', data.content.message);
            pendingAction = data.pending_action;
            pendingState = data.pending_state;
            originalQuery = data.original_query;
            break;
    }
}

// UI helpers
function setInputEnabled(enabled) {
    const input = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    
    input.disabled = !enabled;
    sendBtn.disabled = !enabled;
    
    if (enabled) {
        input.focus();
    }
}

// Storage
function saveChatsToStorage() {
    localStorage.setItem('chats', JSON.stringify(chats));
}

function loadChatsFromStorage() {
    const stored = localStorage.getItem('chats');
    if (stored) {
        chats = JSON.parse(stored);
    }
}
