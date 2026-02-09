from pydantic import BaseModel, ConfigDict, Field, model_validator
from uuid import UUID
from datetime import date
from decimal import Decimal
from typing import Optional
from .models import CategoriaServico, MetodoPagamento

# --- SCHEMAS DE PACIENTE ---
class PacienteBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    telefone: Optional[str] = None

class PacienteCreate(PacienteBase):
    pass

class PacienteResponse(PacienteBase):
    id: UUID
    # Adicionamos o ConfigDict para o Pydantic ler o modelo do SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

# --- SCHEMAS DE PROFISSIONAL ---
class ProfissionalBase(BaseModel):
    nome: str
    ativo: bool = True

class ProfissionalCreate(ProfissionalBase):
    pass

class ProfissionalResponse(ProfissionalBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

# --- SCHEMAS DE SERVIÇO ---
class ServicoBase(BaseModel):
    nome: str
    categoria: CategoriaServico
    preco_padrao: Optional[Decimal] = None

class ServicoCreate(ServicoBase):
    pass

class ServicoResponse(ServicoBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

# --- SCHEMAS DE LANÇAMENTO ---
class LancamentoBase(BaseModel):
    data_pagamento: date
    data_competencia: date
    valor: Decimal = Field(..., gt=0)
    metodo_pagamento: MetodoPagamento
    observacao: Optional[str] = None

class LancamentoCreate(LancamentoBase):
    servico_id: UUID
    profissional_id: Optional[UUID] = None
    
    # Suporte para Paciente On-the-fly
    paciente_id: Optional[UUID] = None
    paciente_nome: Optional[str] = None  # Preenchido se for um novo paciente

    @model_validator(mode='after')
    def validate_paciente_entry(self) -> 'LancamentoCreate':
        if not self.paciente_id and not self.paciente_nome:
            raise ValueError("É necessário informar o ID do paciente ou o Nome para cadastro novo.")
        return self


class LancamentoResponse(LancamentoBase):
    id: UUID
    paciente: PacienteResponse
    servico: ServicoResponse
    profissional: Optional[ProfissionalResponse] = None
    
    model_config = ConfigDict(from_attributes=True)