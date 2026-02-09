import enum
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, Enum, Numeric, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# Importa o modelo base do seu database.py existente
from app.database import TimeStampedModel

# Enums (Mantidos para garantir integridade e tipagem forte)
class CategoriaServico(str, enum.Enum):
    CONSULTA = "CONSULTA"
    TERAPIA = "TERAPIA"

class MetodoPagamento(str, enum.Enum):
    PIX = "PIX"
    DINHEIRO = "DINHEIRO"
    CARTAO_CREDITO = "CARTAO_CREDITO"
    CARTAO_DEBITO = "CARTAO_DEBITO"

class Paciente(TimeStampedModel):
    __tablename__ = "pacientes"

    # id, pkid, created_at já herdados de TimeStampedModel
    
    nome = Column(String, index=True, nullable=False, unique=True)
    telefone = Column(String, nullable=True)

    # Relacionamento reverso
    lancamentos = relationship("Lancamento", back_populates="paciente")

class Profissional(TimeStampedModel):
    __tablename__ = "profissionais" # Antigo 'medicos'

    nome = Column(String, nullable=False, unique=True)
    ativo = Column(Boolean, default=True)

    lancamentos = relationship("Lancamento", back_populates="profissional")

class Servico(TimeStampedModel):
    __tablename__ = "servicos"

    nome = Column(String, nullable=False, unique=True)
    categoria = Column(Enum(CategoriaServico), nullable=False)
    preco_padrao = Column(Numeric(10, 2), nullable=True) # Numeric é vital para dinheiro

    lancamentos = relationship("Lancamento", back_populates="servico")

class Lancamento(TimeStampedModel):
    __tablename__ = "lancamentos"

    # Datas
    data_pagamento = Column(String, nullable=False) # Armazenar como Date no banco, mas cuidado com fuso
    # Obs: Se preferir usar objeto date do python, use: from sqlalchemy import Date
    # data_pagamento = Column(Date, nullable=False) 
    
    from sqlalchemy import Date
    data_pagamento = Column(Date, nullable=False)
    data_competencia = Column(Date, nullable=False)
    
    valor = Column(Numeric(10, 2), nullable=False)
    metodo_pagamento = Column(Enum(MetodoPagamento), nullable=False)
    observacao = Column(Text, nullable=True)

    # Chaves Estrangeiras (Apontando para o UUID 'id' das outras tabelas)
    # Isso facilita o payload do JSON que já vem com UUID
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    servico_id = Column(UUID(as_uuid=True), ForeignKey("servicos.id"), nullable=False)
    
    # Profissional é Nullable (Regra da Terapia sem médico definido)
    profissional_id = Column(UUID(as_uuid=True), ForeignKey("profissionais.id"), nullable=True)
    
    # Relacionamentos
    paciente = relationship("Paciente", back_populates="lancamentos")
    servico = relationship("Servico", back_populates="lancamentos")
    profissional = relationship("Profissional", back_populates="lancamentos")


    # *******************
    # HERE Audit
    # Se precisar rastrear QUEM fez o lançamento (Audit), descomente abaixo:
    # usuario_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    # *******************