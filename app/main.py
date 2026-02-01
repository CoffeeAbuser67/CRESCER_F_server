from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base

# Imports dos Routers
from app.modules.medicos.router import router as medicos_router
from app.modules.usuarios.router import router as usuarios_router

# Cria tabelas (Medicos e Usuarios)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Gestão Médica")

# CORS (Fundamental pro React conseguir enviar Cookies)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_credentials=True, 
    allow_headers=["*"],
)

# Registra as rotas
app.include_router(medicos_router)
app.include_router(usuarios_router)

@app.get("/healthcheck")
def health_check():
    return {"status": "ok"}