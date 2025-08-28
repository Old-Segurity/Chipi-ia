```markdown
# OLD-SECURITY CHIPI IA - Asistente Virtual para Adultos Mayores

## Descripción

OLD-SECURITY CHIPI IA es un asistente virtual especializado diseñado específicamente para adultos mayores, con enfoque en ciberseguridad y usabilidad.

## Características

- 🤖 Asistente conversacional con IA
- 🔒 Enfoque en ciberseguridad
- 📱 Interfaz accesible para adultos mayores
- 💾 Sistema de memoria personalizado
- 🎤 Texto a voz integrado
- 📋 Gestión de contraseñas seguras

## Tecnologías

- Backend: Python + FastAPI
- Frontend: HTML5 + CSS3 + JavaScript
- IA: OpenRouter API
- Hosting: Render.com

## Instalación

1. Clona el repositorio
2. Instala dependencias: `pip install -r requirements.txt`
3. Configura variables de entorno en Render.com dashboard
4. Despliega en Render.com

## Variables de Entorno

- `OPENROUTER_API_KEY`: Tu clave API de OpenRouter

## Despliegue en Render.com

1. Conecta tu repositorio de GitHub a Render
2. Configura las variables de entorno en el dashboard
3. Render detectará automáticamente la configuración y desplegará la aplicación

## Estructura del Proyecto

```

oldsegurity-website/ ├──app/                 # Código backend Python ├──static/              # Archivos frontend estáticos ├──requirements.txt     # Dependencias Python ├──render.yaml          # Configuración de Render └──runtime.txt          # Versión de Python

```

## Uso

1. Abre la aplicación en tu navegador
2. Regístrate con tu número de teléfono
3. ¡Comienza a chatear con CHIPI IA!

## Soporte

Para soporte técnico, contacta a soporte@oldsecurity.com
```

Instrucciones de despliegue:

1. Crea un nuevo repositorio en GitHub con todos estos archivos
2. Conecta tu repositorio a Render.com:
   · Ve a Render.com
   · Conecta tu cuenta de GitHub
   · Selecciona el repositorio
   · Render detectará automáticamente la configuración
3. Configura las variables de entorno en Render:
   · En el dashboard de Render, ve a la sección de Environment
   · Añade la variable OPENROUTER_API_KEY con tu clave API de OpenRouter
4. ¡Listo! Render desplegará automáticamente tu aplicación
