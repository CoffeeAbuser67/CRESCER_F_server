from pydantic import BaseModel, EmailStr
from uuid import UUID  
from datetime import datetime

class MedicoBase(BaseModel):
    name: str
    last_name: str
    email: EmailStr

class MedicoCreate(MedicoBase):
    pass

class MedicoResponse(MedicoBase):
    pkid: int         
    id: UUID          
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True