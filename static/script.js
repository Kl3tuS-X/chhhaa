// Файл: my_chatgpt_bot/static/script.js
// ВЕРСИЯ "НАЗАД В БУДУЩЕЕ 5.0" - КЛАССИКА С НОВЫМИ ФИШКАМИ

const tg = window.Telegram.WebApp;
tg.ready();

// --- DOM Элементы ---
const body = document.body;
const chatWindow = document.getElementById('chat-window');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const newChatButton = document.getElementById('new-chat-button');
const chatList = document.getElementById('chat-list');
const menuButton = document.getElementById('menu-button');
const pageOverlay = document.getElementById('page-overlay');
const chatTitle = document.getElementById('chat-title');
const modelSelectionModal = document.getElementById('model-selection-modal');
const modelCards = document.querySelectorAll('.model-card');
const modalCloseBtn = document.getElementById('modal-close-btn');
const smartPromptsContainer = document.getElementById('smart-prompts-container');
const scrollToBottomBtn = document.getElementById('scroll-to-bottom-btn');
const themeSwitcher = document.getElementById('theme-switcher');
const emptyChatPlaceholder = document.querySelector('.empty-chat-placeholder');

// --- Состояние и Константы ---
let currentChatId = null;
let userId = null;
let newChatModel = 'gemini-2.5-flash';
const ICONS = {
    COPY: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M16 1H4a2 2 0 00-2 2v14h2V3h12V1zm3 4H8a2 2 0 00-2 2v14a2 2 0 002 2h11a2 2 0 002-2V7a2 2 0 00-2-2zm0 16H8V7h11v14z"></path></svg>`,
    CHECK: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"></path></svg>`,
    DELETE: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 7H20M10 11V17M14 11V17M5 7L6 19C6 20.1046 6.89543 21 8 21H16C17.1046 21 18 20.1046 18 19L19 7M9 7V4C9 3.44772 9.44772 3 10 3H14C14.5523 3 15 3.44772 15 4V7" stroke-width="1.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/></svg>`
};
const ALL_SMART_PROMPTS = [ "Объясни квантовые вычисления простыми словами", "Напиши пост для соцсетей о запуске нового продукта", "Составь план путешествия по Италии на 10 дней", "Какая основная идея книги 'Sapiens'?", "Придумай 5 идей для стартапа в сфере экологии", "Напиши короткий рассказ в стиле киберпанк", "Что такое черные дыры и как они образуются?", "Сравни и противопоставь Python и JavaScript", "Составь программу тренировок для набора мышечной массы", "Напиши простой рецепт пасты Карбонара" ];

// --- Функции-помощники ---
function getModelDisplayName(modelId) {
    if (modelId && modelId.includes('pro')) return 'Gemini 2.5 Pro';
    if (modelId && modelId.includes('flash')) return 'Gemini 2.5 Flash';
    return 'Gemini';
}
async function apiCall(endpoint, body) {
    const response = await fetch(endpoint, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body) });
    if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
    return response.json();
}

// --- Функции UI ---
function toggleSidebar() { body.classList.toggle('sidebar-open'); }
function closeSidebar() { body.classList.remove('sidebar-open'); }

function managePlaceholder(show) {
    const placeholder = document.querySelector('.empty-chat-placeholder');
    if (placeholder) {
        placeholder.classList.toggle('hidden', !show);
    }
    if (show) {
        renderSmartPrompts();
    } else {
        smartPromptsContainer.innerHTML = '';
    }
}

function renderEmptyState() {
    chatWindow.innerHTML = `<div class="empty-chat-placeholder"><div class="icon">✨</div><h3>AI Ассистент</h3><p>Начните новый диалог или выберите один из существующих.</p></div>`;
    chatTitle.textContent = "Новый диалог";
    managePlaceholder(true);
}

function renderSmartPrompts() {
    smartPromptsContainer.innerHTML = '';
    const shuffledPrompts = [...ALL_SMART_PROMPTS].sort(() => 0.5 - Math.random()).slice(0, 4);
    shuffledPrompts.forEach((prompt, index) => {
        const card = document.createElement('div');
        card.className = 'prompt-card';
        card.textContent = prompt;
        card.style.animationDelay = `${index * 100}ms`;
        card.onclick = () => {
            messageInput.value = prompt;
            handleSendMessage();
        };
        smartPromptsContainer.appendChild(card);
    });
}

// ВОЗВРАЩАЕМ НАШУ ФУНКЦИЮ ДЛЯ АНИМАЦИИ НАБОРА ТЕКСТА
function typeMessage(element, text) {
    const words = text.split(' ');
    let wordIndex = 0;
    element.textContent = '';
    
    function addWord() {
        if (wordIndex < words.length) {
            element.textContent += (wordIndex > 0 ? ' ' : '') + words[wordIndex];
            wordIndex++;
            chatWindow.scrollTop = chatWindow.scrollHeight;
            setTimeout(addWord, 70); // Скорость появления слов
        }
    }
    addWord();
}

function addMessageToUI(text, type, shouldAnimate = false) {
    const wrapper = document.createElement('div');
    wrapper.className = `message-wrapper ${type === 'user' ? 'user-message-wrapper' : 'bot-message-wrapper'}`;
    if (type === 'user' || shouldAnimate) wrapper.classList.add('float-in');

    const msgEl = document.createElement('div');
    msgEl.className = `message ${type === 'user' ? 'user-message' : 'bot-message'}`;
    
    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-btn';
    copyBtn.title = 'Копировать';
    copyBtn.innerHTML = ICONS.COPY;

    wrapper.appendChild(msgEl);
    wrapper.appendChild(copyBtn);
    chatWindow.appendChild(wrapper);

    // Включаем анимацию для ответа бота
    if (type === 'bot' && shouldAnimate) {
        typeMessage(msgEl, text);
    } else {
        msgEl.textContent = text;
    }
    chatWindow.scrollTop = chatWindow.scrollHeight;
}


function showTypingIndicator() {
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper avatar-indicator-wrapper';
    const avatarSVG = `<div class="avatar-svg-container"><svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="24" cy="24" r="22" fill="#DBEAFE" stroke="#BFDBFE" stroke-width="2"/><g class="avatar-body"><path d="M36 38C36 31.3726 30.6274 26 24 26C17.3726 26 12 31.3726 12 38" stroke-width="2" stroke-linecap="round"/><g class="avatar-eyes"><circle cx="20" cy="22" r="1.5"/><circle cx="28" cy="22" r="1.5"/></g><g class="avatar-brain"><path d="M24 10C21.7909 10 20 11.7909 20 14C20 16.2091 21.7909 18 24 18C26.2091 18 28 16.2091 28 14C28 11.7909 26.2091 10 24 10Z"/></g></g></svg></div>`;
    wrapper.innerHTML = avatarSVG;
    const path = wrapper.querySelector('.avatar-body path');
    const eyes = wrapper.querySelectorAll('.avatar-eyes circle');
    const brain = wrapper.querySelector('.avatar-brain path');
    if (path) path.style.stroke = 'var(--accent-color)';
    if (eyes) eyes.forEach(e => e.style.fill = 'var(--accent-color)');
    if (brain) brain.style.fill = 'var(--accent-color)';
    
    chatWindow.appendChild(wrapper);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return wrapper;
}


function renderChatList(chats) {
    const chatIcon = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M10 17H14M7 12H17M7 7H17M4 21V5C4 3.89543 4.89543 3 6 3H18C19.1046 3 20 3.89543 20 5V17C20 18.1046 19.1046 19 18 19H7.23607C6.49525 19 5.81152 19.4477 5.52786 20.1464L4 21Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
    chatList.innerHTML = '';
    chats.forEach(chat => {
        const el = document.createElement('div');
        el.className = 'chat-item';
        el.dataset.chatId = chat.chat_id;
        const modelName = getModelDisplayName(chat.model_version);
        el.innerHTML = `<div class="chat-item-content"><span class="icon">${chatIcon}</span><span class="chat-title-text">${chat.title}</span></div><span class="model-badge">${modelName}</span><button class="delete-btn" title="Удалить чат">${ICONS.DELETE}</button>`;
        if (chat.chat_id === currentChatId) {
            el.classList.add('active');
            chatTitle.textContent = chat.title;
        }
        chatList.appendChild(el);
    });
}

// --- Основные функции логики ---
async function loadChatHistory(chatId) {
    currentChatId = chatId;
    chatWindow.innerHTML = '';
    managePlaceholder(false);
    document.querySelectorAll('.chat-item.active').forEach(el => el.classList.remove('active'));
    const activeItem = document.querySelector(`.chat-item[data-chat-id="${chatId}"]`);
    if(activeItem) activeItem.classList.add('active');

    const loadingIndicator = showTypingIndicator();
    try {
        const data = await apiCall('/api/get_chat_history', { chat_id: chatId });
        loadingIndicator.remove();
        if (data.history.length > 0) {
            data.history.forEach(msg => addMessageToUI(msg.parts[0].text, msg.role === 'user' ? 'user' : 'bot', false));
        } else {
            managePlaceholder(false);
            chatWindow.innerHTML = '';
        }
    } catch (error) {
        loadingIndicator.remove();
        addMessageToUI('Не удалось загрузить историю.', 'bot', true);
    }
    await loadUserChats(true);
}

async function loadUserChats(keepCurrent = false) {
    if (!userId) return;
    try {
        const data = await apiCall('/api/get_user_chats', { user_id: userId });
        renderChatList(data.chats);
        if (!keepCurrent && data.chats.length > 0) {
            await loadChatHistory(data.chats[0].chat_id);
        } else if (data.chats.length === 0 && !currentChatId) {
            startNewChatMode();
        }
    } catch(error) {
        console.error("Не удалось загрузить чаты:", error);
        startNewChatMode();
    }
}

function startNewChatMode() {
    closeSidebar();
    currentChatId = null;
    chatTitle.textContent = "Новый диалог";
    chatWindow.innerHTML = '';
    renderEmptyState();
}

// ОБНОВЛЕННАЯ ФУНКЦИЯ ОТПРАВКИ СООБЩЕНИЯ
async function handleSendMessage() {
    const text = messageInput.value.trim();
    if (text === '' || sendButton.disabled) return;

    managePlaceholder(false);
    addMessageToUI(text, 'user', true);
    messageInput.value = '';
    messageInput.style.height = 'auto';
    sendButton.disabled = true;

    const loadingIndicator = showTypingIndicator();

    try {
        const payload = { chat_id: currentChatId, user_id: userId, text: text, model_version: currentChatId === null ? newChatModel : undefined };
        
        // Используем нашу стандартную функцию apiCall
        const data = await apiCall('/api/chat', payload);
        
        loadingIndicator.remove();
        
        // Передаем ответ в UI для анимации
        addMessageToUI(data.response, 'bot', true);
        
        if (currentChatId === null) {
            currentChatId = data.chat_id;
        }
        
        // Обновляем список чатов, чтобы увидеть новый заголовок
        await loadUserChats(true);

    } catch (error) {
        loadingIndicator.remove();
        addMessageToUI('Извини, что-то пошло не так на моей стороне.', 'bot', true);
        console.error("Request failed:", error);
    } finally {
        sendButton.disabled = false;
        messageInput.focus();
    }
}


async function handleDeleteChat(chatId) {
    if (!confirm(`Вы уверены, что хотите удалить этот чат? Это действие необратимо.`)) return;
    const chatItem = document.querySelector(`.chat-item[data-chat-id="${chatId}"]`);
    if (chatItem) chatItem.classList.add('deleting');

    try {
        const data = await apiCall('/api/delete_chat', { chat_id: chatId, user_id: userId });
        if (data.success) {
            if (chatId === currentChatId) {
                startNewChatMode();
            }
            renderChatList(data.updated_chats);
        } else {
            alert('Не удалось удалить чат.');
            chatItem?.classList.remove('deleting');
        }
    } catch (error) {
        alert('Произошла ошибка при удалении чата.');
        chatItem?.classList.remove('deleting');
    }
}


// --- Функции темы ---
function applyTheme(theme) {
    if (theme === 'dark') {
        body.classList.add('dark-theme');
    } else {
        body.classList.remove('dark-theme');
    }
}

function handleThemeSwitch() {
    const currentTheme = localStorage.getItem('theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', newTheme);
    applyTheme(newTheme);
}

// --- Инициализация ---
async function init() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);

    try {
        if (tg.initDataUnsafe && tg.initDataUnsafe.user && tg.initDataUnsafe.user.id) {
            userId = tg.initDataUnsafe.user.id;
        } else {
            console.warn("Telegram user data not found. Using mock user ID 123 for testing.");
            userId = 123;
        }
        await loadUserChats();
    } catch(error) {
        renderEmptyState();
        chatTitle.textContent = "Ошибка";
        console.error(error);
    }
}

function showModelModal() { modelSelectionModal.style.display = 'flex'; setTimeout(() => modelSelectionModal.classList.add('visible'), 10); }
function hideModelModal() { modelSelectionModal.classList.remove('visible'); setTimeout(() => modelSelectionModal.style.display = 'none', 300); }

// --- ОБРАБОТЧИКИ СОБЫТИЙ ---
menuButton.addEventListener('click', toggleSidebar);
pageOverlay.addEventListener('click', closeSidebar);
sendButton.addEventListener('click', handleSendMessage);
messageInput.addEventListener('keypress', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendMessage(); } });
newChatButton.addEventListener('click', showModelModal);
modalCloseBtn.addEventListener('click', hideModelModal);
modelSelectionModal.addEventListener('click', e => { if (e.target === modelSelectionModal) hideModelModal(); });
themeSwitcher.addEventListener('click', handleThemeSwitch);

messageInput.addEventListener('input', () => { messageInput.style.height = 'auto'; messageInput.style.height = `${messageInput.scrollHeight}px`; });

chatWindow.addEventListener('scroll', () => { const isScrolledUp = chatWindow.scrollHeight - chatWindow.scrollTop > chatWindow.clientHeight + 100; scrollToBottomBtn.classList.toggle('visible', isScrolledUp); });
scrollToBottomBtn.addEventListener('click', () => { chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: 'smooth' }); });

chatWindow.addEventListener('click', e => {
    const copyBtn = e.target.closest('.copy-btn');
    if (copyBtn) {
        const content = copyBtn.closest('.message-wrapper').querySelector('.message').textContent;
        navigator.clipboard.writeText(content).then(() => { copyBtn.innerHTML = ICONS.CHECK; setTimeout(() => { copyBtn.innerHTML = ICONS.COPY; }, 1500); });
    }
});

modelCards.forEach(card => {
    card.addEventListener('click', () => { newChatModel = card.dataset.model; hideModelModal(); startNewChatMode(); });
});
chatList.addEventListener('click', e => {
    const deleteBtn = e.target.closest('.delete-btn');
    const chatItem = e.target.closest('.chat-item');
    if (deleteBtn && chatItem) {
        e.stopPropagation();
        handleDeleteChat(parseInt(chatItem.dataset.chatId));
    } else if (chatItem) {
        const chatId = parseInt(chatItem.dataset.chatId);
        if (chatId !== currentChatId) {
            closeSidebar();
            loadChatHistory(chatId);
        }
    }
});

init();