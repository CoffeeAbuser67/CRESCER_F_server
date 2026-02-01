from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

# Importações do que criamos nos passos anteriores
from app.database import engine, Base, get_db
from app.modules.medicos.models import Medico
from app.modules.medicos.schemas import MedicoCreate, MedicoResponse
from fastapi.middleware.cors import CORSMiddleware

# Isso aqui cria as tabelas no seu Postgres se elas não existirem
# É o "quebra-galho" pra não precisar de migrations agora
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Gestão Médica")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção vc restringe, agora libera geral
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/medicos/", response_model=MedicoResponse)
def criar_medico(medico: MedicoCreate, db: Session = Depends(get_db)):

    db_medico = db.query(Medico).filter(Medico.email == medico.email).first()
    if db_medico:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    novo_medico = Medico(
        name=medico.name,
        last_name=medico.last_name,
        email=medico.email
    )
    
    db.add(novo_medico)
    db.commit()
    db.refresh(novo_medico)
    return novo_medico

@app.get("/medicos/", response_model=list[MedicoResponse])
def listar_medicos(db: Session = Depends(get_db)):
    medicos = db.query(Medico).all()
    return medicos