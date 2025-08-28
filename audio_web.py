"""
Gestor de audio para funcionalidades de voz - Versión Web
Sistema de texto a voz usando Web Speech API en el frontend
"""

import logging
from app.config import AppConfig
from app.utils import Logger

logger = Logger.get_logger(__name__)

class AudioManagerWeb:
    """Gestor de audio para versión web usando APIs del navegador"""

    def __init__(self):
        self.audio_available = True  # Siempre disponible en web
        self.min_length_for_audio = 30
        logger.info("AudioManagerWeb inicializado para versión web")

    def is_audio_playing(self) -> bool:
        """En web, el audio se controla desde el frontend"""
        return False

    def speak_text(self, text: str) -> bool:
        """En versión web, el audio se maneja desde JavaScript"""
        # Esta función solo existe para compatibilidad
        # El audio real se maneja en el frontend con Web Speech API
        return True

    def stop_audio(self) -> bool:
        """Detiene la reproducción de audio"""
        # En web, se maneja desde el frontend
        return True

    def _clean_text_for_speech(self, text: str) -> str:
        """Limpia el texto para mejor pronunciación"""
        replacements = {
            '•': '-',
            '→': 'entonces',
            '⚠': 'precaución',
            '🔒': 'candado',
            '📱': 'teléfono',
            '💰': 'dinero',
            '👤': 'persona'
        }

        for char, replacement in replacements.items():
            text = text.replace(char, replacement)

        # Limpiar múltiples espacios y saltos de línea excesivos
        text = ' '.join(text.split())
        text = text.replace('\n\n', '. ').replace('\n', '. ')
        return text

    def set_audio_preference(self, enabled: bool):
        """Configura si el audio está habilitado o no"""
        self.audio_available = enabled
        logger.info(f"Preferencia de audio configurada: {'activado' if enabled else 'desactivado'}")
