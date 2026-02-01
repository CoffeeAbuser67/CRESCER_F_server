
from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID 
from app.database import TimeStampedModel

class Usuario(TimeStampedModel):
    __tablename__ = "usuarios"

    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Relacionamento com os tokens (Um usuário pode ter vários tokens ativos)
    refresh_tokens = relationship("UserRefreshToken", back_populates="usuario", cascade="all, delete-orphan")


class UserRefreshToken(TimeStampedModel):
    __tablename__ = "user_refresh_tokens"

    token_hash = Column(String, index=True, nullable=False) # Guardamos o hash do token, não o token puro (segurança extra)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False) # Se true, esse token e sua família estão mortos
    user_agent = Column(String, nullable=True) 
    ip_address = Column(String, nullable=True)

    usuario = relationship("Usuario", back_populates="refresh_tokens")