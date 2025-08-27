// Variables globales
let currentUser = null;
const API_BASE = window.location.origin;

// Elementos DOM
const loginScreen = document.getElementById('login-screen');
const registerScreen = document.getElementById('register-screen');
const chatScreen = document.getElementById('chat-screen');
const logoutBtn = document.getElementById('logout-btn');
const helpBtn = document.getElementById('help-btn');
const welcomeMessage = document.getElementById('welcome-message');
const chatArea = document.getElementById('chat-area');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const successAlert = document.getElementById('success-alert');
const errorAlert = document.getElementById('error-alert');

// Mostrar pantalla
function showScreen(screen) {
    loginScreen.classList.remove('active');
    registerScreen.classList.remove('active');
    chatScreen.classList.remove('active');
    
    screen.classList.add('active');
    
    // Mostrar/ocultar botón de logout
    logoutBtn.style.display = screen === chatScreen ? 'block' : 'none';
}

// Mostrar alerta
function showAlert(element, message, duration = 3000) {
    element.textContent = message;
    element.style.display = 'block';
    
    setTimeout(() => {
        element.style.display = 'none';
    }, duration);
}

// Añadir mensaje al chat
function addMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
    messageDiv.textContent = text;
    
    chatArea.appendChild(messageDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
    
    // Ocultar mensaje de bienvenida después del primer mensaje
    if (isUser && welcomeMessage.style.display !== 'none') {
        welcomeMessage.style.display = 'none';
    }
}

// Enviar mensaje al asistente
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || !currentUser) return;
    
    // Añadir mensaje del usuario
    addMessage(message, true);
    messageInput.value = '';
    
    try {
        const response = await fetch(`${API_BASE}/api/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                phone: currentUser,
                message: message
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            addMessage(data.response);
        } else {
            addMessage('Lo siento, ocurrió un error al procesar tu mensaje.');
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('Error de conexión. Por favor, intenta nuevamente.');
    }
}

// Login
async function login() {
    const phone = document.getElementById('login-phone').value.trim();
    const password = document.getElementById('login-password').value.trim();
    
    if (!phone || !password) {
        showAlert(errorAlert, 'Por favor, completa todos los campos');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ phone, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentUser = data.phone;
            showScreen(chatScreen);
            showAlert(successAlert, '¡Bienvenido! Has ingresado correctamente');
        } else {
            showAlert(errorAlert, data.detail || 'Error en el login');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert(errorAlert, 'Error de conexión. Intenta nuevamente.');
    }
}

// Registro
async function register() {
    const phone = document.getElementById('register-phone').value.trim();
    const password = document.getElementById('register-password').value.trim();
    const confirm = document.getElementById('register-confirm').value.trim();
    
    if (!phone || !password || !confirm) {
        showAlert(errorAlert, 'Por favor, completa todos los campos');
        return;
    }
    
    if (password !== confirm) {
        showAlert(errorAlert, 'Las contraseñas no coinciden');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                phone, 
                password, 
                confirm_password: confirm 
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(successAlert, '¡Cuenta creada exitosamente! Ya puedes iniciar sesión');
            showScreen(loginScreen);
            
            // Limpiar formulario
            document.getElementById('register-phone').value = '';
            document.getElementById('register-password').value = '';
            document.getElementById('register-confirm').value = '';
        } else {
            showAlert(errorAlert, data.detail || 'Error en el registro');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert(errorAlert, 'Error de conexión. Intenta nuevamente.');
    }
}

// Logout
function logout() {
    currentUser = null;
    showScreen(loginScreen);
    chatArea.innerHTML = '';
    welcomeMessage.style.display = 'block';
}

// Mostrar ayuda
function showHelp() {
    addMessage('Puedo ayudarte con:\n• Información sobre aplicaciones\n• Consejos de ciberseguridad\n• Recordatorios importantes\n• Respuestas a tus preguntas\n\nSolo háblame naturalmente!');
}

// Event Listeners
document.getElementById('login-btn').addEventListener('click', login);
document.getElementById('register-btn').addEventListener('click', register);
document.getElementById('goto-register').addEventListener('click', () => showScreen(registerScreen));
document.getElementById('goto-login').addEventListener('click', () => showScreen(loginScreen));
logoutBtn.addEventListener('click', logout);
helpBtn.addEventListener('click', showHelp);
sendBtn.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Inicialización
showScreen(loginScreen);
