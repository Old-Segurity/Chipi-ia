#main.py

"""

Aplicación principal de Chipi IA

Asistente virtual diseñado específicamente para adultos mayores

"""

import re
import os
import sys
import threading
import requests
import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import timedelta

# Añadir al inicio de main.py, después de las importaciones
from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'system')
Config.set('graphics', 'multisamples', '0')  # Mejorar rendimiento
Config.set('kivy', 'exit_on_escape', '0')  # Evitar salida accidental

# Configuración de Kivy
import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.button import Button

# Módulos internos
from src.config import AppConfig, UIConfig
from src.database import DatabaseManager
from src.memory import MemoryManager
from src.apps import AppLauncher
from src.assistant import ChipiAssistant
from src.utils import Logger, SecurityManager, TextUtils
from src.audio import AudioManager

# Añadir después de las importaciones existentes
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.clipboard import Clipboard

# Configuración inicial
Window.softinput_mode = 'below_target'  # Mejorado para teclado numérico

logger = Logger.get_logger(__name__)

def debug_env_variables():
    """Función de debug para ver todas las variables"""
    print("=" * 60)
    print("DEBUG: VARIABLES DE ENTORNO DISPONIBLES")
    print("=" * 60)
    # Todas las variables
    all_vars = dict(os.environ)
    for key, value in all_vars.items():
        if any(k in key for k in ['API', 'KEY', 'CHIPI', 'OPEN']):
            print(f"{key}: {value}")
    print("=" * 60)

# Ejecutar debug al inicio
debug_env_variables()

class SelectableLabel(ButtonBehavior, Label):
    """Label seleccionable que permite copiar texto"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)  # Fondo transparente
        self.background_normal = ''
        self.password_text = None  # Texto de contraseña para copiar selectivamente

    def on_release(self):
        """Copiar texto al hacer clic - prioriza contraseña si existe"""
        if self.password_text:
            # Si hay contraseña detectada, copiar solo la contraseña
            Clipboard.copy(self.password_text)
            # Mostrar mensaje temporal de confirmación
            app = App.get_running_app()
            if hasattr(app, 'sm') and app.sm.has_screen('chat'):
                chat_screen = app.sm.get_screen('chat')
                chat_screen.show_temp_message("Contraseña copiada", duration=2)
        elif self.text:
            # Si no hay contraseña, copiar todo el texto
            Clipboard.copy(self.text)
            # Mostrar mensaje temporal de confirmación
            app = App.get_running_app()
            if hasattr(app, 'sm') and app.sm.has_screen('chat'):
                chat_screen = app.sm.get_screen('chat')
                chat_screen.show_temp_message("Texto copiado", duration=2)

# Cargar variables de entorno antes de cualquier otra operación
def load_environment():
    """Busca y carga variables de entorno desde archivos .env"""
    try:
        # Buscar en directorio current y padres
        current_dir = Path(__file__).parent
        possible_paths = [
            current_dir / '.env',
            current_dir.parent / '.env',
            current_dir / 'config' / '.env',
            current_dir / 'src' / '.env',
            current_dir / 'assets' / '.env'
        ]

        env_loaded = False
        for env_path in possible_paths:
            if env_path.exists():
                try:
                    from dotenv import load_dotenv
                    load_dotenv(env_path, override=True)
                    logger.info(f"✅ Variables de entorno CARGADAS desde: {env_path}")
                    env_loaded = True
                    
                    # Verificación simple
                    api_key = AppConfig.get_api_key()
                    if api_key:
                        logger.info(f"✅ API KEY DETECTADA: {api_key[:12]}...")
                    else:
                        logger.warning("❌ NO SE DETECTÓ API KEY")
                    
                    break
                except Exception as e:
                    logger.error(f"❌ Error cargando {env_path}: {e}")
                    continue

        if not env_loaded:
            logger.warning("⚠️ No se encontró archivo .env, verificando variables del sistema...")
            api_key = AppConfig.get_api_key()
            if api_key:
                logger.info(f"✅ API key encontrada en variables del sistema: {api_key[:12]}...")

        return env_loaded

    except Exception as e:
        logger.error(f"❌ Error cargando variables de entorno: {e}")
        return False

# Ejecutar la carga de entorno al inicio del módulo
load_environment()

class BaseScreen(Screen):
    """Clase base para todas las pantallas con funcionalidad común mejorada"""

    def show_message(self, title: str, message: str, message_type: str = "info",
                    duration: Optional[float] = None):
        """Muestra un popup con diseño profesional y duración configurable"""
        color_map = {
            "success": (0.2, 0.8, 0.2, 1),
            "error": (0.8, 0.2, 0.2, 1),
            "warning": (0.97, 0.85, 0.17, 1),
            "info": (0.2, 0.6, 0.8, 1)
        }

        # Contenedor principal con fondo redondeado
        content = BoxLayout(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10)
        )

        with content.canvas.before:
            Color(*color_map.get(message_type, (0.2, 0.6, 0.8, 1)))
            RoundedRectangle(
                pos=content.pos,
                size=content.size,
                radius=[dp(15),],
            )

        # Título con estilo
        title_label = Label(
            text=title,
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(40)
        )

        # Mensaje principal
        message_label = Label(
            text=message,
            font_size='18sp',
            color=(1, 1, 1, 1),
            text_size=(dp(280), None),
            halign='center',
            valign='middle'
        )

        content.add_widget(title_label)
        content.add_widget(message_label)

        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(dp(340), dp(180)),
            auto_dismiss=True,
            background_color=(0, 0, 0, 0),
            separator_height=0
        )

        # Auto-cerrar después de tiempo específico
        auto_close_duration = duration or (3 if message_type == "success" else None)
        if auto_close_duration:
            Clock.schedule_once(lambda dt: popup.dismiss(), auto_close_duration)

        # Botón de cierre para errores/advertencias sin auto-cierre
        if not auto_close_duration:
            btn = Button(
                text="Entendido",
                size_hint_y=None,
                height=dp(40),
                background_color=(0.15, 0.15, 0.2, 1),
                color=(1, 1, 1, 1))
            btn.bind(on_release=popup.dismiss)
            content.add_widget(btn)

        popup.open()
        return popup

class LoginScreen(BaseScreen):
    """Pantalla de inicio de sesión optimizada para adultos mayores"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = DatabaseManager()
        self.login_attempts = 0
        self.max_attempts = 5

    def on_pre_enter(self):
        """Se ejecuta antes de entrar a la pantalla - Configurar teclado numérico"""
        self.ids.telefono.input_type = 'number'
        self.ids.contrasena.input_type = 'text'

    def validate_and_login(self, phone: str, password: str):
        """Valida credenciales y procede al login con protección contra fuerza bruta"""
        try:
            # Limpiar espacios
            phone = phone.strip()
            password = password.strip()

            # Verificar intentos fallidos
            if self.login_attempts >= self.max_attempts:
                self.show_message("Bloqueado",
                                "Demasiados intentos fallidos. Intenta más tarde.",
                                "error", 5)
                return

            # Validaciones específicadas para adultos mayores
            if not phone:
                self.show_message("Error", "Por favor, ingresa tu número de teléfono", "error")
                return

            if not password:
                self.show_message("Error", "Por favor, ingresa tu contraseña", "error")
                return

            # Validar formato de teléfono colombiano
            if not self._validate_colombian_phone(phone):
                self.show_message(
                    "Error",
                    "El número debe tener 10 dígitos\nEjemplo: 3001234567",
                    "error"
                )
                return

            # Intentar login
            if self.db_manager.validate_user(phone, password):
                logger.info(f"Login exitoso para usuario: {phone}")
                self.login_attempts = 0  # Resetear contador
                app = App.get_running_app()
                chat_screen = app.sm.get_screen('chat')
                chat_screen.set_user(phone)
                app.sm.current = 'chat'
                self.show_message("Bienvenido!", "Has ingresado correctamente", "success")
            else:
                self.login_attempts += 1
                remaining = self.max_attempts - self.login_attempts
                if remaining > 0:
                    self.show_message(
                        "Error de acceso",
                        f"Número o contraseña incorrectos\nIntentos restantes: {remaining}",
                        "error"
                    )
                else:
                    self.show_message(
                        "Cuenta bloqueada",
                        "Demasiados intentos fallidos. Intenta más tarde.",
                        "error",
                        5
                    )

        except Exception as e:
            logger.error(f"Error en login: {e}")
            self.show_message("Error", "Ocurrió un problema. Intenta nuevamente.", "error")

    def _validate_colombian_phone(self, phone: str) -> bool:
        """Valida que sea un número de teléfono colombiano válido"""
        return phone.isdigit() and len(phone) == 10 and phone.startswith('3')

class RegisterScreen(BaseScreen):
    """Pantalla de registro con validaciones mejoradas"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = DatabaseManager()

    def on_pre_enter(self):
        """Se ejecuta antes de entrar a la pantalla - Configurar teclados"""
        self.ids.telefono.input_type = 'number'
        self.ids.contrasena.input_type = 'text'
        self.ids.confirmar_contrasena.input_type = 'text'

    def validate_and_register(self, phone: str, password: str, confirm_password: str):
        """Valida datos y registra nuevo usuario"""
        try:
            # Limpiar espacios
            phone = phone.strip()
            password = password.strip()
            confirm_password = confirm_password.strip()

            # Validaciones paso a paso para claridad
            if not self._validate_phone_format(phone):
                return

            if not self._validate_password_strength(password):
                return

            if not self._validate_password_match(password, confirm_password):
                return

            # Verificar si el usuario ya existe
            if self.db_manager.user_exists(phone):
                self.show_message(
                    "Usuario existente",
                    "Este número ya está registrado\n¿Olvidaste tu contraseña?",
                    "warning"
                )
                return

            # Registrar usuario
            if self.db_manager.create_user(phone, password):
                logger.info(f"Usuario registrado exitosamente: {phone}")
                self.show_message(
                    "Registro exitoso!",
                    "Tu cuenta ha sido creada\nYa puedes iniciar sesión",
                    "success"
                )

                # Limpiar campos
                self.ids.telefono.text = ""
                self.ids.contrasena.text = ""
                self.ids.confirmar_contrasena.text = ""

                # Ir a login después de 2 segundos
                Clock.schedule_once(lambda dt: self._go_to_login(), 2)
            else:
                self.show_message("Error", "No se pudo crear la cuenta. Intenta nuevamente.", "error")

        except Exception as e:
            logger.error(f"Error en registro: {e}")
            self.show_message("Error", "Ocurrió un problema. Intenta nuevamente.", "error")

    def _validate_phone_format(self, phone: str) -> bool:
        """Valida formato de teléfono con mensajes específicos"""
        if not phone:
            self.show_message("Error", "Por favor, ingresa tu número de teléfono", "error")
            return False

        if not phone.isdigit():
            self.show_message("Error", "El número solo debe contener dígitos", "error")
            return False

        if len(phone) != 10:
            self.show_message("Error", "El número debe tener exactamente 10 dígitos", "error")
            return False

        if not phone.startswith('3'):
            self.show_message("Error", "Debe ser un número de celular colombiano\n(Comenzar con 3)", "error")
            return False

        return True

    def _validate_password_strength(self, password: str) -> bool:
        """Valida fortaleza de contraseña adaptada para adultos mayores"""
        if not password:
            self.show_message("Error", "Por favor, ingresa una contraseña", "error")
            return False

        if len(password) < 6:
            self.show_message("Error", "La contraseña debe tener al menos 6 caracteres", "error")
            return False

        # Contar letras y números
        letters = sum(c.isalpha() for c in password)
        digits = sum(c.isdigit() for c in password)

        if letters < 3 or digits < 3:
            self.show_message("Error", "La contraseña debe tener al menos 3 letras y 3 números", "error")
            return False

        return True

    def _validate_password_match(self, password: str, confirm_password: str) -> bool:
        """Valida que las contraseñas coincidan"""
        if password != confirm_password:
            self.show_message("Error", "Las contraseñas no coinciden\nPor favor, verifica", "error")
            return False

        return True

    def _go_to_login(self):
        """Navega a la pantalla de login"""
        App.get_running_app().sm.current = 'login'

class ChatScreen(BaseScreen):
    telefono = StringProperty("")
    bienvenida_text = StringProperty(
        "Hola! Soy Chipi, tu asistente virtual\n\n"
        "Estoy aquí para ayudarte con:\n"
        "• Abrir aplicaciones\n"
        "• Recordar información importante\n"
        "• Responder tus preguntas\n"
        "• Guardar contactos y direcciones\n"
        "• Cualquier consulta que tengas\n\n"
        "Puedes hablarme de forma natural, como si fuera tu nieto"
    )
    current_message_widget = ObjectProperty(None, allownone=True)
    audio_playing = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.memory_manager = None
        self.assistant = None
        self.app_launcher = AppLauncher()
        self.audio_manager = AudioManager()
        self.keyboard_mode = "text"
        self.audio_playing = False
        self.is_processing = False  # Evitar múltiples mensajes simultáneos
        self.temp_messages = []  # Para mensajes temporales

        # Programar verificaciones periódicas
        Clock.schedule_interval(self._check_keyboard, 0.5)
        Clock.schedule_interval(self._update_audio_button, 0.1)

    def show_help_message(self):
        """Muestra mensaje de ayuda formateado correctamente"""
        help_text = (
            "Puedo ayudarte con:\n"
            "• Abrir aplicaciones\n"
            "• Guardar contraseñas\n"
            "• Crear recordatorios\n"
            "• Responder preguntas\n"
            "• Guardar información personal\n\n"
            "Solo háblame naturalmente!"
        )
        self.add_message(help_text, "ia", auto_scroll=True)

    def _update_audio_button(self, dt):
        """Actualiza el estado del botón de audio"""
        try:
            self.audio_playing = self.audio_manager.is_audio_playing()
        except Exception as e:
            logger.error(f"Error actualizando botón de audio: {e}")

    def stop_audio(self):
        """Detiene la reproducción de audio con mensaje temporal"""
        try:
            if self.audio_manager.stop_audio():
                self.audio_playing = False
                # Mostrar mensaje temporal que se auto-elimina
                temp_message = self.add_message("Audio detenido", "ia",
                                              auto_scroll=True)
                # Programar eliminación después de 3 segundos
                Clock.schedule_once(lambda dt: self._remove_temp_message(temp_message), 3)
        except Exception as e:
            logger.error(f"Error deteniendo audio: {e}")

    def _remove_temp_message(self, message_widget):
        """Elimina un mensaje temporal del chat"""
        try:
            if message_widget and message_widget[0] in self.ids.chat_area.children:
                self.ids.chat_area.remove_widget(message_widget[0])
        except Exception as e:
            logger.error(f"Error eliminando mensaje temporal: {e}")

    def show_temp_message(self, message: str, duration: float = 2.0):
        """Muestra un mensaje temporal de confirmación"""
        temp_popup = Popup(
            title='',
            content=Label(text=message, font_size='16sp'),
            size_hint=(None, None),
            size=(dp(200), dp(100)),
            auto_dismiss=True,
            background_color=(0, 0, 0, 0)
        )
        temp_popup.open()
        # Cerrar automáticamente después del tiempo especificado
        Clock.schedule_once(lambda dt: temp_popup.dismiss(), duration)

    def _check_keyboard(self, dt):
        """Verifica periódicamente el estado del teclado para prevenir bugs"""
        try:
            from kivy.core.window import Window
            if hasattr(Window, 'keyboard') and Window.keyboard:
                # Forzar la actualización del teclado si está activo
                Window.keyboard.update_selection()
        except Exception as e:
            logger.error(f"Error verificando teclado: {e}")

    def on_pre_enter(self):
        """Se ejecuta antes de entrar a la pantalla"""
        self.ids.chat_area.clear_widgets()
        self.ids.bienvenida_label.opacity = 1
        self.ids.bienvenida_label.height = self.ids.bienvenida_label.texture_size[1] + dp(20)
        self._reset_keyboard()
        self.is_processing = False
        self.temp_messages = []

    def on_leave(self):
        """Se ejecuta al salir de la pantalla"""
        self._hide_keyboard()
        # Detener audio al salir
        if self.audio_playing:
            self.audio_manager.stop_audio()
        # Limpiar mensajes temporales
        self._cleanup_temp_messages()

    def _cleanup_temp_messages(self):
        """Limpia todos los mensajes temporales"""
        for temp_msg in self.temp_messages:
            self._remove_temp_message(temp_msg)
        self.temp_messages = []

    def _reset_keyboard(self):
        """Reinicia el teclado para prevenir bugs"""
        try:
            from kivy.core.window import Window
            if hasattr(Window, 'keyboard') and Window.keyboard:
                Window.keyboard.release()
            # Forzar el modo de teclado por defecto
            self.ids.entrada.input_type = 'text'
        except Exception as e:
            logger.error(f"Error reiniciando teclado: {e}")

    def _hide_keyboard(self):
        """Oculta el teclado virtual"""
        try:
            from kivy.core.window import Window
            Window.release_keyboard()
            if hasattr(Window, 'keyboard') and Window.keyboard:
                Window.keyboard.release()
        except Exception as e:
            logger.error(f"Error ocultando teclado: {e}")

    def set_keyboard_type(self, keyboard_type):
        """Configura el tipo de teclado según la aplicación"""
        self.keyboard_mode = keyboard_type
        if keyboard_type == "number":
            self.ids.entrada.input_type = 'number'
            # Forzar mostrar teclado numérico inmediatamente
            if not self.ids.entrada.focus:
                self.ids.entrada.focus = True
                Clock.schedule_once(lambda dt: setattr(self.ids.entrada, 'focus', False), 0.1)
        else:
            self.ids.entrada.input_type = 'text'

    def on_touch_down(self, touch):
        """Cierra el teclado cuando se toca fuera del TextInput"""
        if self.ids.entrada.focus:
            if not self.ids.entrada.collide_point(*touch.pos):
                self.ids.entrada.focus = False
                self._hide_keyboard()
        return super().on_touch_down(touch)

    def set_user(self, phone: str):
        """Configura el usuario activo"""
        self.telefono = phone
        self.memory_manager = MemoryManager(phone)
        self.assistant = ChipiAssistant(self.memory_manager, self.app_launcher)
        logger.info(f"Usuario configurado: {phone}")

        # Verificar estado de la API al iniciar sesión
        self._check_api_status()

    def _check_api_status(self):
        """Verifica y muestra el estado de la API"""
        api_key = AppConfig.get_api_key()
        has_internet = AppConfig.has_internet_connection()
        
        # Debug info más detallado
        logger.info(f"API Key encontrada: {api_key is not None}")
        logger.info(f"Conexión a internet: {has_internet}")
        
        if api_key:
            logger.info(f"Longitud API Key: {len(api_key)}")
            logger.info(f"Prefijo API Key: {api_key[:10]}")
        
        if not api_key:
            self.add_message(
                "⚠️ Modo local activado: No se encontró API key\n\n"
                "Puedo ayudarte con:\n"
                "• Abrir aplicaciones\n• Guardar contraseñas\n• Recordatorios\n"
                "• Información personal\n\n"
                "Para IA completa: Configura CHIPI_API_KEY en .env",
                "ia", auto_scroll=True
            )
        elif not has_internet:
            self.add_message(
                "⚠️ Sin conexión a internet\n\n"
                "Funciones locales disponibles:\n"
                "• Abrir aplicaciones\n• Contraseñas guardadas\n"
                "• Recordatorios\n• Información personal",
                "ia", auto_scroll=True
            )
        else:
            # Probar conexión con la API de forma más detallada
            connection_test = self._test_api_connection_detailed()
            if "✅" in connection_test:
                self.add_message("✅ Conectado a IA avanzada", "ia", auto_scroll=True)
            else:
                self.add_message(
                    f"⚠️ {connection_test}\n\nUsando modo local mejorado",
                    "ia", auto_scroll=True
                )

    def _test_api_connection_detailed(self):
        """Prueba detallada de conexión con la API"""
        try:
            api_key = AppConfig.get_api_key()
            if not api_key:
                return "❌ No se encontró API key"
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/chipi-ai/chipi-assistant",
                "X-Title": "Chipi IA Assistant"
            }
            
            test_data = {
                "model": "anthropic/claude-3.5-sonnet",
                "messages": [{"role": "user", "content": "Hola, responde con 'OK'"}],
                "max_tokens": 5,
                "temperature": 0.1
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=test_data,
                timeout=15
            )
            
            logger.info(f"Status code: {response.status_code}")
            logger.info(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                return "✅ Conexión con API exitosa"
            elif response.status_code == 401:
                return "❌ API key inválida o no autorizada"
            elif response.status_code == 429:
                return "❌ Límite de tasa excedido"
            else:
                return f"❌ Error en API: {response.status_code} - {response.text[:100]}..."
                
        except requests.Timeout:
            return "❌ Timeout: La API no respondió a tiempo"
        except requests.ConnectionError:
            return "❌ Error de conexión: No se pudo conectar a la API"
        except Exception as e:
            return f"❌ Error inesperado: {str(e)}"

    def _extract_password_from_message(self, texto: str) -> Optional[str]:
        """Extrae la contraseña de un mensaje de recomendación - Ahora incluye numéricas"""
        patterns = [
            r"te recomiendo:?\s*([A-Za-z0-9]{4,})",
            r"contraseña segura:?\s*([A-Za-z0-9]{4,})",
            r"recomiendo:?\s*([A-Za-z0-9]{4,})",
            r":\s*([A-Za-z0-9]{4,})",
            r"para.*?:?\s*([A-Za-z0-9]{4,})",
            r"([A-Za-z0-9]{4,})(?=\\n|$|\\s|[.,!?])",
            # Patrones específicos para contraseñas numéricas
            r"(\d{4,})(?=\\n|$|\\s|[.,!?])",  # 4 o más dígitos seguidos
            r"código:?\s*(\d{4,})",  # Para códigos numéricos
            r"pin:?\s*(\d{4,})",  # Para PINs
            r"clave:?\s*(\d{4,})",  # Para claves numéricas
        ]

        texto_sin_saltos = texto.replace('\n', ' ')
        for pattern in patterns:
            match = re.search(pattern, texto_sin_saltos)
            if match:
                password_candidate = match.group(1)
                # Verificar que sea una contraseña plausible
                # Para alfanuméricas: mínimo 4 caracteres con letras y números
                # Para numéricas: mínimo 4 dígitos
                if (len(password_candidate) >= 4 and
                    ((any(c.isalpha() for c in password_candidate) and
                      any(c.isdigit() for c in password_candidate)) or
                     password_candidate.isdigit())):
                    return password_candidate

        # Búsqueda adicional para patrones comunes de contraseñas
        additional_patterns = [
            r"es\s+([A-Za-z0-9]{4,})",
            r"(\b\d{4,6}\b)",  # Números de 4-6 dígitos (típicos PINs)
            r"(\b[A-Za-z0-9]{6,12}\b)",  # Contraseñas de 6-12 caracteres
        ]

        for pattern in additional_patterns:
            match = re.search(pattern, texto_sin_saltos)
            if match:
                password_candidate = match.group(1)
                if len(password_candidate) >= 4:
                    return password_candidate

        return None

    def add_message(self, texto: str, emisor: str, auto_scroll: bool = True,
                   is_progressive: bool = False, is_temporary: bool = False):
        """Añade un mensaje al chat con diseño optimizado"""
        # Formatear texto correctamente
        texto = TextUtils.format_message(texto)

        # Ocultar contraseñas en mensajes de usuario
        if emisor == "usuario" and self._is_password_command(texto):
            texto = self._mask_password(texto)

        max_width = int(self.width * 0.75) if self.width else 300

        container = BoxLayout(size_hint_y=None, height=0, padding=[0, 0, 0, 0])

        if emisor == "usuario":
            container.padding = [dp(40), 0, 0, 0]
            color_bubble = UIConfig.USER_BUBBLE_COLOR
            color_text = UIConfig.USER_TEXT_COLOR
            halign = 'right'
        else:
            container.padding = [0, 0, dp(40), 0]
            color_bubble = UIConfig.BOT_BUBBLE_COLOR
            color_text = UIConfig.BOT_TEXT_COLOR
            halign = 'left'

        # Detectar si es un mensaje con contraseña (solo para IA)
        password = None
        if emisor == "ia":
            password = self._extract_password_from_message(texto)

        # Usar SelectableLabel para todos los mensajes
        msg = SelectableLabel(
            text=texto,
            font_size='16sp',
            size_hint=(None, None),
            halign=halign,
            valign='middle',
            text_size=(max_width, None),
            color=color_text,
            padding=(dp(16), dp(12))
        )

        # Si se detectó una contraseña, guardarla para copia selectiva
        if password:
            msg.password_text = password

        msg.texture_update()
        msg.size = (max_width, msg.texture_size[1] + dp(24))

        # Burbuja con esquinas redondeadas
        with msg.canvas.before:
            Color(*color_bubble)
            RoundedRectangle(pos=msg.pos, size=msg.size, radius=[20, 20, 20, 20])

        def update_rect(instance, value):
            rect = msg.canvas.before.children[-1]
            rect.pos = msg.pos
            rect.size = msg.size

        msg.bind(pos=update_rect, size=update_rect)

        # Configuración especial para mensajes progresivos
        if is_progressive:
            msg.bind(text=self.update_message_size)

        container.add_widget(msg)
        container.height = msg.height + dp(12)

        self.ids.chat_area.add_widget(container)

        # Desplazar al fondo
        if auto_scroll:
            Clock.schedule_once(lambda dt: self.scroll_to_bottom(), 0.1)

        message_data = (container, msg)

        # Guardar mensajes temporales para limpieza
        if is_temporary:
            self.temp_messages.append(message_data)

        return message_data

    def update_message_size(self, instance, value):
        """Actualiza dinámicamente el tamaño del mensaje"""
        # Actualizar solo si hay un cambio significativo para reducir parpadeo
        new_height = instance.texture_size[1] + dp(24)
        if abs(new_height - instance.height) > dp(5):
            instance.size = (instance.width, new_height)
            # Ajustar el contenedor padre
            if instance.parent:
                instance.parent.height = instance.height + dp(12)
            self.scroll_to_bottom()

    def _is_password_command(self, text: str) -> bool:
        """Detecta si es un comando para guardar contraseña"""
        patterns = [
            r"mi\s+contraseña\s+de",
            r"guarda\s+la\s+contraseña\s+de",
            r"la\s+clave\s+de"
        ]
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in patterns)

    def _mask_password(self, text: str) -> str:
        """Oculta la contraseña en el texto"""
        parts = text.split(' es ')
        if len(parts) > 1:
            return f"{parts[0]} es [contraseña oculta]"
        return text

    def scroll_to_bottom(self):
        """Desplaza el ScrollView al fondo"""
        # Scroll to bottom (0 is bottom, 1 is top)
        self.ids.sv.scroll_y = 0

    def send_message(self):
        """Procesa y envía mensaje del usuario con protección contra spam"""
        if self.is_processing:
            return

        try:
            texto = self.ids.entrada.text.strip()
            if not texto:
                return

            # Marcar como procesando
            self.is_processing = True

            # Detener audio actual si está reproduciendo
            if self.audio_manager.is_audio_playing():
                self.audio_manager.stop_audio()

            # Ocultar teclado inmediatamente
            self.ids.entrada.focus = False
            self._hide_keyboard()

            # Ocultar mensaje de bienvenida
            bienvenida = self.ids.bienvenida_label
            if bienvenida.opacity != 0:
                bienvenida.opacity = 0
                bienvenida.height = 0

            # Añadir mensaje del usuario
            if self._is_password_command(texto):
                parts = texto.split(' es ')
                if len(parts) >= 2:
                    hidden_text = f"{parts[0]} es {'*' * len(parts[1])}"
                    self.add_message(hidden_text, "usuario", auto_scroll=True)
                else:
                    self.add_message(texto, "usuario", auto_scroll=True)
            else:
                self.add_message(texto, "usuario", auto_scroll=True)

            # Mostrar indicador de escritura
            writing_indicator = self.add_message("Escribiendo...", "ia", auto_scroll=True, is_temporary=True)

            # Procesar en segundo plano para no bloquear la UI
            def process_in_background():
                try:
                    respuesta = self.assistant.process_command(texto)
                    # Programar actualización en el hilo principal
                    Clock.schedule_once(lambda dt: self._show_response(
                        respuesta, writing_indicator
                    ), 0)
                except Exception as e:
                    logger.error(f"Error procesando comando: {e}")
                    Clock.schedule_once(lambda dt: self._show_error(writing_indicator), 0)

            # Ejecutar en hilo separado
            threading.Thread(target=process_in_background, daemon=True).start()

            # Limpiar entrada
            self.ids.entrada.text = ""

        except Exception as e:
            logger.error(f"Error al enviar mensaje: {e}")
            self.is_processing = False
            self.add_message(
                "Lo siento, ocurrió un error. ¿Puedes intentar nuevamente?",
                "ia",
                auto_scroll=True
            )

    def _show_response(self, respuesta, writing_indicator):
        """Muestra la respuesta del asistente"""
        try:
            # Remover indicador de escritura
            if writing_indicator and writing_indicator[0] in self.ids.chat_area.children:
                self.ids.chat_area.remove_widget(writing_indicator[0])

            # Añadir mensaje completo directamente
            self.add_message(respuesta, "ia", auto_scroll=True)

            # Iniciar audio inmediatamente si es respuesta larga
            if len(respuesta) > self.audio_manager.min_length_for_audio:
                threading.Thread(
                    target=self.audio_manager.speak_text,
                    args=(respuesta,),
                    daemon=True
                ).start()
        finally:
            self.is_processing = False

    def _show_error(self, writing_indicator):
        """Maneja errores en el procesamiento"""
        try:
            if writing_indicator and writing_indicator[0] in self.ids.chat_area.children:
                self.ids.chat_area.remove_widget(writing_indicator[0])
            self.add_message(
                "Lo siento, ocurrió un problema al procesar tu solicitud",
                "ia",
                auto_scroll=True
            )
        finally:
            self.is_processing = False

class ChipiApp(App):
    """Aplicación principal de Chipi IA mejorada"""

    def build(self):
        """Construye la aplicación con manejo de errores"""
        try:
            self.title = "CHIPI IA - Asistente para Adultos Mayores"
            self.icon = str(Path("assets/icon.png")) if Path("assets/icon.png").exists() else None

            # Verificación exhaustiva de API y conexión
            self._check_system_status()

            # Configurar gestor de pantallas
            self.sm = ScreenManager(transition=FadeTransition(duration=0.3))

            # Añadir pantallas
            self.sm.add_widget(LoginScreen(name='login'))
            self.sm.add_widget(RegisterScreen(name='register'))
            self.sm.add_widget(ChatScreen(name='chat'))

            # Pantalla inicial
            self.sm.current = 'login'

            logger.info("Aplicación Chipi IA iniciada correctamente")
            return self.sm

        except Exception as e:
            logger.critical(f"Error crítico al construir la aplicación: {e}")
            # Mostrar error al usuario
            self.show_startup_error(str(e))
            return BoxLayout()  # Layout vacío como fallback

    def _check_system_status(self):
        """Verifica el estado del sistema y muestra información detallada"""
        # Verificar API key
        api_key = AppConfig.get_api_key()
        has_internet = AppConfig.has_internet_connection()

        logger.info("=" * 50)
        logger.info("DIAGNÓSTICO DEL SISTEMA CHIPI IA")
        logger.info("=" * 50)

        if api_key:
            logger.info(f"✅ API KEY: {api_key[:12]}...{api_key[-4:]}")
            logger.info(f"✅ TIPO: OpenRouter")
            # Probar conexión con la API
            connection_test = AppConfig.test_api_connection()
            logger.info(f"🔗 CONEXIÓN API: {connection_test}")
        else:
            logger.warning("❌ API KEY: No encontrada")
            logger.info("ℹ️ Buscando en: CHIPI_API_KEY, OPENROUTER_API_KEY, AI_API_KEY, API_KEY")

        # Mostrar variables de entorno disponibles
        env_vars = ['CHIPI_API_KEY', 'OPENROUTER_API_KEY']
        for var in env_vars:
            value = os.getenv(var)
            if value:
                logger.info(f"ℹ️ {var}: {value[:12]}...")

        logger.info(f"🌐 INTERNET: {'✅ Conectado' if has_internet else '❌ Sin conexión'}")
        logger.info("=" * 50)

    def show_startup_error(self, error_msg):
        """Muestra error de inicio de la aplicación"""
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        content.add_widget(Label(text="Error al iniciar la aplicación", font_size='20sp'))
        content.add_widget(Label(text=error_msg, font_size='16sp'))
        popup = Popup(title='Error', content=content, size_hint=(0.8, 0.4))
        popup.open()

    def logout(self):
        """Cierra sesión del usuario de forma segura"""
        try:
            # Limpiar datos de la sesión
            chat_screen = self.sm.get_screen('chat')
            chat_screen.telefono = ""
            chat_screen.memory_manager = None
            chat_screen.assistant = None
            chat_screen.is_processing = False

            # Detener audio si está reproduciendo
            if hasattr(chat_screen, 'audio_manager') and chat_screen.audio_manager:
                chat_screen.audio_manager.stop_audio()

            # Limpiar mensajes temporales
            chat_screen._cleanup_temp_messages()

            # Volver al login
            self.sm.current = 'login'

            logger.info("Sesión cerrada correctamente")

        except Exception as e:
            logger.error(f"Error al cerrar sesión: {e}")
            # Forzar reinicio si hay error crítico
            self.sm.current = 'login'

def main():
    """Función principal de la aplicación con mejor manejo de errores"""
    try:
        # Configurar directorio de trabajo
        app_dir = Path(__file__).parent
        os.chdir(app_dir)

        # Cargar archivo de interfaz con múltiples ubicaciones posibles
        possible_kv_paths = [
            app_dir / "ui" / "chipi.kv",
            app_dir / "chipi.kv",
            app_dir.parent / "ui" / "chipi.kv"
        ]

        kv_loaded = False
        for kv_path in possible_kv_paths:
            if kv_path.exists():
                Builder.load_file(str(kv_path))
                logger.info(f"Archivo KV cargado: {kv_path}")
                kv_loaded = True
                break

        if not kv_loaded:
            logger.warning("Archivo .kv no encontrado, usando interfaz por defecto")

        # Inicializar base de datos
        DatabaseManager.initialize()

        # Ejecutar aplicación
        ChipiApp().run()

    except Exception as e:
        logger.critical(f"Error crítico en la aplicación: {e}")
        # Mostrar error al usuario antes de cerrar
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Traceback completo: {error_details}")
        sys.exit(1)

if __name__ == "__main__":
    main()