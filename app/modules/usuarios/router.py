from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth_utils import get_password_hash, verify_password, create_access_token
from app.dependencies import get_current_user # Importamos a dependência que criamos

from .models import Usuario
from .schemas import UsuarioCreate, UsuarioLogin, UsuarioResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])

# --- REGISTRO ---
@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UsuarioCreate, db: Session = Depends(get_db)):
    # Verifica duplicidade
    if db.query(Usuario).filter(Usuario.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Cria usuário
    hashed_pw = get_password_hash(user_in.password)
    novo_usuario = Usuario(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pw
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

# --- LOGIN (Set Cookie) ---
@router.post("/login")
def login(user_in: UsuarioLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == user_in.email).first()
    
    # Verifica senha
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    # Gera JWT
    access_token = create_access_token(data={"sub": user.email})
    
    # Seta Cookie HttpOnly
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,  # <--- O Segredo da segurança
        max_age=1800,   # 30 min
        expires=1800,
        samesite="lax",
        secure=False    # Em prod (HTTPS) mude para True
    )
    return {"message": "Login realizado", "username": user.username}

# --- LOGOUT (Kill Cookie) ---
@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logout realizado"}

# --- ROTA TESTE PROTEGIDA ---
@router.get("/me", response_model=UsuarioResponse)
def get_me(current_user: Usuario = Depends(get_current_user)):
    return current_user