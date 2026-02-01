from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.database import get_db
from app.config.settings import settings
from app.modules.usuarios.models import Usuario

# Essa função é o "Login Required" do Django
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