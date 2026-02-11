from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Annotated, List, Optional

from datetime import date, datetime

from app.database import get_db
from app.auth import get_current_user

from . import models, schemas

router = APIRouter(prefix="/financeiro", dependencies=[Depends(get_current_user)], tags=["Financeiro"])

# Dependency simplificada com Annotated
db_dependency = Annotated[Session, Depends(get_db)]





# --- ENDPOINTS AUXILIARES ---

@router.get("/pacientes", response_model=list[schemas.PacienteResponse])
def get_pacientes(db: db_dependency):
    return db.query(models.Paciente).order_by(models.Paciente.nome).all()


@router.get("/profissionais", response_model=List[schemas.ProfissionalResponse])
def list_profissionais(db: db_dependency):
    return db.query(models.Profissional).filter(
        models.Profissional.ativo == True
    ).order_by(models.Profissional.nome).all()


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


@router.get("/servicos", response_model=List[schemas.ServicoResponse])
def list_servicos(db: db_dependency):
    return db.query(models.Servico).order_by(models.Servico.nome).all()


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
    # --- 1. RESOLUÇÃO DO PACIENTE ---
    target_paciente_id = data.paciente_id

    # Lógica On-the-fly: Se não tem ID mas tem Nome
    if not target_paciente_id and data.paciente_nome:

        nome_limpo = data.paciente_nome.strip()

        paciente_existente = db.query(models.Paciente).filter(
            func.lower(models.Paciente.nome) == func.lower(nome_limpo)
        ).first()

        if paciente_existente:
            target_paciente_id = paciente_existente.id

        else:
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
def list_lancamentos(
    db: db_dependency, 
    skip: int = 0, 
    limit: int = 5000, 
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    query = db.query(models.Lancamento)

    if start_date:
        query = query.filter(models.Lancamento.data_pagamento >= start_date)
    
    if end_date:
        query = query.filter(models.Lancamento.data_pagamento <= end_date)

    query = query.order_by(desc(models.Lancamento.data_pagamento), desc(models.Lancamento.id))

    return query.offset(skip).limit(limit).all()