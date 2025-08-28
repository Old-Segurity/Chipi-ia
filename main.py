from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging
import os

# Import Chipi modules
from app.config import AppConfig
from app.database import DatabaseManager
from app.memory import MemoryManager
from app.assistant import ChipiAssistant
from app.apps import AppLauncher
from app.utils import Logger

logger = Logger.get_logger(__name__)

app = FastAPI(title="OLD-SECURITY CHIPI IA", version="2.1.0")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class LoginRequest(BaseModel):
    phone: str
    password: str

class RegisterRequest(BaseModel):
    phone: str
    password: str
    confirm_password: str

class MessageRequest(BaseModel):
    phone: str
    message: str

# Initialize components
db_manager = DatabaseManager()
app_launcher = AppLauncher()

@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "OLD-SECURITY CHIPI IA API Running"}

@app.post("/api/login")
async def login(request: LoginRequest):
    try:
        if db_manager.validate_user(request.phone, request.password):
            memory_manager = MemoryManager(request.phone)
            return {
                "success": True,
                "message": "Login exitoso",
                "phone": request.phone
            }
        else:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/register")
async def register(request: RegisterRequest):
    try:
        if request.password != request.confirm_password:
            raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")
        
        if db_manager.create_user(request.phone, request.password):
            return {
                "success": True,
                "message": "Usuario registrado exitosamente",
                "phone": request.phone
            }
        else:
            raise HTTPException(status_code=400, detail="No se pudo crear el usuario")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/message")
async def process_message(request: MessageRequest):
    try:
        if not db_manager.validate_user(request.phone, ""):
            raise HTTPException(status_code=401, detail="Usuario no autenticado")
        
        memory_manager = MemoryManager(request.phone)
        assistant = ChipiAssistant(memory_manager, app_launcher)
        response = assistant.process_command(request.message)
        
        return {
            "success": True,
            "response": response,
            "phone": request.phone
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
