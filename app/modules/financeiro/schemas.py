from pydantic import BaseModel, ConfigDict, Field, model_validator
from uuid import UUID
from datetime import date
from decimal import Decimal
from typing import Optional
from .models import CategoriaServico, MetodoPagamento


# ── ⋙────── SCHEMAS DE PACIENTE ─────────➤




class PacienteMinimo(BaseModel): # <●> PacienteMinimo
    id: UUID
    nome: str
    model_config = ConfigDict(from_attributes=True)


class PacienteBase(BaseModel): # <●> PacienteBase
    nome: str = Field(..., min_length=2, max_length=100)
    telefone: Optional[str] = None


class PacienteCreate(PacienteBase): # <●> PacienteCreate
    pass



class PacienteResponse(PacienteBase): # <●> PacienteResponse
    id: UUID
    # Adicionamos o ConfigDict para o Pydantic ler o modelo do SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


# ── ⋙────── SCHEMAS DE PROFISSIONAL ─────────➤




class ProfissionalMinimo(BaseModel):
    id: UUID
    nome: str
    ativo: bool
    model_config = ConfigDict(from_attributes=True)




class ProfissionalBase(BaseModel): # <●> ProfissionalBase
    nome: str
    ativo: bool = True



class ProfissionalCreate(ProfissionalBase): # <●> ProfissionalCreate
    pass


class ProfissionalResponse(ProfissionalBase): # <●> ProfissionalResponse
    id: UUID
    model_config = ConfigDict(from_attributes=True)


# ── ⋙────── SCHEMAS DE SERVIÇO ─────────➤









class ServicoMinimo(BaseModel): # <●> ServicoMinimo
    id: UUID
    nome: str
    categoria: str
    model_config = ConfigDict(from_attributes=True)
class ServicoBase(BaseModel): # <●> ServicoBase
    nome: str
    categoria: CategoriaServico

class ServicoCreate(ServicoBase): # <●> ServicoCreate
    pass

class ServicoResponse(ServicoBase): # <●> ServicoResponse
    id: UUID
    model_config = ConfigDict(from_attributes=True)




# ── ⋙────── SCHEMAS DE LANÇAMENTO ─────────➤
class LancamentoBase(BaseModel): # <●> LancamentoBase
    data_pagamento: date
    data_competencia: date
    valor: Decimal = Field(..., gt=0)
    metodo_pagamento: MetodoPagamento
    observacao: Optional[str] = None


class LancamentoCreate(LancamentoBase): # <●> LancamentoCreate
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


class LancamentoResponse(BaseModel): # <●> LancamentoResponse
    id: UUID
    data_pagamento: date
    data_competencia: date
    valor: Decimal
    metodo_pagamento: str
    observacao: Optional[str] = None
    
    paciente: Optional[PacienteMinimo] = None 
    servico: ServicoMinimo = None # (Defina um schema de serviço tbm se precisar)
    profissional: Optional[ProfissionalMinimo] = None
    model_config = ConfigDict(from_attributes=True)






