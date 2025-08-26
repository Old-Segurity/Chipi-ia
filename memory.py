"""
Sistema de memoria personalizada para cada usuario - Optimizado para seguridad y usabilidad
"""

import json
import re
import hashlib
from typing import Dict, Optional, List, Any
from pathlib import Path
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from .config import AppConfig
from .utils import Logger

logger = Logger.get_logger(__name__)

class MemoryManager:
    """Gestor de memoria personalizada mejorado con encriptación y categorías organizadas"""
    
    def __init__(self, phone: str):
        self.phone = phone
        self.memory_file = AppConfig.DATA_DIR / f"memoria_{self._hash_phone(phone)}.json"
        self.encryption_key = self._get_encryption_key()
        self.fernet = Fernet(self.encryption_key) if self.encryption_key else None
        
        AppConfig.ensure_directories()
        self._ensure_memory_structure()
    
    def _hash_phone(self, phone: str) -> str:
        """Hash seguro del número de teléfono para nombres de archivo"""
        return hashlib.sha256(phone.encode()).hexdigest()[:16]
    
    def _get_encryption_key(self) -> Optional[bytes]:
        """Obtiene o genera clave de encriptación segura"""
        try:
            key_file = AppConfig.DATA_DIR / "memory_key.key"
            
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                # Generar nueva clave
                new_key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(new_key)
                # Establecer permisos seguros
                key_file.chmod(0o600)
                return new_key
                
        except Exception as e:
            logger.error(f"Error obteniendo clave de encriptación: {e}")
            return None
    
    def _encrypt_data(self, data: str) -> str:
        """Encripta datos sensibles"""
        if not self.fernet or not data:
            return data
        try:
            return self.fernet.encrypt(data.encode()).decode()
        except Exception as e:
            logger.error(f"Error encriptando datos: {e}")
            return data
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Desencripta datos"""
        if not self.fernet or not encrypted_data:
            return encrypted_data
        try:
            return self.fernet.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            logger.error(f"Error desencriptando datos: {e}")
            return encrypted_data
    
    def _ensure_memory_structure(self):
        """Asegura que existe la estructura básica de memoria con categorías organizadas"""
        if not self.memory_file.exists():
            default_memory = {
                "metadata": {
                    "version": "2.1.0",
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "owner": self.phone,
                    "encryption_enabled": self.fernet is not None
                },
                "categories": {
                    "personal_info": {
                        "description": "Información personal del usuario",
                        "items": {},
                        "encrypted": True
                    },
                    "passwords": {
                        "description": "Contraseñas seguras",
                        "items": {},
                        "encrypted": True
                    },
                    "reminders": {
                        "description": "Recordatorios importantes",
                        "items": {},
                        "encrypted": False
                    },
                    "contacts": {
                        "description": "Contactos de emergencia y familiares",
                        "items": {},
                        "encrypted": True
                    },
                    "medical_info": {
                        "description": "Información médica importante",
                        "items": {},
                        "encrypted": True
                    },
                    "preferences": {
                        "description": "Preferencias de la aplicación",
                        "items": {},
                        "encrypted": False
                    },
                    "favorites": {
                        "description": "Aplicaciones y servicios favoritos",
                        "items": {},
                        "encrypted": False
                    }
                },
                "conversation_history": []
            }
            self._save_memory(default_memory)
    
    def load_memory(self) -> Dict:
        """Carga la memoria completa del usuario con verificación de integridad"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    memory = json.load(f)
                
                # Verificar integridad básica
                if not self._validate_memory_structure(memory):
                    logger.warning("Estructura de memoria inválida, reparando...")
                    memory = self._repair_memory_structure(memory)
                
                # Desencriptar datos si es necesario
                memory = self._decrypt_memory_data(memory)
                
                return memory
            
            # Si el archivo no existe, crear estructura nueva
            self._ensure_memory_structure()
            return self.load_memory()
            
        except Exception as e:
            logger.error(f"Error cargando memoria para {self.phone}: {e}")
            return self._create_empty_memory()
    
    def _save_memory(self, memory: Dict) -> bool:
        """Guarda la memoria completa del usuario con encriptación"""
        try:
            # Actualizar metadatos
            memory["metadata"]["last_updated"] = datetime.now().isoformat()
            memory["metadata"]["encryption_enabled"] = self.fernet is not None
            
            # Encriptar datos sensibles antes de guardar
            memory_to_save = self._encrypt_memory_data(memory.copy())
            
            # Guardar con write-and-replace para evitar corrupción
            temp_file = self.memory_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(memory_to_save, f, ensure_ascii=False, indent=2)
            
            # Reemplazar archivo original
            temp_file.replace(self.memory_file)
            
            # Establecer permisos seguros
            self.memory_file.chmod(0o600)
            
            logger.debug(f"Memoria guardada para {self.phone}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando memoria para {self.phone}: {e}")
            return False
    
    def _encrypt_memory_data(self, memory: Dict) -> Dict:
        """Encripta datos sensibles en la memoria"""
        if not self.fernet:
            return memory
        
        for category_name, category_data in memory.get("categories", {}).items():
            if category_data.get("encrypted", False):
                for key, item_data in category_data.get("items", {}).items():
                    if "value" in item_data:
                        item_data["value"] = self._encrypt_data(item_data["value"])
        
        return memory
    
    def _decrypt_memory_data(self, memory: Dict) -> Dict:
        """Desencripta datos sensibles en la memoria"""
        if not self.fernet:
            return memory
        
        for category_name, category_data in memory.get("categories", {}).items():
            if category_data.get("encrypted", False):
                for key, item_data in category_data.get("items", {}).items():
                    if "value" in item_data:
                        item_data["value"] = self._decrypt_data(item_data["value"])
        
        return memory
    
    def _validate_memory_structure(self, memory: Dict) -> bool:
        """Valida la estructura básica de la memoria"""
        return (
            "metadata" in memory and
            "categories" in memory and
            "conversation_history" in memory and
            isinstance(memory["categories"], dict)
        )
    
    def _repair_memory_structure(self, memory: Dict) -> Dict:
        """Repara la estructura de memoria si está corrupta"""
        default_memory = self._create_empty_memory()
        
        # Preservar datos existentes si es posible
        if "categories" in memory and isinstance(memory["categories"], dict):
            for category_name, category_data in memory["categories"].items():
                if category_name in default_memory["categories"]:
                    if isinstance(category_data, dict) and "items" in category_data:
                        default_memory["categories"][category_name]["items"] = category_data["items"]
        
        if "conversation_history" in memory and isinstance(memory["conversation_history"], list):
            default_memory["conversation_history"] = memory["conversation_history"]
        
        return default_memory
    
    def _create_empty_memory(self) -> Dict:
        """Crea una estructura de memoria vacía"""
        return {
            "metadata": {
                "version": "2.1.0",
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "owner": self.phone,
                "encryption_enabled": self.fernet is not None
            },
            "categories": {
                cat: {"items": {}, "encrypted": enc}
                for cat, enc in [
                    ("personal_info", True),
                    ("passwords", True),
                    ("reminders", False),
                    ("contacts", True),
                    ("medical_info", True),
                    ("preferences", False),
                    ("favorites", False)
                ]
            },
            "conversation_history": []
        }
    
    def store_item(self, category: str, key: str, value: str, description: str = "") -> bool:
        """Almacena un elemento en una categoría específica con descripción opcional"""
        try:
            memory = self.load_memory()
            
            if category not in memory["categories"]:
                # Crear categoría nueva si no existe
                memory["categories"][category] = {
                    "items": {},
                    "encrypted": True,  # Por defecto encriptar categorías nuevas
                    "description": description or f"Categoría {category}"
                }
            
            memory["categories"][category]["items"][key] = {
                "value": value,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "description": description
            }
            
            return self._save_memory(memory)
            
        except Exception as e:
            logger.error(f"Error almacenando item en {category}: {e}")
            return False
    
    def get_item(self, category: str, key: str) -> Optional[str]:
        """Obtiene un elemento de una categoría específica"""
        try:
            memory = self.load_memory()
            
            if (category in memory["categories"] and 
                key in memory["categories"][category]["items"]):
                return memory["categories"][category]["items"][key]["value"]
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo item de {category}: {e}")
            return None
    
    def get_item_details(self, category: str, key: str) -> Optional[Dict]:
        """Obtiene detalles completos de un elemento"""
        try:
            memory = self.load_memory()
            
            if (category in memory["categories"] and 
                key in memory["categories"][category]["items"]):
                return memory["categories"][category]["items"][key]
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo detalles de item: {e}")
            return None
    
    def get_category_items(self, category: str) -> Dict[str, str]:
        """Obtiene todos los elementos de una categoría"""
        try:
            memory = self.load_memory()
            
            if category in memory["categories"]:
                return {
                    k: v["value"] 
                    for k, v in memory["categories"][category]["items"].items()
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error obteniendo items de {category}: {e}")
            return {}
    
    def get_category_with_details(self, category: str) -> Dict[str, Dict]:
        """Obtiene todos los elementos de una categoría con sus detalles"""
        try:
            memory = self.load_memory()
            
            if category in memory["categories"]:
                return memory["categories"][category]["items"].copy()
            
            return {}
            
        except Exception as e:
            logger.error(f"Error obteniendo categoría con detalles: {e}")
            return {}
    
    def remove_item(self, category: str, key: str) -> bool:
        """Elimina un elemento de una categoría"""
        try:
            memory = self.load_memory()
            
            if (category in memory["categories"] and 
                key in memory["categories"][category]["items"]):
                del memory["categories"][category]["items"][key]
                return self._save_memory(memory)
            
            return False
            
        except Exception as e:
            logger.error(f"Error eliminando item de {category}: {e}")
            return False
    
    def add_conversation_entry(self, user_message: str, bot_response: str):
        """Añade una entrada al historial de conversación con limpieza automática"""
        try:
            memory = self.load_memory()
            
            entry = {
                "timestamp": datetime.now().isoformat(),
                "user": user_message,
                "bot": bot_response,
                "length": len(user_message) + len(bot_response)
            }
            
            memory["conversation_history"].append(entry)
            
            # Limpieza automática: mantener conversación bajo 50KB
            total_size = sum(entry.get("length", 0) for entry in memory["conversation_history"])
            while total_size > 50000 and memory["conversation_history"]:
                removed = memory["conversation_history"].pop(0)
                total_size -= removed.get("length", 0)
            
            # También limitar por cantidad (máximo 100 conversaciones)
            if len(memory["conversation_history"]) > 100:
                memory["conversation_history"] = memory["conversation_history"][-100:]
            
            self._save_memory(memory)
            
        except Exception as e:
            logger.error(f"Error añadiendo entrada de conversación: {e}")
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Obtiene las conversaciones recientes con información de contexto"""
        try:
            memory = self.load_memory()
            history = memory.get("conversation_history", [])
            
            # Invertir para obtener las más recientes primero
            recent = list(reversed(history))[:limit]
            
            # Añadir contexto útil para cada conversación
            for conv in recent:
                conv["time_ago"] = self._get_time_ago(conv["timestamp"])
                
            return recent
            
        except Exception as e:
            logger.error(f"Error obteniendo conversaciones recientes: {e}")
            return []
    
    def _get_time_ago(self, timestamp: str) -> str:
        """Convierte timestamp a formato 'hace x tiempo'"""
        try:
            past_time = datetime.fromisoformat(timestamp)
            now = datetime.now()
            diff = now - past_time
            
            if diff.days > 0:
                return f"hace {diff.days} días"
            elif diff.seconds >= 3600:
                hours = diff.seconds // 3600
                return f"hace {hours} horas"
            elif diff.seconds >= 60:
                minutes = diff.seconds // 60
                return f"hace {minutes} minutos"
            else:
                return "hace unos momentos"
                
        except:
            return "reciente"
    
    def search_memory(self, query: str, category: str = None) -> Dict[str, List]:
        """Busca en toda la memoria del usuario con búsqueda inteligente"""
        results = {}
        query_lower = query.lower().strip()
        
        try:
            memory = self.load_memory()
            
            # Determinar categorías a buscar
            categories_to_search = [category] if category else memory["categories"].keys()
            
            for cat in categories_to_search:
                if cat not in memory["categories"]:
                    continue
                    
                matches = []
                for key, item_data in memory["categories"][cat]["items"].items():
                    value = item_data.get("value", "")
                    desc = item_data.get("description", "")
                    
                    # Búsqueda en key, value y description
                    if (query_lower in key.lower() or 
                        query_lower in value.lower() or 
                        query_lower in desc.lower()):
                        
                        matches.append({
                            "key": key,
                            "value": value,
                            "description": desc,
                            "created_at": item_data.get("created_at"),
                            "last_updated": item_data.get("last_updated")
                        })
                
                if matches:
                    results[cat] = matches
            
            # También buscar en el historial de conversaciones
            if not category or category == "conversation_history":
                conv_matches = []
                for conv in memory.get("conversation_history", []):
                    if (query_lower in conv.get("user", "").lower() or 
                        query_lower in conv.get("bot", "").lower()):
                        
                        conv_matches.append(conv)
                
                if conv_matches:
                    results["conversation_history"] = conv_matches
            
            return results
            
        except Exception as e:
            logger.error(f"Error buscando en memoria: {e}")
            return {}
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la memoria del usuario"""
        try:
            memory = self.load_memory()
            stats = {
                "total_categories": len(memory["categories"]),
                "total_items": 0,
                "categories": {},
                "conversation_count": len(memory.get("conversation_history", [])),
                "last_updated": memory["metadata"]["last_updated"],
                "encryption_enabled": memory["metadata"]["encryption_enabled"]
            }
            
            for cat_name, cat_data in memory["categories"].items():
                item_count = len(cat_data.get("items", {}))
                stats["total_items"] += item_count
                stats["categories"][cat_name] = {
                    "item_count": item_count,
                    "encrypted": cat_data.get("encrypted", False)
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de memoria: {e}")
            return {}
    
    def export_memory(self, include_sensitive: bool = False) -> Dict:
        """Exporta la memoria para backup o transferencia"""
        try:
            memory = self.load_memory()
            export_data = {
                "metadata": memory["metadata"].copy(),
                "categories": {},
                "exported_at": datetime.now().isoformat(),
                "include_sensitive": include_sensitive
            }
            
            for cat_name, cat_data in memory["categories"].items():
                export_data["categories"][cat_name] = {
                    "item_count": len(cat_data.get("items", {})),
                    "encrypted": cat_data.get("encrypted", False)
                }
                
                if include_sensitive or not cat_data.get("encrypted", False):
                    export_data["categories"][cat_name]["items"] = cat_data.get("items", {}).copy()
                else:
                    # Para datos sensibles no incluidos, solo mostrar conteo
                    export_data["categories"][cat_name]["items"] = {
                        "count": len(cat_data.get("items", {})),
                        "sensitive": True
                    }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exportando memoria: {e}")
            return {}
    
    def cleanup_old_items(self, max_age_days: int = 365) -> int:
        """Limpia items antiguos y retorna el número de elementos eliminados"""
        try:
            memory = self.load_memory()
            removed_count = 0
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            for cat_name, cat_data in memory["categories"].items():
                items_to_remove = []
                
                for key, item_data in cat_data.get("items", {}).items():
                    created_at = item_data.get("created_at")
                    if created_at:
                        try:
                            item_date = datetime.fromisoformat(created_at)
                            if item_date < cutoff_date:
                                items_to_remove.append(key)
                        except:
                            pass
                
                for key in items_to_remove:
                    del cat_data["items"][key]
                    removed_count += 1
            
            if removed_count > 0:
                self._save_memory(memory)
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Error limpiando items antiguos: {e}")
            return 0