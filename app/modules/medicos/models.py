
from app.database import TimeStampedModel 
from sqlalchemy import Column, String

class Medico(TimeStampedModel):
    __tablename__ = "medicos"

    name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)