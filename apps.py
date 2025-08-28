"""
Sistema de lanzamiento de aplicaciones Android
Mejorado con más aplicaciones y mejor detección
"""

import re
import logging
from typing import Optional, Dict, List, Tuple
from app.config import AppConfig
from app.utils import Logger

logger = Logger.get_logger(__name__)

class AppLauncher:
    """Lanzador de aplicaciones Android optimizado para adultos mayores"""

    # Base de datos extensa de aplicaciones colombianas (mejorada)
    APP_PACKAGES = {
        # Comunicación y redes sociales
        "whatsapp": "com.whatsapp",
        "wasap": "com.whatsapp",
        "watsapp": "com.whatsapp",
        "facebook": "com.facebook.katana",
        "messenger": "com.facebook.orca",
        "instagram": "com.instagram.android",
        "telegram": "org.telegram.messenger",
        "twitter": "com.twitter.android",
        "x": "com.twitter.android",
        "tiktok": "com.zhiliaoapp.musically",
        "linkedin": "com.linkedin.android",

        # Correo electrónico
        "correo": "com.google.android.gm",
        "gmail": "com.google.android.gm",
        "mail": "com.google.android.gm",
        "outlook": "com.microsoft.office.outlook",
        "hotmail": "com.microsoft.office.outlook",
        "yahoo mail": "com.yahoo.mobile.client.android.mail",

        # Videollamadas
        "skype": "com.skype.raider",
        "zoom": "us.zoom.videomeetings",
        "meet": "com.google.android.apps.meetings",
        "google meet": "com.google.android.apps.meetings",
        "duo": "com.google.android.apps.tachyon",
        "teams": "com.microsoft.teams",
        "webex": "com.cisco.webex.meetings",

        # Bancos colombianos (lista ampliada)
        "bancolombia": "com.bancolombia.app.personas",
        "nequi": "com.nequi.MobileApp",
        "daviplata": "com.davivienda.daviplata",
        "davivienda": "com.davivienda.daviplus",
        "bbva": "com.bbva.netcash",
        "banco de bogota": "com.bancodebogota.banco",
        "banco popular": "com.bancopopular.virtual",
        "scotiabank": "com.scotiabankcolpatria.banca",
        "bancoomeva": "com.coomeva.mobilebanking",
        "banco caja social": "com.casocial.bancamovil",
        "banagrario": "com.bancoagrario.transacciones",
        "movii": "com.redmovil.movii",
        "sufi": "com.sufi.mobile",
        "bancamia": "com.bancamia.app",
        "banco falabella": "com.falabella.falabellamobile",
        "banco pichincha": "com.grupopichincha.mobilebanking",
        "banco w": "com.bancow.app",
        "banco santander": "com.soaint.santander.consumer",

        # EPS y salud (lista ampliada)
        "sura": "com.epssura.citas",
        "eps sura": "com.epssura.citas",
        "nuevo eps": "com.nuevoeps.movil",
        "sanitas": "com.colsanitas.colsanitasmovil",
        "compensar": "com.compensar.saludmovil",
        "salud total": "com.saludtotal.saludtotalmovil",
        "famisanar": "com.famisanar.virtual",
        "coomeva eps": "com.coomeva.salud",
        "medimas": "com.medimas.salud",
        "saludvida": "com.saludvida.eps",
        "capital salud": "com.capitalsalud.eps",
        "aliansalud": "com.aliansalud.eps",
        "comfacor": "com.comfacor.eps",

        # Compras y domicilios
        "mercado libre": "com.mercadolibre",
        "mercadolibre": "com.mercadolibre",
        "rappi": "com.rappi.customer",
        "uber": "com.ubercab",
        "didi": "com.didiglobal.passenger",
        "cabify": "com.cabify.rider",
        "jumbo": "com.jumbo.app",
        "exito": "com.exito.app",
        "olx": "com.olx.olx",
        "amazon": "com.amazon.mShop.android.shopping",
        "didi food": "com.xiaojukeji.didifood.global",
        "uber eats": "com.ubercab.eats",
        "domicilios.com": "com.domicilios.android.restaurant",
        "ifood": "br.com.brainweb.ifood",

        # Entretenimiento
        "youtube": "com.google.android.youtube",
        "yt": "com.google.android.youtube",
        "spotify": "com.spotify.music",
        "netflix": "com.netflix.mediaclient",
        "disney plus": "com.disney.disneyplus",
        "hbo max": "com.hbo.hbonow",
        "prime video": "com.amazon.avod.thirdpartyclient",
        "caracol play": "com.caracol.play",
        "win sports": "com.winsports.winsportsonline",
        "rtvc play": "co.gov.rtvcplay",
        "claro video": "com.clarovideo.app",

        # Navegación y mapas
        "maps": "com.google.android.apps.maps",
        "mapas": "com.google.android.apps.maps",
        "google maps": "com.google.android.apps.maps",
        "waze": "com.waze",
        "google earth": "com.google.earth",

        # Utilidades básicas
        "chrome": "com.android.chrome",
        "navegador": "com.android.chrome",
        "calculadora": "com.google.android.calculator",
        "calendario": "com.google.android.calendar",
        "reloj": "com.google.android.deskclock",
        "contactos": "com.google.android.contacts",
        "galería": "com.sec.android.gallery3d",
        "fotos": "com.google.android.apps.photos",
        "configuración": "com.android.settings",
        "configuracion": "com.android.settings",
        "cámara": "com.android.camera2",
        "camara": "com.android.camera2",

        # Operadores telefónicos
        "mi claro": "com.claro.app",
        "claro": "com.claro.app",
        "mi tigo": "com.tigo.shop",
        "tigo": "com.tigo.shop",
        "mi movistar": "com.telefonica.movistar",
        "movistar": "com.telefonica.movistar",
        "mi etb": "com.etb.app",
        "etb": "com.etb.app",
        "mi wom": "co.wom.womapp",
        "wom": "co.wom.womapp",
        "virgin mobile": "com.virginmobile.latam",

        # Gobierno y trámites
        "gov co": "com.govco.app",
        "gobierno": "com.govco.app",
        "simit": "co.org.simit",
        "registraduria": "com.registraduria.app",
        "cedula": "com.registraduria.app",
        "rut": "co.com.andi.app",
        "siise": "co.gov.sisben",
        "sisben": "co.gov.sisben",
        "agencia nacional": "co.gov.ane.app",
        "dian": "co.gov.dian.movil",

        # Otros servicios útiles
        "play store": "com.android.vending",
        "tienda": "com.android.vending",
        "kindle": "com.amazon.kindle",
        "biblia": "com.sirma.mobile.bible.android",
        "dropbox": "com.dropbox.android",
        "drive": "com.google.android.apps.docs",
        "google drive": "com.google.android.apps.docs",
        "onedrive": "com.microsoft.skydrive",
        "weather": "com.accuweather.android",
        "clima": "com.accuweather.android"
    }

    # Patrones de reconocimiento de comandos mejorados
    APP_PATTERNS = [
        r"(?:abrir|abre|abrime|quiero abrir|puedes abrir|activar|iniciar|ejecutar)?\s*(?:la\s+app\s+|el\s+app\s+|app\s+|aplicación\s+|aplicacion\s+)?(.+)",
        r"necesito\s+(?:usar\s+|acceder\s+)?(.+)",
        r"usar\s+(?:la\s+)?(.+)",
        r"entrar\s+a\s+(.+)",
        r"ir\s+a\s+(.+)",
        r"quiero\s+(?:ver\s+|usar\s+)?(.+)"
    ]

    # Tipos de teclado para diferentes apps (ampliado)
    APP_KEYBOARD_TYPES = {
        # Bancos - teclado numérico
        "bancolombia": "number",
        "nequi": "number",
        "daviplata": "number",
        "davivienda": "number",
        "bbva": "number",
        "banco de bogota": "number",
        "banco popular": "number",
        "scotiabank": "number",
        "bancoomeva": "number",
        "banco caja social": "number",
        "banagrario": "number",
        "movii": "number",
        "sufi": "number",
        "bancamia": "number",

        # Redes sociales - teclado alfanumérico
        "whatsapp": "text",
        "facebook": "text",
        "instagram": "text",
        "twitter": "text",
        "gmail": "text",
        "correo": "text",

        # Juegos - teclado normal
        "juegos": "text",

        # Utilidades - según necesidad
        "calculadora": "number",
        "calendario": "text"
    }

    def __init__(self):
        self.android_available = False
        # En versión web, no inicializamos módulos Android
        logger.info("AppLauncher inicializado en modo web")

    def find_app_package(self, command: str) -> Optional[str]:
        """Encuentra el paquete de una app basado en el comando del usuario"""
        command_clean = command.lower().strip()

        # Probar patrones de reconocimiento
        for pattern in self.APP_PATTERNS:
            match = re.search(pattern, command_clean)
            if match:
                app_name = match.group(1).strip()
                # Limpiar el nombre de la app
                app_name = self._clean_app_name(app_name)
                if not app_name:
                    continue

                # Buscar coincidencia exacta
                if app_name in self.APP_PACKAGES:
                    return self.APP_PACKAGES[app_name]

                # Buscar coincidencia parcial con prioridad
                matches = self._find_partial_matches(app_name)
                if matches:
                    # Devolver la mejor coincidencia
                    return matches[0][1]

        return None

    def _clean_app_name(self, name: str) -> str:
        """Limpia el nombre de la app removiendo palabras innecesarias"""
        words_to_remove = [
            "la", "el", "de", "del", "app", "aplicacion", "aplicación",
            "por", "para", "con", "mi", "tu", "su", "al", "se", "es",
            "en", "un", "una", "uno", "unas", "unos", "lo", "las", "los",
            "que", "qué", "como", "cómo", "cuando", "cuándo", "donde", "dónde"
        ]

        words = name.split()
        cleaned_words = [word for word in words if word.lower() not in words_to_remove and len(word) > 2]
        return " ".join(cleaned_words).strip()

    def _find_partial_matches(self, app_name: str) -> List[Tuple[str, str]]:
        """Encuentra coincidencias parciales ordenadas por relevancia"""
        matches = []
        app_name_lower = app_name.lower()

        for key, package in self.APP_PACKAGES.items():
            # Verificar si el nombre de la app está contenido en la clave
            if app_name_lower in key:
                # Priorizar coincidencias más largas y exactas
                score = len(key) - len(app_name_lower)
                matches.append((score, package, key))

            # Verificar si alguna palabra coincide
            elif any(word in key for word in app_name_lower.split()):
                score = 10  # Prioridad media
                matches.append((score, package, key))

        # Ordenar por score (menor score = mejor coincidencia)
        matches.sort(key=lambda x: x[0])
        return [(key, package) for score, package, key in matches]

    def launch_app(self, app_name: str) -> str:
        """Lanza una aplicación y retorna el resultado"""
        # En versión web, no podemos abrir apps nativas
        package = self.find_app_package(f"abrir {app_name}")
        if package:
            return f"En la versión web, no puedo abrir aplicaciones directamente. Pero puedo ayudarte con información sobre {app_name.title()}."
        else:
            return self._get_app_not_found_message(app_name)

    def _get_app_not_found_message(self, app_name: str) -> str:
        """Genera mensaje de ayuda cuando no se encuentra una app"""
        suggestions = self._get_similar_apps(app_name)
        message = f"No reconozco la aplicación '{app_name}'. "
        if suggestions:
            message += f"¿Te refieres a alguna de estas?\n"
            for suggestion in suggestions[:3]:  # Máximo 3 sugerencias
                message += f"• {suggestion.title()}\n"
        else:
            message += "Algunas apps que puedo abrir:\n"
            popular_apps = ["WhatsApp", "Facebook", "Bancolombia", "Nequi", "YouTube", "Gmail"]
            for app in popular_apps:
                message += f"• {app}\n"

        message += "\nPuedes decirme: 'Abrir [nombre de la app]'"
        return message.strip()

    def _get_similar_apps(self, app_name: str) -> List[str]:
        """Encuentra aplicaciones similares basadas en el nombre"""
        app_name_lower = app_name.lower()
        suggestions = []

        # Búsqueda por similitud de palabras
        for key in self.APP_PACKAGES.keys():
            # Buscar palabras similares
            if any(word in key for word in app_name_lower.split()) or \
                    any(word in app_name_lower for word in key.split()):
                suggestions.append(key)

        # Eliminar duplicados y limitar resultados
        return list(dict.fromkeys(suggestions))[:5]

    def get_keyboard_type(self, app_name: str) -> str:
        """Obtiene el tipo de teclado recomendado para una app"""
        app_name_clean = app_name.lower()
        for key, kbd_type in self.APP_KEYBOARD_TYPES.items():
            if key in app_name_clean:
                return kbd_type
        return "text"  # Por defecto

    def get_installed_apps(self) -> List[str]:
        """Obtiene lista de apps instaladas (si está disponible)"""
        # En versión web, no podemos detectar apps instaladas
        return []

    def get_app_categories(self) -> Dict[str, List[str]]:
        """Retorna las aplicaciones organizadas por categorías"""
        categories = {
            "Redes Sociales": ["whatsapp", "facebook", "instagram", "twitter", "linkedin"],
            "Bancos": ["bancolombia", "nequi", "daviplata", "bbva", "banco de bogota"],
            "Compras": ["mercado libre", "rappi", "amazon", "olx"],
            "Entretenimiento": ["youtube", "netflix", "spotify", "disney plus"],
            "Utilidades": ["calculadora", "calendario", "maps", "gmail"]
        }
        return categories

    def suggest_apps_by_category(self, category: str) -> List[str]:
        """Sugiere aplicaciones basadas en categoría"""
        categories = self.get_app_categories()
        return categories.get(category.lower(), [])
