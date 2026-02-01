import bcrypt
from datetime import datetime, timedelta, timezone
import hashlib
from jose import jwt
from app.config.settings import settings

# ... (Mantenha verify_password e get_password_hash iguais) ...

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