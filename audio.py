"""
Gestor de audio para funcionalidades de voz - Optimizado para adultos mayores
"""

import os
import time
import threading
from pathlib import Path
from gtts import gTTS
import pygame
from .config import AppConfig
from .utils import Logger

logger = Logger.get_logger(__name__)

class AudioManager:
    """Gestor de audio optimizado para adultos mayores con mejoras de rendimiento y usabilidad"""
    
    def __init__(self):
        self.audio_available = True
        self.min_length_for_audio = 30  # Reducido para más respuestas con audio
        self.currently_playing = False
        self.audio_thread = None
        
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            logger.info("AudioManager inicializado con configuración optimizada")
        except Exception as e:
            self.audio_available = False
            logger.error(f"Error inicializando audio: {e}")
    
    def is_audio_playing(self) -> bool:
        """Verifica si hay audio reproduciéndose"""
        try:
            return pygame.mixer.music.get_busy() or self.currently_playing
        except:
            return False
    
    def speak_text(self, text: str) -> bool:
        """Convierte texto a voz con voz profesional y configuraciones optimizadas"""
        if not self.audio_available or not text.strip():
            return False
            
        # Limpiar texto para mejor pronunciación
        cleaned_text = self._clean_text_for_speech(text)
        
        # Para adultos mayores, permitimos audio en respuestas más cortas
        if len(cleaned_text) < self.min_length_for_audio:
            # Pero solo si es una respuesta significativa, no solo "sí" o "no"
            if len(cleaned_text.split()) > 2:
                pass  # Permitir audio
            else:
                return False
        
        try:
            # Detener audio actual si está reproduciendo
            if self.is_audio_playing():
                self.stop_audio()
                time.sleep(0.3)  # Pequeña pausa antes de empezar nuevo audio
            
            # Crear directorio de audio si no existe
            AppConfig.ensure_directories()
            
            # Generar nombre de archivo único
            filename = f"voice_{int(time.time())}.mp3"
            filepath = AppConfig.AUDIO_DIR / filename
            
            # Configurar voz profesional para adultos mayores
            tts = gTTS(
                text=cleaned_text,
                lang='es',
                tld='com.mx',  # Español mexicano (más claro y neutral)
                slow=False,    # Velocidad normal pero clara
                lang_check=False
            )
            
            tts.save(str(filepath))
            
            # Reproducir en hilo separado para no bloquear la UI
            self.audio_thread = threading.Thread(
                target=self._play_audio, 
                args=(str(filepath),),
                daemon=True
            )
            self.audio_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Error en TTS: {e}")
            return False
    
    def _play_audio(self, filepath: str):
        """Reproduce audio en un hilo separado"""
        try:
            self.currently_playing = True
            
            # Cargar y reproducir
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            
            # Esperar a que termine la reproducción
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # Limpiar archivo temporal
            self._cleanup_audio_file(filepath)
            
        except Exception as e:
            logger.error(f"Error reproduciendo audio: {e}")
        finally:
            self.currently_playing = False
    
    def _cleanup_audio_file(self, filepath: str):
        """Elimina archivo de audio después de reproducirlo"""
        try:
            # Pequeña pausa antes de eliminar
            time.sleep(0.5)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.debug(f"Archivo de audio eliminado: {filepath}")
                
        except Exception as e:
            logger.error(f"Error eliminando archivo de audio: {e}")
    
    def stop_audio(self) -> bool:
        """Detiene la reproducción de audio actual"""
        try:
            if self.is_audio_playing():
                pygame.mixer.music.stop()
                self.currently_playing = False
                return True
            return False
        except Exception as e:
            logger.error(f"Error deteniendo audio: {e}")
            return False
    
    def _clean_text_for_speech(self, text: str) -> str:
        """Limpia el texto para mejor pronunciación en TTS"""
        # Reemplazar caracteres problemáticos
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