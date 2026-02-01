import uuid
from sqlalchemy import create_engine, Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID 

# Configuração da Conexão
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:master@localhost:5432/CRESCER_F"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para todos os modelos
Base = declarative_base()



class TimeStampedModel(Base):
    __abstract__ = True 

    pkid = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

# Dependência do Banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()