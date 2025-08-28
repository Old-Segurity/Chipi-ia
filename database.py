"""
Gestor de base de datos y usuarios - Optimizado para seguridad y usabilidad
"""

import json
import hashlib
import hmac
import os
import secrets
import re
from typing import Dict, Optional, List
from pathlib import Path
from datetime import datetime, timedelta
from app.config import AppConfig
from app.utils import Logger

logger = Logger.get_logger(__name__)

class DatabaseManager:
    """Gestor de base de datos para usuarios con seguridad mejorada"""

    def __init__(self):
        AppConfig.ensure_directories()
        self.users_file = AppConfig.USERS_DB
        self.backup_manager = BackupManager()

    @classmethod
    def initialize(cls):
        """Inicializa la base de datos con verificación de integridad"""
        instance = cls()
        if not instance.users_file.exists():
            instance._create_empty_db()
            logger.info("Base de datos inicializada")
        else:
            # Verificar integridad de la base de datos existente
            if not instance._verify_database_integrity():
                logger.warning("Problemas de integridad detectados en la base de datos")
                instance._repair_database()

            # Crear backup inicial
            instance.backup_manager.create_backup()
            logger.info("Base de datos verificada y lista para usar")

    def _create_empty_db(self):
        """Crea un archivo de base de datos vacío con estructura segura"""
        try:
            empty_db = {
                "metadata": {
                    "version": "2.1.0",
                    "created_at": datetime.now().isoformat(),
                    "last_modified": datetime.now().isoformat(),
                    "user_count": 0,
                    "integrity_hash": ""
                },
                "users": {}
            }

            # Calcular hash de integridad
            empty_db["metadata"]["integrity_hash"] = self._calculate_integrity_hash(empty_db["users"])

            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(empty_db, f, ensure_ascii=False, indent=2)

            logger.info("Base de datos vacía creada con estructura segura")
        except Exception as e:
            logger.error(f"Error creando base de datos: {e}")
            raise

    def _load_database(self) -> Dict:
        """Carga la base de datos completa con verificación"""
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    db = json.load(f)

                # Verificar integridad
                if not self._verify_data_integrity(db):
                    logger.warning("Integridad de datos comprometida, reparando...")
                    db = self._repair_database_data(db)

                return db
            return self._create_empty_db_structure()
        except json.JSONDecodeError:
            logger.error("Error de formato JSON en la base de datos")
            return self._repair_corrupted_db()
        except Exception as e:
            logger.error(f"Error cargando base de datos: {e}")
            return self._create_empty_db_structure()

    def _save_database(self, db: Dict) -> bool:
        """Guarda la base de datos con verificación de integridad"""
        try:
            # Actualizar metadatos
            db["metadata"]["last_modified"] = datetime.now().isoformat()
            db["metadata"]["user_count"] = len(db["users"])
            db["metadata"]["integrity_hash"] = self._calculate_integrity_hash(db["users"])

            # Crear backup antes de guardar
            self.backup_manager.create_backup()

            # Guardar con write-and-replace para evitar corrupción
            temp_file = self.users_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(db, f, ensure_ascii=False, indent=2)

            # Reemplazar archivo original
            temp_file.replace(self.users_file)

            logger.debug("Base de datos guardada exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error guardando base de datos: {e}")
            return False

    def _calculate_integrity_hash(self, data: Dict) -> str:
        """Calcula hash de integridad para los datos"""
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    def _verify_data_integrity(self, db: Dict) -> bool:
        """Verifica la integridad de los datos"""
        if "metadata" not in db or "users" not in db:
            return False

        expected_hash = db["metadata"].get("integrity_hash", "")
        actual_hash = self._calculate_integrity_hash(db["users"])
        return expected_hash == actual_hash

    def _verify_database_integrity(self) -> bool:
        """Verifica integridad completa de la base de datos"""
        try:
            db = self._load_database()
            return self._verify_data_integrity(db)
        except:
            return False

    def _repair_database(self):
        """Repara la base de datos corrupta"""
        try:
            backup = self.backup_manager.get_latest_backup()
            if backup and backup.exists():
                self.backup_manager.restore_backup(backup)
                logger.info("Base de datos reparada desde backup")
            else:
                self._create_empty_db()
                logger.info("Nueva base de datos creada (no había backup)")
        except Exception as e:
            logger.error(f"Error reparando base de datos: {e}")
            self._create_empty_db()

    def _repair_corrupted_db(self) -> Dict:
        """Intenta reparar una base de datos corrupta"""
        try:
            # Intentar recuperar datos del archivo corrupto
            with open(self.users_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Buscar estructura de usuarios
            users_match = re.search(r'"users":\s*({[^}]*})', content)
            if users_match:
                users_json = users_match.group(1)
                users_data = json.loads(users_json)
                db = self._create_empty_db_structure()
                db["users"] = users_data
                return db
        except:
            pass
        return self._create_empty_db_structure()

    def _create_empty_db_structure(self) -> Dict:
        """Crea estructura de base de datos vacía"""
        return {
            "metadata": {
                "version": "2.1.0",
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "user_count": 0,
                "integrity_hash": self._calculate_integrity_hash({})
            },
            "users": {}
        }

    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple:
        """Genera hash seguro de la contraseña con salt"""
        if salt is None:
            salt = secrets.token_hex(16)

        # Usar PBKDF2 para hashing más seguro
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iteraciones
        ).hex()

        return password_hash, salt

    def create_user(self, phone: str, password: str) -> bool:
        """Crea un nuevo usuario con validación mejorada"""
        try:
            # Validar formato de teléfono
            if not self._validate_phone_format(phone):
                return False

            # Validar fortaleza de contraseña
            if not self._validate_password_strength(password):
                return False

            db = self._load_database()

            if phone in db["users"]:
                return False  # Usuario ya existe

            # Crear hash seguro de contraseña con PBKDF2
            password_hash, salt = self._hash_password(password)

            db["users"][phone] = {
                'password_hash': password_hash,
                'salt': salt,
                'created_at': datetime.now().isoformat(),
                'last_login': None,
                'is_active': True,
                'login_attempts': 0,
                'locked_until': None,
                'preferences': {
                    'audio_enabled': True,
                    'font_size': 'medium',
                    'theme': 'default'
                }
            }

            return self._save_database(db)
        except Exception as e:
            logger.error(f"Error creando usuario {phone}: {e}")
            return False

    def validate_user(self, phone: str, password: str) -> bool:
        """Valida las credenciales del usuario con protección contra fuerza bruta"""
        try:
            db = self._load_database()

            if phone not in db["users"]:
                return False

            user_data = db["users"][phone]

            # Verificar si la cuenta está bloqueada
            if self._is_account_locked(user_data):
                return False

            stored_hash = user_data['password_hash']
            salt = user_data.get('salt')

            # MIGRACIÓN: Si no hay salt, es el método antiguo (SHA256 simple)
            if salt is None:
                # Verificar con método antiguo
                old_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
                if old_hash == stored_hash:
                    # Migrar a nuevo método PBKDF2
                    new_hash, new_salt = self._hash_password(password)
                    user_data['password_hash'] = new_hash
                    user_data['salt'] = new_salt
                    user_data['login_attempts'] = 0
                    user_data['last_login'] = datetime.now().isoformat()
                    self._save_database(db)
                    return True
                return False

            # Método nuevo (PBKDF2)
            input_hash, _ = self._hash_password(password, salt)
            if hmac.compare_digest(input_hash, stored_hash):
                # Login exitoso - resetear contador de intentos
                user_data['login_attempts'] = 0
                user_data['last_login'] = datetime.now().isoformat()
                user_data['locked_until'] = None
                self._save_database(db)
                return True
            else:
                # Login fallido - incrementar intentos
                user_data['login_attempts'] = user_data.get('login_attempts', 0) + 1

                # Bloquear cuenta después de múltiples intentos
                if user_data['login_attempts'] >= AppConfig.MAX_LOGIN_ATTEMPTS:
                    user_data['locked_until'] = (datetime.now() + timedelta(minutes=30)).isoformat()

                self._save_database(db)
                return False
        except Exception as e:
            logger.error(f"Error validando usuario {phone}: {e}")
            return False

    def _is_account_locked(self, user_data: Dict) -> bool:
        """Verifica si la cuenta está temporalmente bloqueada"""
        locked_until = user_data.get('locked_until')
        if locked_until:
            try:
                lock_time = datetime.fromisoformat(locked_until)
                if datetime.now() < lock_time:
                    return True
            except:
                pass
        return False

    def _validate_phone_format(self, phone: str) -> bool:
        """Valida el formato del número de teléfono"""
        return (phone.isdigit() and
                len(phone) == 10 and
                phone.startswith('3'))

    def _validate_password_strength(self, password: str) -> bool:
        """Valida la fortaleza de la contraseña"""
        if len(password) < AppConfig.PASSWORD_MIN_LENGTH:
            return False

        # Verificar que tenga al menos 3 letras y 3 números
        letters = sum(c.isalpha() for c in password)
        digits = sum(c.isdigit() for c in password)
        return letters >= 3 and digits >= 3

    def user_exists(self, phone: str) -> bool:
        """Verifica si un usuario existe"""
        db = self._load_database()
        return phone in db["users"]

    def get_user_data(self, phone: str) -> Optional[Dict]:
        """Obtiene los datos de un usuario de forma segura"""
        try:
            db = self._load_database()
            user_data = db["users"].get(phone)
            if user_data:
                # No retornar información sensible
                safe_data = user_data.copy()
                safe_data.pop('password_hash', None)
                safe_data.pop('salt', None)
                return safe_data
            return None
        except Exception as e:
            logger.error(f"Error obteniendo datos de usuario {phone}: {e}")
            return None

    def update_user_preference(self, phone: str, preference: str, value: any) -> bool:
        """Actualiza una preferencia del usuario"""
        try:
            db = self._load_database()
            if phone not in db["users"]:
                return False

            if 'preferences' not in db["users"][phone]:
                db["users"][phone]['preferences'] = {}

            db["users"][phone]['preferences'][preference] = value
            return self._save_database(db)
        except Exception as e:
            logger.error(f"Error actualizando preferencia de usuario {phone}: {e}")
            return False

    def get_all_users(self) -> List[Dict]:
        """Obtiene lista de todos los usuarios (sin información sensible)"""
        try:
            db = self._load_database()
            users = []
            for phone, data in db["users"].items():
                safe_data = {
                    'phone': phone,
                    'created_at': data.get('created_at'),
                    'last_login': data.get('last_login'),
                    'is_active': data.get('is_active', True)
                }
                users.append(safe_data)
            return users
        except Exception as e:
            logger.error(f"Error obteniendo lista de usuarios: {e}")
            return []

    def delete_user(self, phone: str) -> bool:
        """Elimina un usuario de forma segura"""
        try:
            db = self._load_database()
            if phone in db["users"]:
                del db["users"][phone]
                return self._save_database(db)
            return False
        except Exception as e:
            logger.error(f"Error eliminando usuario {phone}: {e}")
            return False

    def _repair_database_data(self, db: Dict) -> Dict:
        """Repara los datos de la base de datos"""
        try:
            # Asegurar que la estructura básica existe
            if "metadata" not in db:
                db["metadata"] = {}
            if "users" not in db:
                db["users"] = {}

            # Actualizar metadatos
            db["metadata"]["version"] = "2.1.0"
            db["metadata"]["last_modified"] = datetime.now().isoformat()
            db["metadata"]["user_count"] = len(db["users"])
            db["metadata"]["integrity_hash"] = self._calculate_integrity_hash(db["users"])
            return db
        except Exception as e:
            logger.error(f"Error reparando datos de la base de datos: {e}")
            return self._create_empty_db_structure()

class BackupManager:
    """Gestor de backups para la base de datos"""

    def __init__(self):
        self.backup_dir = AppConfig.BACKUP_DIR
        AppConfig.ensure_directories()

    def create_backup(self) -> bool:
        """Crea un backup de la base de datos"""
        try:
            db_file = AppConfig.USERS_DB
            if not db_file.exists():
                return False

            # Crear nombre de backup con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"users_backup_{timestamp}.json"

            # Copiar archivo
            import shutil
            shutil.copy2(db_file, backup_file)

            # Limpiar backups antiguos (mantener solo los 5 más recientes)
            self._clean_old_backups()

            logger.info(f"Backup creado: {backup_file.name}")
            return True
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            return False

    def _clean_old_backups(self):
        """Elimina backups antiguos, manteniendo solo los más recientes"""
        try:
            backups = list(self.backup_dir.glob("users_backup_*.json"))
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Mantener solo los 5 backups más recientes
            for backup in backups[5:]:
                try:
                    backup.unlink()
                    logger.debug(f"Backup antiguo eliminado: {backup.name}")
                except:
                    pass
        except Exception as e:
            logger.error(f"Error limpiando backups antiguos: {e}")

    def get_latest_backup(self) -> Optional[Path]:
        """Obtiene el backup más reciente"""
        try:
            backups = list(self.backup_dir.glob("users_backup_*.json"))
            if not backups:
                return None
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return backups[0]
        except Exception as e:
            logger.error(f"Error obteniendo último backup: {e}")
            return None

    def restore_backup(self, backup_file: Optional[Path] = None) -> bool:
        """Restaura la base de datos desde un backup"""
        try:
            if backup_file is None:
                backup_file = self.get_latest_backup()

            if backup_file is None or not backup_file.exists():
                return False

            # Crear backup de la base de datos actual antes de restaurar
            self.create_backup()

            # Restaurar desde backup
            import shutil
            shutil.copy2(backup_file, AppConfig.USERS_DB)

            logger.info(f"Base de datos restaurada desde backup: {backup_file.name}")
            return True
        except Exception as e:
            logger.error(f"Error restaurando backup: {e}")
            return False
