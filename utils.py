"""
Utilidades y herramientas de soporte - Optimizadas para seguridad y usabilidad
"""

import logging
import hashlib
import hmac
import os
import secrets
import re
import json
import socket
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from .config import AppConfig

class Logger:
    """Sistema de logging centralizado con rotación y niveles configurables"""
    
    _loggers = {}
    _log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Obtiene o crea un logger con configuración estándar"""
        if name not in cls._loggers:
            cls._loggers[name] = cls._create_logger(name)
        return cls._loggers[name]
    
    @classmethod
    def _create_logger(cls, name: str) -> logging.Logger:
        """Crea un nuevo logger con configuración estándar"""
        AppConfig.ensure_directories()
        
        logger = logging.getLogger(name)
        
        # Evitar duplicar handlers
        if logger.handlers:
            return logger
            
        # Configurar nivel desde variables de entorno o por defecto
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        logger.setLevel(cls._log_levels.get(log_level, logging.INFO))
        
        # Formato consistente
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para archivo con rotación
        log_file = AppConfig.LOGS_DIR / "chipi.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # Handler para consola (solo errores y warnings)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # Logger para errores críticos en archivo separado
        error_handler = logging.FileHandler(
            AppConfig.LOGS_DIR / "errors.log", 
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
        
        return logger
    
    @classmethod
    def set_log_level(cls, level: str):
        """Configura el nivel de logging para todos los loggers"""
        level_upper = level.upper()
        if level_upper in cls._log_levels:
            for logger in cls._loggers.values():
                logger.setLevel(cls._log_levels[level_upper])
    
    @classmethod
    def get_log_file_path(cls) -> Path:
        """Obtiene la ruta del archivo de log principal"""
        return AppConfig.LOGS_DIR / "chipi.log"
      
    @classmethod
    def clear_old_logs(cls, max_age_days: int = 30):
        """Limpia logs antiguos"""
        try:
            for log_file in AppConfig.LOGS_DIR.glob("*.log"):
                if log_file.stat().st_mtime < (datetime.now().timestamp() - max_age_days * 86400):
                    log_file.unlink()
        except Exception as e:
            print(f"Error limpiando logs antiguos: {e}")

class SecurityManager:
    """Gestor de seguridad avanzado para la aplicación"""
    
    # Patrones para validación
    PHONE_PATTERN = re.compile(r'^3\d{9}$')  # Teléfonos colombianos
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    WEAK_PASSWORDS = {'123456', 'password', 'qwerty', '111111', 'admin', 'contraseña'}
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Genera hash seguro de contraseña con salt usando PBKDF2"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Usar PBKDF2 con múltiples iteraciones
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iteraciones para mayor seguridad
        ).hex()
        
        return password_hash, salt
    
    @staticmethod
    def verify_password(password: str, hash_stored: str, salt: str) -> bool:
        """Verifica una contraseña contra su hash"""
        input_hash, _ = SecurityManager.hash_password(password, salt)
        return hmac.compare_digest(input_hash, hash_stored)
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 500) -> str:
        """Sanitiza entrada del usuario removiendo caracteres peligrosos"""
        if not text:
            return ""
        
        # Limitar longitud
        text = text.strip()[:max_length]
        
        # Remover caracteres peligrosos
        dangerous_chars = {'<', '>', '"', "'", '&', '\x00', '\r', '\n', '\\'}
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        # Remover scripts y etiquetas HTML
        text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', text)
        
        return text
     
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Valida número de teléfono colombiano"""
        phone_clean = phone.strip()
        return bool(SecurityManager.PHONE_PATTERN.match(phone_clean))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de email"""
        return bool(SecurityManager.EMAIL_PATTERN.match(email.strip()))
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Valida fortaleza de contraseña con feedback detallado"""
        result = {
            'is_valid': True,
            'issues': [],
            'score': 0
        }
        
        # Verificar longitud mínima
        if len(password) < AppConfig.PASSWORD_MIN_LENGTH:
            result['is_valid'] = False
            result['issues'].append(f"La contraseña debe tener al menos {AppConfig.PASSWORD_MIN_LENGTH} caracteres")
        
        # Verificar contraseñas débiles
        if password.lower() in SecurityManager.WEAK_PASSWORDS:
            result['is_valid'] = False
            result['issues'].append("La contraseña es demasiado común")
        
        # Contar tipos de caracteres
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        # Calcular score de fortaleza
        score = 0
        if len(password) >= 8: score += 1
        if len(password) >= 12: score += 1
        if has_upper: score += 1
        if has_lower: score += 1
        if has_digit: score += 1
        if has_special: score += 2
        
        result['score'] = score
        
        # Recomendaciones basadas en score
        if score < 3:
            result['is_valid'] = False
            result['issues'].append("Contraseña muy débil")
        elif score < 5:
            result['issues'].append("Considera usar mayúsculas, números y símbolos")
        
        return result
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Genera un token seguro para sesiones"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def encrypt_data(data: str, key: Optional[bytes] = None) -> Tuple[str, bytes]:
        """Encripta datos sensibles"""
        if key is None:
            key = Fernet.generate_key()
        
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data.encode())
        return encrypted.decode(), key
    
    @staticmethod
    def decrypt_data(encrypted_data: str, key: bytes) -> str:
        """Desencripta datos"""
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()
    
    @staticmethod
    def check_password_leak(password: str) -> bool:
        """
        Verifica si la contraseña ha sido comprometida en brechas
        (Implementación simplificada - en producción usar API como HaveIBeenPwned)
        """
        # Esta es una implementación básica. En producción, usar:
        # https://haveibeenpwned.com/API/v3#PwnedPasswords
        common_leaks = {
            '123456', 'password', '123456789', '12345678', '12345',
            '111111', '1234567', 'sunshine', 'qwerty', 'iloveyou'
        }
        return password in common_leaks

class NetworkUtils:
    """Utilidades de red y conectividad"""
    
    @staticmethod
    def check_internet_connection(timeout: int = 5) -> bool:
        """Verifica conexión a internet de forma confiable"""
        try:
            # Intentar con DNS de Google
            socket.create_connection(("8.8.8.8", 53), timeout=timeout)
            return True
        except OSError:
            pass
        
        try:
            # Intentar con HTTP request
            requests.get("https://www.google.com", timeout=timeout)
            return True
        except:
            return False
    
    @staticmethod
    def get_network_status() -> Dict[str, Any]:
        """Obtiene estado detallado de la red"""
        return {
            'internet_connected': NetworkUtils.check_internet_connection(),
            'timestamp': datetime.now().isoformat(),
            'wifi_connected': NetworkUtils._check_wifi_connection(),
            'network_type': NetworkUtils._get_network_type()
        }
    
    @staticmethod
    def _check_wifi_connection() -> bool:
        """Verifica si está conectado a WiFi"""
        try:
            # Implementación básica - en Android se necesitarían permisos adicionales
            import socket
            return socket.gethostbyname(socket.gethostname()) != "127.0.0.1"
        except:
            return False
    
    @staticmethod
    def _get_network_type() -> str:
        """Intenta determinar el tipo de red"""
        try:
            # Esta es una implementación simplificada
            return "WiFi" if NetworkUtils._check_wifi_connection() else "Móvil"
        except:
            return "Desconocido"
    
    @staticmethod
    def make_secure_request(url: str, method: str = "GET", **kwargs) -> requests.Response:
        """Realiza una petición HTTP segura con timeout y verificación SSL"""
        timeout = kwargs.pop('timeout', 30)
        verify = kwargs.pop('verify', True)
        
        try:
            response = requests.request(
                method=method,
                url=url,
                timeout=timeout,
                verify=verify,
                **kwargs
            )
            return response
        except requests.Timeout:
            raise Exception("La solicitud tardó demasiado tiempo")
        except requests.RequestException as e:
            raise Exception(f"Error de conexión: {e}")

class TextUtils:
    """Utilidades para formato y presentación de texto"""
    
    @staticmethod
    def format_message(text: str) -> str:
        """Convierte textos con \n en saltos de línea reales y limpia formato"""
        if not text:
            return ""
        
        # Reemplazar \\n por saltos de línea reales
        text = text.replace('\\n', '\n')
        
        # Limpiar caracteres de escape
        text = text.replace('\\"', '"').replace("\\'", "'")
        
        # Asegurar que los puntos sigan con espacio
        text = re.sub(r'\.([a-zA-Z])', r'. \1', text)
        
        return text.strip()
    
    @staticmethod
    def wrap_text(text: str, max_line_length: int = 50) -> str:
        """Ajusta texto para que no sea demasiado ancho"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            if len(' '.join(current_line + [word])) <= max_line_length:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)


class FileUtils:
    """Utilidades para manejo seguro de archivos"""
    
    @staticmethod
    def safe_json_write(filepath: Path, data: Any) -> bool:
        """Escribe datos JSON de forma segura (evita corrupción)"""
        try:
            # Escribir a archivo temporal primero
            temp_file = filepath.with_suffix('.tmp')
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Reemplazar archivo original
            temp_file.replace(filepath)
            
            # Establecer permisos seguros
            filepath.chmod(0o600)
            
            return True
        except Exception as e:
            print(f"Error escribiendo archivo JSON: {e}")
            # Intentar limpiar archivo temporal
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except:
                pass
            return False
    
    @staticmethod
    def safe_json_read(filepath: Path, default: Any = None) -> Any:
        """Lee datos JSON de forma segura con manejo de errores"""
        try:
            if not filepath.exists():
                return default
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Intentar recuperar datos corruptos
            return FileUtils._recover_corrupted_json(filepath, default)
        except Exception as e:
            print(f"Error leyendo archivo JSON: {e}")
            return default
    
    @staticmethod
    def _recover_corrupted_json(filepath: Path, default: Any) -> Any:
        """Intenta recuperar datos de un archivo JSON corrupto"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Buscar el último objeto JSON válido
            brace_count = 0
            last_valid_pos = 0
            
            for i, char in enumerate(content):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        last_valid_pos = i + 1
            
            if last_valid_pos > 0:
                valid_content = content[:last_valid_pos]
                return json.loads(valid_content)
            
            return default
        except:
            return default
    
    @staticmethod
    def get_file_size(filepath: Path) -> int:
        """Obtiene el tamaño de un archivo en bytes"""
        try:
            return filepath.stat().st_size
        except:
            return 0
    
    @staticmethod
    def cleanup_old_files(directory: Path, pattern: str, max_age_days: int = 30) -> int:
        """Limpia archivos antiguos que coincidan con el patrón"""
        cleaned_count = 0
        cutoff_time = datetime.now().timestamp() - (max_age_days * 86400)
        
        try:
            for file_path in directory.glob(pattern):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1
        except Exception as e:
            print(f"Error limpiando archivos antiguos: {e}")
        
        return cleaned_count

class ValidationUtils:
    """Utilidades de validación de datos"""
    
    @staticmethod
    def validate_colombian_phone(phone: str) -> Tuple[bool, str]:
        """Valida número de teléfono colombiano con mensaje de error"""
        phone_clean = phone.strip()
        
        if not phone_clean:
            return False, "Por favor ingresa un número de teléfono"
        
        if not phone_clean.isdigit():
            return False, "El número solo debe contener dígitos"
        
        if len(phone_clean) != 10:
            return False, "El número debe tener exactamente 10 dígitos"
        
        if not phone_clean.startswith('3'):
            return False, "Debe ser un número de celular colombiano (comenzar con 3)"
        
        return True, "Número válido"
    
    @staticmethod
    def validate_passwords_match(password: str, confirm_password: str) -> Tuple[bool, str]:
        """Valida que las contraseñas coincidan"""
        if password != confirm_password:
            return False, "Las contraseñas no coinciden"
        return True, "Contraseñas coinciden"
    
    @staticmethod
    def validate_age_related_input(input_text: str, max_length: int = 100) -> Tuple[bool, str]:
        """Validación especial para entradas de adultos mayores"""
        if not input_text.strip():
            return False, "Por favor completa este campo"
        
        if len(input_text) > max_length:
            return False, f"El texto es demasiado largo (máximo {max_length} caracteres)"
        
        # Verificar caracteres extraños que podrían ser errores de tipeo
        strange_chars = {'@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '=', '{', '}', '[', ']', '|', '\\', ':', ';', '"', "'", '<', '>', '?', '/', '~', '`'}
        found_chars = [char for char in input_text if char in strange_chars]
        
        if found_chars:
            return False, f"Caracteres no permitidos: {', '.join(found_chars[:3])}"
        
        return True, "Entrada válida"

class AccessibilityUtils:
    """Utilidades de accesibilidad para adultos mayores"""
    
    @staticmethod
    def get_accessible_font_size(preference: str = 'medium') -> str:
        """Obtiene tamaño de fuente accesible según preferencia"""
        sizes = {
            'small': '16sp',
            'medium': '20sp',
            'large': '24sp',
            'xlarge': '28sp',
            'xxlarge': '32sp'
        }
        return sizes.get(preference.lower(), '20sp')
    
    @staticmethod
    def get_contrast_color(background_color: tuple) -> tuple:
        """Calcula color de contraste óptimo para un fondo dado"""
        # Fórmula de luminosidad relativa (WCAG)
        r, g, b, a = background_color
        luminance = (0.299 * r + 0.587 * g + 0.114 * b)
        
        return (0, 0, 0, 1) if luminance > 0.5 else (1, 1, 1, 1)
    
    @staticmethod
    def is_high_contrast_mode() -> bool:
        """Verifica si debería usarse modo alto contraste"""
        # En una implementación real, esto podría leer preferencias del sistema
        return False
    
    @staticmethod
    def get_voice_speed(preference: str = 'normal') -> float:
        """Obtiene velocidad de voz según preferencia"""
        speeds = {
            'slow': 0.8,
            'normal': 1.0,
            'fast': 1.2
        }
        return speeds.get(preference.lower(), 1.0)

# Inicialización de utilities
def initialize_utilities():
    """Inicializa todas las utilities al importar el módulo"""
    AppConfig.ensure_directories()
    Logger.clear_old_logs(30)
    logger = Logger.get_logger(__name__)
    logger.info("Utilities inicializadas correctamente")

# Inicializar al importar
initialize_utilities()