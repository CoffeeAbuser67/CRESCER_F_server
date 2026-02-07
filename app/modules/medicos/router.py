from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.usuarios.models import Usuario
from .models import Medico
from .schemas import MedicoCreate, MedicoResponse
from typing import Annotated # 
from app.auth import get_current_user

router = APIRouter(prefix="/medicos", tags=["Médicos"])

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[Usuario, Depends(get_current_user)]


@router.post("/", response_model=MedicoResponse)
def criar_medico(medico: MedicoCreate, db: Session = Depends(get_db), user = Depends(get_current_user)):
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

@router.get("/", response_model=list[MedicoResponse])
def listar_medicos(db: Session = Depends(get_db)):
    return db.query(Medico).all()