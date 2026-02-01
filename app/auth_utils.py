import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.config.settings import settings

# --- NÃO USAMOS MAIS O CryptContext do Passlib ---

def verify_password(plain_password: str, hashed_password: str):
    # O bcrypt pede bytes, então usamos .encode('utf-8')
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str):
    # Gera o salt e o hash
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8') # Retorna string para salvar no banco

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt