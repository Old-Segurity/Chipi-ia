"""
Configuración centralizada de la aplicación - Optimizada para adultos mayores
"""

import os
import socket
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class AppConfig:
    """Configuración general de la aplicación con mejoras de seguridad y usabilidad"""

    # Información de la aplicación
    APP_NAME = "Chipi IA"
    APP_VERSION = "2.1.0"
    APP_DESCRIPTION = "Asistente Virtual para Adultos Mayores"

    # Directorios (usando pathlib para mejor compatibilidad entre sistemas)
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    ASSETS_DIR = BASE_DIR / "assets"
    LOGS_DIR = BASE_DIR / "logs"
    AUDIO_DIR = BASE_DIR / "audio"
    BACKUP_DIR = BASE_DIR / "backups"

    # Archivos de datos
    USERS_DB = DATA_DIR / "users.json"

    # Configuración de seguridad mejorada
    PASSWORD_MIN_LENGTH = 6
    SESSION_TIMEOUT = 3600  # 1 hora
    MAX_LOGIN_ATTEMPTS = 5
    PASSWORD_HASH_ITERATIONS = 100000

    # API Configuration con valores de respaldo
    API_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    # En config.py - Modelos gratuitos con límites generosos
    API_MODEL = "google/gemini-flash-1.5"  # 100+ solicitudes gratis/día
# API_MODEL = "meta-llama/llama-3.1-8b-instruct"  # Muy generoso free tier
# API_MODEL = "microsoft/wizardlm-2-8x22b"  # Buen free tier
    API_TIMEOUT = 10
    API_MAX_TOKENS = 250
    API_TEMPERATURE = 0.3

    # Configuración de audio
    AUDIO_ENABLED = True
    AUDIO_MIN_LENGTH = 30

    # Backup configuration
    BACKUP_ENABLED = True
    BACKUP_INTERVAL = 86400  # 24 horas en segundos

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """Obtiene la clave API de forma segura - VERSIÓN SIMPLIFICADA"""
        # Múltiples fuentes posibles para la API key
        possible_keys = [
            os.getenv('CHIPI_API_KEY'),
            os.getenv('OPENROUTER_API_KEY'),
            os.getenv('AI_API_KEY'),
            os.getenv('API_KEY')
        ]
        
        for api_key in possible_keys:
            if api_key and api_key.strip():
                # ¡VERIFICACIÓN MUY FLEXIBLE! - Cualquier key no vacía es válida
                key_clean = api_key.strip()
                print(f"✅ API KEY ENCONTRADA: {key_clean[:15]}... (longitud: {len(key_clean)})")
                return key_clean
        
        print("❌ No se encontró ninguna API key")
        return None

    @classmethod
    def test_api_connection(cls):
        """Prueba la conexión con la API de OpenRouter"""
        api_key = cls.get_api_key()
        if not api_key:
            return "❌ No se encontró API key"

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/chipi-ai/chipi-assistant",
                "X-Title": "Chipi IA Assistant"
            }

            test_data = {
                "model": cls.API_MODEL,
                "messages": [{"role": "user", "content": "Hola"}],
                "max_tokens": 5,
                "temperature": 0.1
            }

            response = requests.post(
                cls.API_BASE_URL,
                headers=headers,
                json=test_data,
                timeout=15
            )

            if response.status_code == 200:
                return "✅ Conexión con API exitosa"
            else:
                return f"❌ Error en API: {response.status_code} - {response.text[:100]}..."

        except Exception as e:
            return f"❌ Error de conexión: {e}"

    @classmethod
    def ensure_directories(cls):
        """Crea los directorios necesarios si no existen"""
        directories = [cls.DATA_DIR, cls.ASSETS_DIR, cls.LOGS_DIR, cls.AUDIO_DIR, cls.BACKUP_DIR]
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"Error creando directorio {directory}: {e}")

    @classmethod
    def has_internet_connection(cls, timeout: int = 10) -> bool:
        """Verifica conexión a internet"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=timeout)
            return True
        except:
            return False

    @classmethod
    def load_environment_variables(cls):
        """Carga variables de entorno"""
        env_path = cls.BASE_DIR / ".env"
        if env_path.exists():
            try:
                load_dotenv(env_path)
                print(f"✅ Variables de entorno cargadas desde: {env_path}")
                return True
            except Exception as e:
                print(f"❌ Error cargando .env: {e}")
        print("⚠️ No se encontró archivo .env")
        return False

    @classmethod
    def get_database_path(cls) -> Path:
        """Obtiene la ruta de la base de datos"""
        cls.ensure_directories()
        return cls.USERS_DB

    @classmethod
    def get_app_info(cls) -> Dict[str, Any]:
        """Retorna información de la aplicación"""
        return {
            "name": cls.APP_NAME,
            "version": cls.APP_VERSION,
            "description": cls.APP_DESCRIPTION,
            "has_internet": cls.has_internet_connection(),
            "api_connected": cls.get_api_key() is not None
        }

class UIConfig:
    """Configuración de la interfaz de usuario"""

    # Colores principales
    PRIMARY_COLOR = (0.97, 0.85, 0.17, 1)
    SECONDARY_COLOR = (0.12, 0.13, 0.20, 1)
    BACKGROUND_COLOR = (0.08, 0.12, 0.18, 1)

    # Colores para chat
    USER_BUBBLE_COLOR = (0.2, 0.6, 0.9, 1)
    USER_TEXT_COLOR = (1, 1, 1, 1)
    BOT_BUBBLE_COLOR = (0.95, 0.95, 0.95, 1)
    BOT_TEXT_COLOR = (0.1, 0.1, 0.1, 1)

    # Colores de estado
    SUCCESS_COLOR = (0.2, 0.7, 0.2, 1)
    ERROR_COLOR = (0.9, 0.2, 0.2, 1)
    WARNING_COLOR = (0.97, 0.75, 0.17, 1)
    INFO_COLOR = (0.2, 0.6, 0.8, 1)

    # Tamaños de fuente
    FONT_SIZE_XXL = '28sp'
    FONT_SIZE_XL = '24sp'
    FONT_SIZE_LARGE = '20sp'
    FONT_SIZE_MEDIUM = '18sp'
    FONT_SIZE_NORMAL = '16sp'
    FONT_SIZE_SMALL = '14sp'

    # Espaciado
    PADDING_XXL = 25
    PADDING_XL = 20
    PADDING_LARGE = 16
    PADDING_MEDIUM = 12
    PADDING_SMALL = 8

    # Alturas de elementos
    BUTTON_HEIGHT = 60
    INPUT_HEIGHT = 55
    HEADER_HEIGHT = 85

    @classmethod
    def get_color_scheme(cls) -> Dict[str, tuple]:
        """Retorna el esquema de colores"""
        return {
            "primary": cls.PRIMARY_COLOR,
            "secondary": cls.SECONDARY_COLOR,
            "background": cls.BACKGROUND_COLOR,
            "user_bubble": cls.USER_BUBBLE_COLOR,
            "user_text": cls.USER_TEXT_COLOR,
            "bot_bubble": cls.BOT_BUBBLE_COLOR,
            "bot_text": cls.BOT_TEXT_COLOR,
            "success": cls.SUCCESS_COLOR,
            "error": cls.ERROR_COLOR,
            "warning": cls.WARNING_COLOR,
            "info": cls.INFO_COLOR
        }

# Inicialización automática
AppConfig.ensure_directories()
AppConfig.load_environment_variables()

# Logger
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)