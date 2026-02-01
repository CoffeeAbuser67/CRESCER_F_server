from app.database import TimeStampedModel
from sqlalchemy import Column, String

class Usuario(TimeStampedModel):
    __tablename__ = "usuarios"

    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)