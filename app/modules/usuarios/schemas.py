from pydantic import BaseModel, EmailStr
from uuid import UUID

class UsuarioBase(BaseModel):
    username: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

class UsuarioResponse(UsuarioBase):
    id: UUID
    
    class Config:
        from_attributes = True