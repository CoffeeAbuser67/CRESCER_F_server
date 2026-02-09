from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Annotated, List

from app.database import get_db
from app.auth import get_current_user

from . import models, schemas

router = APIRouter(prefix="/financeiro", dependencies=[Depends(get_current_user)], tags=["Financeiro"])

# Dependency simplificada com Annotated
db_dependency = Annotated[Session, Depends(get_db)]


# --- ENDPOINTS AUXILIARES ---

@router.post("/profissionais", response_model=schemas.ProfissionalResponse, status_code=status.HTTP_201_CREATED)
def create_profissional(data: schemas.ProfissionalCreate, db: db_dependency):
    try:
        obj = models.Profissional(**data.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback() # Limpa a sessão
        raise HTTPException(
            status_code=409,
            detail=f"Já existe um profissional cadastrado com o nome '{data.nome}'."
        )


@router.post("/servicos", response_model=schemas.ServicoResponse, status_code=status.HTTP_201_CREATED)
def create_servico(data: schemas.ServicoCreate, db: db_dependency):
    try:
        obj = models.Servico(**data.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback() 
        raise HTTPException(
            status_code=409, 
            detail=f"Já existe um serviço cadastrado com o nome '{data.nome}'."
        )


# --- ENDPOINTS DE LANÇAMENTO ---


@router.post("/lancamentos", response_model=schemas.LancamentoResponse, status_code=status.HTTP_201_CREATED)
def create_lancamento(data: schemas.LancamentoCreate, db: db_dependency):
    # --- 1. RESOLUÇÃO DO PACIENTE (On-the-fly) ---
    target_paciente_id = data.paciente_id

    if not target_paciente_id and data.paciente_nome:
        # *******************
        # HERE AJUSTE 
        # Se quiser evitar duplicatas exatas por nome, pode fazer um .filter().first() antes.
        # Por agora, criamos direto para manter a agilidade do Excel.
        # *******************
        novo_paciente = models.Paciente(nome=data.paciente_nome)
        db.add(novo_paciente)
        db.flush()
        db.refresh(novo_paciente)
        target_paciente_id = novo_paciente.id

    # --- 2. VALIDAÇÃO DE CATEGORIA vs PROFISSIONAL ---
    servico = db.query(models.Servico).filter(models.Servico.id == data.servico_id).first()
    
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado.")

    if servico.categoria == models.CategoriaServico.CONSULTA and not data.profissional_id:
        raise HTTPException(
            status_code=400, 
            detail="Lançamentos do tipo CONSULTA exigem um profissional vinculado."
        )

    # --- 3. CRIAÇÃO DO LANÇAMENTO ---
    # Convertemos o Pydantic para Dict, removendo campos de auxílio do paciente
    lancamento_data = data.model_dump(exclude={"paciente_nome", "paciente_id"})
    
    novo_lancamento = models.Lancamento(
        **lancamento_data,
        paciente_id=target_paciente_id
    )

    db.add(novo_lancamento)
    db.commit()
    db.refresh(novo_lancamento)
    
    return novo_lancamento

@router.get("/lancamentos", response_model=List[schemas.LancamentoResponse])
def list_lancamentos(db: db_dependency, skip: int = 0, limit: int = 100):
    return db.query(models.Lancamento).offset(skip).limit(limit).all()