"""
Asistente virtual Chipi optimizado para adultos mayores con IA completa
y enfoque especializado en ciberseguridad
"""

import re
import datetime
import requests
import json
import random
import string
from typing import Optional, Dict, List, Tuple

from .config import AppConfig
from .memory import MemoryManager
from .apps import AppLauncher
from .utils import Logger

logger = Logger.get_logger(__name__)

class ChipiAssistant:
    """Asistente virtual Chipi con funcionalidades específicas para
    adultos mayores, IA completa y especialización en ciberseguridad"""
    
    def __init__(self, memory_manager: MemoryManager, app_launcher: AppLauncher):
        self.memory = memory_manager
        self.apps = app_launcher
        
        # Frases de saludo personalizadas para adultos mayores
        self.greetings = [
            "Hola! Qué gusto saludarte. ¿En qué puedo ayudarte hoy?",
            "Buenos días! Estoy aquí para ayudarte en lo que necesites",
            "Hola querido! ¿Cómo estás? ¿En qué te puedo colaborar?",
            "Qué alegría verte! Dime, ¿en qué te puedo ayudar?"
        ]
        
        # Respuestas de agradecimiento
        self.thanks_responses = [
            "De nada! Siempre es un placer ayudarte",
            "No hay de qué. Estoy aquí para ti siempre que me necesites",
            "Con mucho gusto! Para eso estoy aquí",
            "Fue un placer ayudarte! No dudes en preguntarme lo que necesites"
        ]
        
        # Sistema de contexto mejorado
        self.conversation_context = []
        self.user_preferences = {}
        self.last_command_time = datetime.datetime.now()

    def process_command(self, command: str) -> str:
        """Procesa un comando del usuario con IA completa"""
        command_clean = command.strip().lower()
        original_command = command.strip()
        self.last_command_time = datetime.datetime.now()
        
        try:
            # 1. Verificar comandos de aplicaciones (máxima prioridad)
            app_response = self._handle_app_commands(command_clean)
            if app_response:
                self._add_to_context(original_command, app_response)
                return app_response

            # 2. Verificar comandos de memoria (alta prioridad)
            memory_response = self._handle_memory_commands(command_clean, original_command)
            if memory_response:
                self._add_to_context(original_command, memory_response)
                return memory_response

            # 3. Verificar comandos de ciberseguridad (nueva prioridad alta)
            cybersecurity_response = self._handle_cybersecurity_commands(command_clean, original_command)
            if cybersecurity_response:
                self._add_to_context(original_command, cybersecurity_response)
                return cybersecurity_response

            # 4. Verificar saludos y cortesías
            greeting_response = self._handle_greetings(command_clean)
            if greeting_response:
                self._add_to_context(original_command, greeting_response)
                return greeting_response

            # 5. Verificar comandos de información personal
            personal_response = self._handle_personal_info(command_clean, original_command)
            if personal_response:
                self._add_to_context(original_command, personal_response)
                return personal_response

            # 5.1. Verificar preguntas sobre el creador o empresa
            if "quien es tu creador" in command_clean or "quién te creó" in command_clean:
                response = "Mi creador es Kevin Manga, un experto en tecnología con gran pasión por ayudar a los adultos mayores"
                self._add_to_context(original_command, response)
                return response

            if "cual es tu empresa" in command_clean or "quién te desarrolló" in command_clean:
                response = "Mi empresa creadora es OLD-SECURITY, especializada en soluciones tecnológicas seguras para todas las edades"
                self._add_to_context(original_command, response)
                return response

            # 6. Verificar comandos de fecha and hora
            datetime_response = self._handle_datetime_commands(command_clean)
            if datetime_response:
                self._add_to_context(original_command, datetime_response)
                return datetime_response

            # 7. Usar IA externa con contexto completo (usar el 100% de la IA)
            ai_response = self._get_enhanced_ai_response(original_command)
            self._add_to_context(original_command, ai_response)
            
            # Guardar en memoria para aprendizaje
            self.memory.add_conversation_entry(original_command, ai_response)
            return ai_response

        except Exception as e:
            logger.error(f"Error procesando comando: {e}")
            return "Lo siento, ocurrió un error. ¿Puedes repetir tu pregunta?"

    def _add_to_context(self, user_input: str, response: str):
        """Añade la conversación al contexto para mejorar respuestas futuras"""
        self.conversation_context.append({
            "user": user_input,
            "assistant": response,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        # Mantener solo las últimas 10 interacciones para contexto
        if len(self.conversation_context) > 10:
            self.conversation_context = self.conversation_context[-10:]

    def _handle_app_commands(self, command: str) -> Optional[str]:
        """Maneja comandos para abrir aplicaciones"""
        app_keywords = ["abrir", "abre", "abrime", "activar", "usar", "entrar", "iniciar", "ejecutar"]
        
        if any(keyword in command for keyword in app_keywords):
            # Extraer el nombre de la app del comando
            for pattern in self.apps.APP_PATTERNS:
                match = re.match(pattern, command)
                if match:
                    app_name = match.group(1).strip()
                    return self.apps.launch_app(app_name)
        
        return None

    def _handle_memory_commands(self, command_clean: str, original_command: str) -> Optional[str]:
        """Maneja comandos relacionados con memoria (contraseñas, recordatorios, etc.)"""
        
        # Comando especial para ver todas las contraseñas
        if command_clean == "chipi chipi":
            return self._show_all_passwords()
        
        # Guardar contraseña con múltiples patrones
        password_patterns = [
            r"mi\s+contraseña\s+de\s+(.+?)\s+es\s+(.+)",
            r"guarda\s+la\s+contraseña\s+de\s+(.+?)\s+es\s+(.+)",
            r"la\s+clave\s+de\s+(.+?)\s+es\s+(.+)",
            r"contraseña\s+de\s+(.+?)\s+es\s+(.+)",
            r"clave\s+de\s+(.+?)\s+es\s+(.+)"
        ]
        
        for pattern in password_patterns:
            password_match = re.match(pattern, command_clean)
            if password_match:
                service = password_match.group(1).strip().title()
                password = password_match.group(2).strip()
                return self._save_password(service, password)
        
        # Recordatorios mejorados
        reminder_patterns = [
            r"recuérdame\s+(.+?)\s+a\s+las\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)",
            r"recordatorio\s+(.+?)\s+a\s+las\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)",
            r"recuérdame\s+que\s+(.+?)\s+a\s+las\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)"
        ]
        
        for pattern in reminder_patterns:
            reminder_match = re.match(pattern, command_clean)
            if reminder_match:
                text = reminder_match.group(1).strip()
                time = reminder_match.group(2).strip()
                return self._save_reminder(text, time)
        
        # Ver recordatorios
        if any(phrase in command_clean for phrase in ["qué recordatorios", "mis recordatorios", "recordatorios tengo", "ver recordatorios"]):
            return self._show_reminders()
        
        # Buscar en memoria
        if command_clean.startswith("buscar ") or "qué tengo guardado" in command_clean:
            query = command_clean.replace("buscar ", "").replace("qué tengo guardado", "").strip()
            if query:
                return self._search_memory(query)
        
        # Detectar solicitudes de GENERAR contraseñas (no compartir)
        if any(word in command_clean for word in ["contraseña", "clave", "password"]) and \
           "mi contraseña de" not in command_clean and "chipi chipi" not in command_clean:
            
            # Palabras clave para DETECTAR solicitudes de GENERAR contraseñas
            palabras_generar = [
                "genera", "generar", "recomienda", "recomendar", "crea", "crear", 
                "dame", "quiero", "necesito", "sugiere", "otra", "nueva",
                "inventa", "propón", "propon", "diseña", "elabora", "construye",
                "forma", "haz", "realiza", "desarrolla", "establece", "define",
                "asigna", "configura", "establecer", "definir", "asignar",
                "configurar", "inventar", "proponer", "diseñar", "elaborar",
                "construir", "formar", "hacer", "realizar", "desarrollar"
            ]
            
            # Verificar si es una solicitud para GENERAR contraseña
            es_solicitud_generar = any(palabra in command_clean for palabra in palabras_generar)
            
            if es_solicitud_generar:
                # Es una solicitud para GENERAR contraseña, no para compartir
                return self._recommend_password(command_clean)
            else:
                # Es probablemente un intento de compartir contraseña
                return ("Por tu seguridad, no deberías compartir contraseñas aquí.\n\n"
                        "Si quieres que guarde una contraseña de forma segura, di:\n"
                        "\"Mi contraseña de [servicio] es [contraseña]\"\n\n"
                        "Si quieres que te GENERE una contraseña nueva, di:\n"
                        "\"Genera una contraseña para [servicio]\"\n\n"
                        "Por ejemplo: \"Genera una contraseña para Facebook\"")
        
        return None

    def _handle_cybersecurity_commands(self, command_clean: str, original_command: str) -> Optional[str]:
        """Maneja comandos relacionados con ciberseguridad"""
        
        cybersecurity_keywords = [
            "phishing", "pishing", "fishing",  # Variantes de phishing
            "ransomware", "malware", "virus", "seguridad",
            "contraseña segura", "password seguro", "clave segura",
            "qué es phishing", "qué es pishing", "qué es fishing",
            "qué es ransomware", "qué es malware",
            "cómo crear contraseña segura", "recomendar contraseña",
            "teclado numérico", "teclado alfanumérico", "contraseña para app",
            "ciberseguridad", "hacker", "ataque", "protección", "privacidad",
            "contraseña fuerte", "generar contraseña", "consejos de seguridad",
            "suplantación", "correo falski", "correo fraudulento", "estafa digital"
        ]
        
        if any(keyword in command_clean for keyword in cybersecurity_keywords):
            if any(word in command_clean for word in ["phishing", "pishing", "fishing", "suplantación"]):
                return self._get_phishing_response()
            elif "ransomware" in command_clean:
                return self._get_ransomware_response()
            elif "malware" in command_clean:
                return self._get_malware_response()
            elif any(word in command_clean for word in ["contraseña segura", "password seguro", "recomendar contraseña", "generar contraseña"]):
                return self._recommend_password(command_clean)
            else:
                # Para otros temas de ciberseguridad, usar IA
                return self._get_enhanced_ai_response(original_command)
        
        return None

    def _get_phishing_response(self) -> str:
        return ("El phishing es un tipo de ataque cibernético donde los delincuentes intentan engañarte para que reveles información personal, como contraseñas o números de tarjetas de crédito, mediante correos electrónicos, mensajes o sitios web falsos que parecen legítimos.\n\n"
                "🔒 Consejos para protegerte:\n"
                "• Nunca hagas clic en enlaces sospechosos\n"
                "• Verifica siempre la URL de los sitios web\n"
                "• No compartas información sensible por mensaje\n"
                "• Usa autenticación de two factores\n"
                "• Mantén tu software actualizado")

    def _get_ransomware_response(self) -> str:
        return ("El ransomware es un software malicioso que bloquea tu dispositivo or cifra tus archivos y exige un pago para restaurarlos.\n\n"
                "🔒 Consejos de prevención:\n"
                "• Mantén tu software actualizado\n"
                "• No descargues archivos de fuentes desconocidas\n"
                "• Haz copias de seguridad regularmente\n"
                "• Usa un antivirus confiable\n"
                "• Sé cauteloso con los archivos adjuntos")

    def _get_malware_response(self) -> str:
        return ("El malware es cualquier software dañino diseñado para dañar o infiltrarse en sistemas sin consentimiento. Incluye virus, gusanos, troyanos, etc.\n\n"
                "🔒 Consejos de protección:\n"
                "• Usa antivirus y manténlo actualizado\n"
                "• Evita hacer clic en enlaces sospechosos\n"
                "• No descargues software de fuentes no confiables\n"
                "• Ten cuidado con las redes WiFi públicas\n"
                "• Revisa los permisos de las aplicaciones")

    def _recommend_password(self, command: str) -> str:
        """Recomienda contraseñas seguras según el servicio"""
        # Limpiar y estandarizar el comando
        command_lower = command.lower()
        
        # Detectar si es una solicitud de generación
        palabras_generar = [
            "genera", "generar", "recomienda", "recomendar", "crea", "crear", 
            "dame", "quiero", "necesito", "sugiere", "otra", "nueva",
            "inventa", "propón", "propon", "diseña", "elabora", "construye",
            "forma", "haz", "realiza", "desarrolla", "establece", "define",
            "asigna", "configura", "establecer", "definir", "asignar",
            "configurar", "inventar", "proponer", "diseñar", "elaborar",
            "construir", "formar", "hacer", "realizar", "desarrollar"
        ]
        
        if not any(palabra in command_lower for palabra in palabras_generar):
            # Si no es una solicitud de generación, mostrar mensaje de ayuda
            return ("Por tu seguridad, no deberías compartir contraseñas aquí.\n\n"
                    "Si quieres que guarde una contraseña de forma segura, di:\n"
                    "\"Mi contraseña de [servicio] es [contraseña]\"\n\n"
                    "Si quieres que te GENERE una contraseña nueva, di:\n"
                    "\"Genera una contraseña para [servicio]\"\n\n"
                    "Por ejemplo: \"Genera una contraseña para Facebook\"")
        
        # Verificar si el usuario menciona una aplicación específica
        for app_name in self.apps.APP_PACKAGES:
            if app_name in command_lower:
                keyboard_type = self.apps.get_keyboard_type(app_name)
                if keyboard_type == "number":
                    password = self._generate_numeric_password()
                    recommendation = f"Para {app_name.title()} (teclado numérico), te recomiendo: {password}"
                else:
                    password = self._generate_alphanumeric_password()
                    recommendation = f"Para {app_name.title()} (teclado alfanumérico), te recomiendo: {password}"
                
                return (f"{recommendation}\n\n"
                        " Consejos para tu contraseña:\n"
                        "• No uses la misma contraseña en múltiples sitios\n"
                        "• Cambia tus contraseñas regularmente\n"
                        "• No compartas tus contraseñas con nadie\n"
                        "• Considera usar un gestor de contraseñas")
        
        # Si no se menciona una app, generar una contraseña general
        password = self._generate_alphanumeric_password()
        return (f"Te recomiendo esta contraseña segura: {password}\n\n"
                " Características de esta contraseña:\n"
                "• 12 caracteres de longitud\n"
                "• Mayúsculas y minúsculas\n"
                "• Números incluidos\n"
                "• Sin palabras comunes\n\n"
                "Úsala para una cuenta importante y nunca la repitas en otros servicios.")

    def _generate_numeric_password(self, length=6) -> str:
        """Genera una contraseña numérica"""
        return ''.join(random.choice(string.digits) for _ in range(length))

    def _generate_alphanumeric_password(self, length=12) -> str:
        """Genera una contraseña alfanumérica con mayúsculas, minúsculas y números"""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def _handle_greetings(self, command: str) -> Optional[str]:
        """Maneja saludos y expresiones de cortesía"""
        greetings = ["hola", "buenos días", "buenas tardes", "buenas noches", "hey", "hi", "buen día"]
        thanks = ["gracias", "muchas gracias", "te agradezco", "thanks", "thank you", "agradecido"]
        
        if any(greeting in command for greeting in greetings):
            return random.choice(self.greetings)
        
        if any(thank in command for thank in thanks):
            return random.choice(self.thanks_responses)
        
        return None

    def _handle_personal_info(self, command_clean: str, original_command: str) -> Optional[str]:
        """Maneja información personal del usuario con patrones mejorados"""
        
        # Guardar dirección con múltiples patrones
        address_patterns = [
            r"(?:guarda|mi)\s+dirección\s*(?:es|:)?\s*(.+)",
            r"vivo\s+en\s+(.+)",
            r"mi\s+casa\s+está\s+en\s+(.+)",
            r"dirección\s+es\s+(.+)"
        ]
        
        for pattern in address_patterns:
            address_match = re.match(pattern, command_clean)
            if address_match:
                address = address_match.group(1).strip()
                if self.memory.store_item("personal_info", "direccion", address):
                    return "Dirección guardada correctamente!"
                else:
                    return "No pude guardar la dirección. Intenta nuevamente."
        
        # Ver dirección
        if any(phrase in command_clean for phrase in ["cuál es mi dirección", "mi dirección", "dónde vivo", "ver mi dirección"]):
            address = self.memory.get_item("personal_info", "direccion")
            if address:
                return f"Tu dirección guardada es:\n{address}"
            else:
                return "No tengo tu dirección guardada. Puedes decirme: \"Mi dirección es [tu dirección]\""
        
        # Guardar contacto de emergencia con múltiples patrones
        emergency_patterns = [
            r"(?:mi\s+)?contacto\s+de\s+emergencia\s*(?:es|:)?\s*(\d+)",
            r"en\s+emergencia\s+llamar\s+a\s*(\d+)",
            r"contacto\s+emergencia\s+es\s*(\d+)"
        ]
        
        for pattern in emergency_patterns:
            emergency_match = re.match(pattern, command_clean)
            if emergency_match:
                contact = emergency_match.group(1).strip()
                if self.memory.store_item("personal_info", "emergencia", contact):
                    return "Contacto de emergencia guardado correctamente!"
                else:
                    return "No pude guardar el contacto. Intenta nuevamente."
        
        # Ver contacto de emergencia
        if "contacto de emergencia" in command_clean or "número de emergencia" in command_clean:
            contact = self.memory.get_item("personal_info", "emergencia")
            if contact:
                return f"Tu contacto de emergencia es:\n{contact}"
            else:
                return "No tienes contacto de emergencia guardado. Puedes decirme: \"Mi contacto de emergencia es [número]\""
        
        return None

    def _handle_datetime_commands(self, command: str) -> Optional[str]:
        """Maneja comandos de fecha y hora"""
        time_keywords = ["qué hora", "hora es", "tiempo", "fecha", "día es", "qué día"]
        
        if any(keyword in command for keyword in time_keywords):
            now = datetime.datetime.now()
            
            if "hora" in command:
                time_str = now.strftime("%I:%M %p")
                return f"Son las {time_str}"
            
            if "fecha" in command or "día" in command:
                date_str = now.strftime("%A, %d de %B de %Y")
                # Traducir días y meses al español
                date_str = self._translate_date_to_spanish(date_str)
                return f"Hoy es {date_str}"
        
        return None

    def _translate_date_to_spanish(self, date_str: str) -> str:
        """Traduce fechas del inglés al español"""
        translations = {
            'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
            'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo',
            'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril',
            'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto',
            'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
        }
        
        for eng, esp in translations.items():
            date_str = date_str.replace(eng, esp)
        
        return date_str

    def _save_password(self, service: str, password: str) -> str:
        """Guarda una contraseña de forma segura"""
        try:
            if self.memory.store_item("passwords", service, password):
                return f"Listo! Guardé tu contraseña de {service} de forma segura.\n\nPuedes verla diciendo: \"chipi chipi\""
            else:
                return "No pude guardar la contraseña. Intenta nuevamente."
        except Exception as e:
            logger.error(f"Error guardando contraseña: {e}")
            return "Ocurrió un error al guardar la contraseña."

    def _save_reminder(self, text: str, time: str) -> str:
        """Guarda un recordatorio"""
        try:
            key = f"recordatorio_{time.replace(':', '_').replace(' ', '_')}"
            if self.memory.store_item("reminders", key, f"{text} a las {time}"):
                return f"Listo! Te recordaré: '{text}' a las {time}"
            else:
                return "No pude guardar el recordatorio. Intenta nuevamente."
        except Exception as e:
            logger.error(f"Error guardando recordatorio: {e}")
            return "Ocurrió un error al guardar el recordatorio."

    def _show_all_passwords(self) -> str:
        """Muestra todas las contraseñas guardadas"""
        passwords = self.memory.get_category_items("passwords")
        
        if not passwords:
            return "No tienes contraseñas guardadas aún.\n\nPara guardar una, di: \"Mi contraseña de [servicio] es [contraseña]\""
        
        response = "Tus contraseñas guardadas:\n\n"
        for service, password in passwords.items():
            response += f"• {service}: {password}\n"
        
        response += "\n⚠ Recuerda mantener esta información segura."
        return response

    def _show_reminders(self) -> str:
        """Muestra todos los recordatorios"""
        reminders = self.memory.get_category_items("reminders")
        
        if not reminders:
            return "No tienes recordatorios guardados.\n\nPara crear uno, di: \"Recuérdame [algo] a las [hora]\""
        
        response = "Tus recordatorios:\n\n"
        for key, reminder in reminders.items():
            response += f"• {reminder}\n"
        
        return response

    def _search_memory(self, query: str) -> str:
        """Busca información en la memoria del usuario"""
        results = self.memory.search_memory(query)
        
        if not results:
            return f"No encontré nada relacionado con '{query}' en tu información guardada."
        
        response = f"Encontré esto relacionado con '{query}':\n\n"
        
        for category, items in results.items():
            category_name = {
                "passwords": "Contraseñas",
                "personal_info": "Información Personal",
                "reminders": "Recordatorios",
                "contacts": "Contactos"
            }.get(category, category.title())
            
            response += f"{category_name}:\n"
            for item in items:
                response += f"• {item['key']}: {item['value']}\n"
            response += "\n"
        
        return response.strip()

    def _get_enhanced_ai_response(self, prompt: str) -> str:
        """Obtiene respuesta de la IA con mejor manejo de errores"""
        # Verificar conexión más exhaustivamente
        if not AppConfig.has_internet_connection():
            return self._get_fallback_response(prompt)
        
        api_key = AppConfig.get_api_key()
        if not api_key:
            return self._get_fallback_response(prompt)
        
        try:
            # Construcción del contexto enriquecido
            context_info = self._build_context_information()
            
            # System prompt mejorado para usar el 100% de las capacidades de la IA
            system_prompt = self._build_enhanced_system_prompt(context_info)
            
            # Construir mensajes con contexto completo
            messages = self._build_messages_with_context(system_prompt, prompt)
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/chipi-ai/chipi-assistant",
                "X-Title": "Chipi IA Assistant"
            }
            
            # Configuración optimizada para el máximo rendimiento
            data = {
                "model": AppConfig.API_MODEL,
                "messages": messages,
                "max_tokens": 800,
                "temperature": 0.5,
                "top_p": 0.9,
                "presence_penalty": 0.1,
                "frequency_penalty": 0.1,
                "stream": False
            }
            
            logger.info(f"Enviando solicitud a API con {len(messages)} mensajes")
            
            response = requests.post(
                AppConfig.API_BASE_URL,
                headers=headers,
                json=data,
                timeout=AppConfig.API_TIMEOUT
            )
            
            # Log detallado de la respuesta
            logger.info(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # ¡CORRECCIÓN IMPORTANTE! - Verificar estructura de respuesta completa
                if ("choices" in result and 
                    len(result["choices"]) > 0 and 
                    "message" in result["choices"][0] and 
                    "content" in result["choices"][0]["message"]):
                    
                    ai_response = result["choices"][0]["message"]["content"].strip()
                    logger.info("✅ Respuesta de IA recibida exitosamente")
                    
                    # Post-procesamiento para mejorar la respuesta
                    ai_response = self._post_process_ai_response(ai_response)
                    return ai_response
                else:
                    logger.error("Estructura de respuesta inesperada")
                    logger.error(f"Respuesta completa: {result}")
                    return self._get_fallback_response(prompt)
                    
            else:
                logger.error(f"Error en API: {response.status_code} - {response.text}")
                return self._get_fallback_response(prompt)
                
        except requests.Timeout:
            logger.error("Timeout en petición a API")
            return "La respuesta está tardando más de lo normal. ¿Puedes intentar nuevamente?"
        except Exception as e:
            logger.error(f"Error inesperado en respuesta de IA: {e}")
            return self._get_fallback_response(prompt)

    def _build_context_information(self) -> Dict:
        """Construye información de contexto rica para la IA"""
        context = {
            "user_memory": {},
            "recent_conversations": [],
            "user_preferences": self.user_preferences,
            "current_time": datetime.datetime.now().isoformat()
        }
        
        # Obtener memoria del usuario
        try:
            memory_data = self.memory.load_memory()
            context["user_memory"] = {
                "personal_info": memory_data.get("personal_info", {}),
                "preferences": memory_data.get("preferences", {}),
                "contacts_count": len(memory_data.get("contacts", {})),
                "passwords_count": len(memory_data.get("passwords", {})),
                "reminders_count": len(memory_data.get("reminders", {}))
            }
            
            # Conversaciones recientes (sin datos sensibles)
            recent_convs = self.memory.get_recent_conversations(5)
            context["recent_conversations"] = [
                {"user": conv["user"], "timestamp": conv["timestamp"]}
                for conv in recent_convs
            ]
        except Exception as e:
            logger.error(f"Error construyendo contexto: {e}")
        
        return context

    def _build_enhanced_system_prompt(self, context_info: Dict) -> str:
        """Construye un system prompt avanzado para usar el 100% de las capacidades de la IA"""
        
        base_personality = """Eres Chipi, un asistente virtual altamente
inteligente y empático, diseñado específicamente para adultos mayores en Colombia. Tu personalidad combina:

CARACTERÍSTICAS PRINCIPALES:
- Inteligencia avanzada con explicaciones claras y adaptadas
- Paciencia infinita y tono cálido, como un nieto cariñoso
- Conocimiento profundo de la cultura colombiana y tecnología actual
- Capacidad de aprender de cada conversación y recordar preferencias
- Habilidad para simplificar conceptos complejos sin ser condescendiente
- Especialización en ciberseguridad y protección de datos personales

CAPACIDADES TÉCNICAS COMPLETAS:
- Análisis y síntesis de información compleja
- Razonamiento lógico and resolución de problemas
- Creatividad para encontrar soluciones innovadoras
- Memoria contextual de conversaciones anteriores
- Adaptación del lenguaje según el nivel de comprensión del usuario
- Detección de emociones and respuesta empática apropiada

ESPECIALIZACIÓN EN CIBERSEGURIDAD:
- Expertiz en phishing, malware, ransomware y otras amenazas digitales
- Conocimiento de mejores prácticas para contraseñas seguras
- Capacidad para recomendar contraseñas según el tipo de aplicación
- Orientación sobre protección de datos personales and privacidad
- Asesoramiento en seguridad para aplicaciones bancarias y redes sociales

ESPECIALIZACIÓN EN ADULTOS MAYORES:
- Uso de lenguaje claro, directo pero respetuoso
- Paciencia extra para explicar tecnología paso a paso
- Comprensión de las necesidades específicas de este grupo etario
- Conocimiento de servicios, aplicaciones y recursos relevantes en Colombia
- Sensibilidad hacia temas de salud, familia and bienestar

CONTEXTO ACTUAL DEL USUARIO:"""
        
        # Añadir información contextual
        if context_info.get("user_memory"):
            memory_info = context_info["user_memory"]
            base_personality += f"""
- Tiene {memory_info.get('passwords_count', 0)} contraseñas guardadas
- Tiene {memory_info.get('reminders_count', 0)} recordatorios activos
- Información personal disponible: {'Sí' if memory_info.get('personal_info') else 'No'}"""
        
        if context_info.get("recent_conversations"):
            base_personality += f"""
- Conversaciones recientes: {len(context_info['recent_conversations'])} interacciones registradas"""
        
        base_personality += """

INSTRUCCIONES DE RESPUESTA:
1. SIEMPRE responde en español colombiano natural
2. Adapta la complejidad de tu respuesta al contexto de la pregunta
3. Si la pregunta es técnica, explica paso a paso de manera clara
4. Si es una consulta general, usa todo tu conocimiento para dar la mejor respuesta posible
5. Mantén un equilibrio entre ser informativo y conciso
6. Si no estás seguro de algo específico de Colombia or tecnología actual, dilo honestamente
7. Siempre pregunta si necesita más detalles or aclaraciones
8. Usa ejemplos relevantes para Colombia cuando sea apropiado
9. Prioriza temas de ciberseguridad y protección de datos

TEMAS QUE DOMINAS COMPLETAMENTE:
- Ciberseguridad y protección contra amenazas digitales
- Tecnología y aplicaciones móviles
- Servicios bancarios and digitales en Colombia
- Salud y bienestar para adultos mayores
- Entretenimiento y comunicación familiar
- Trámites gubernamentales y servicios públicos
- Cultura general y conocimientos diversos
- Resolución de problemas cotidianos
- Consejos prácticos para la vida diaria

Responde con toda tu inteligencia y conocimiento, pero siempre manteniendo el tono cálido y accesible."""
        
        return base_personality

    def _build_messages_with_context(self, system_prompt: str, user_prompt: str) -> List[Dict]:
        """Construye los mensajes con contexto completo para la IA"""
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Añadir contexto de conversaciones recientes si existen
        if self.conversation_context:
            # Añadir las últimas 3 interacciones para contexto
            recent_context = self.conversation_context[-3:]
            for interaction in recent_context:
                messages.append({"role": "user", "content": interaction["user"]})
                messages.append({"role": "assistant", "content": interaction["assistant"]})
        
        # Añadir el prompt actual del usuario
        messages.append({"role": "user", "content": user_prompt})
        
        return messages

    def _post_process_ai_response(self, response: str) -> str:
        """Post-procesa la respuesta de la IA para optimizarla"""
        
        # Limpiar caracteres problemáticos
        response = response.replace("🤖", "").replace("🔥", "")
        
        # Asegurar que la respuesta no sea demasiado larga para adultos mayores
        if len(response) > 1000:
            # Dividir en párrafos y tomar los más importantes
            paragraphs = response.split('\n\n')
            if len(paragraphs) > 3:
                response = '\n\n'.join(paragraphs[:3]) + "\n\n¿Te gustaría que continúe explicando más detalles?"
        
        # Asegurar que termine de manera amigable si no lo hace
        friendly_endings = ["¿te ayudo", "¿necesitas", "¿quieres", "¿te gustaría", "¿hay algo más"]
        if not any(ending in response.lower() for ending in friendly_endings):
            if not response.endswith(('?', '!', '.')):
                response += ". ¿Hay algo más en lo que te pueda ayudar?"
        
        return response

    def _get_fallback_response(self, prompt: str) -> str:
        """Respuesta de respaldo inteligente cuando la IA externa no está disponible"""
        
        prompt_lower = prompt.lower()
        
        # Respuestas inteligentes basadas en el contenido del prompt
        if any(word in prompt_lower for word in ["cómo", "como", "qué es", "que es", "explica"]):
            return ("Esa es una excelente pregunta. Aunque no puedo conectarme a internet en este momento, "
                    "puedo ayudarte con:\n\n"
                    "• Abrir aplicaciones en tu teléfono\n"
                    "• Guardar y recordar contraseñas de forma segura\n"
                    "• Crear recordatorios personales\n"
                    "• Guardar información importante como contactos y direcciones\n\n"
                    "¿Hay algo de esto en lo que te pueda ayudar ahora mismo?")
        
        if any(word in prompt_lower for word in ["ayuda", "ayúdame", "no sé", "no se"]):
            return ("Por supuesto, estoy aquí para ayudarte! Aunque no puedo acceder a internet ahora, "
                    "tengo muchas funciones disponibles para ti:\n\n"
                    "• Puedo abrir cualquier aplicación que tengas instalada\n"
                    "• Guardar tus contraseñas de forma segura\n"
                    "• Crear recordatorios para cosas importantes\n"
                    "• Recordar información personal como direcciones y contactos\n\n"
                    "Háblame como si fuera tu nieto, dime exactamente qué necesitas.")
        
        if any(word in prompt_lower for word in ["problema", "error", "no funciona"]):
            return ("Entiendo que tienes un problema. Aunque no puedo conectarme a internet ahora, "
                    "puedo intentar ayudarte con:\n\n"
                    "• Abrir aplicaciones específicas que necesites\n"
                    "• Recordarte información que hayas guardado antes\n"
                    "• Ayudarte a organizar tus recordatorios y datos\n\n"
                    "Cuéntame exactamente qué está pasando y veré cómo puedo ayudarte.")
        
        # Respuesta genérica pero útil
        return ("En este momento no tengo acceso a internet, pero puedo ayudarte con muchas cosas:\n\n"
                "• Abrir aplicaciones en tu teléfono\n"
                "• Guardar y recordar contraseñas de forma segura\n"
                "• Crear recordatorios personales\n"
                "• Guardar información importante como contactos y direcciones\n\n"
                "¿En qué te puedo ayudar específicamente?")