from datetime import datetime, timedelta, timezone
import hashlib
from typing import Annotated

import bcrypt
from fastapi import Depends, HTTPException, Request, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.database import get_db
from app.modules.usuarios.models import Usuario


# HERE  --- 1. Hashing e Senhas ---

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def get_token_hash(token: str) -> str: 
    """
    Gera um hash SHA-256 para armazenar tokens longos no banco.
    Bcrypt não serve aqui porque tokens excedem 72 bytes.
    """
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


# HERE --- 2. Geração de Tokens (JWT) ---

def create_access_token(data: dict):
    to_encode = data.copy()
    # Expira em Minutos
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"}) # Adicionei type pra diferenciar
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    # Expira em DIAS
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# HERE --- 3. Validação de Token  ---

def get_current_user(request: Request, db: Session = Depends(get_db)):
    # 1. Tenta pegar o cookie
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    
    # 2. Limpa o prefixo 'Bearer ' se existir
    scheme, _, param = token.partition(" ")
    token_str = param if scheme.lower() == "bearer" else token

    # 3. Decodifica o JWT
    try:
        payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    # 4. Busca o usuário no banco
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    
    return user