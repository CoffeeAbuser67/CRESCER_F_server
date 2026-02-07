from fastapi import APIRouter, Depends, HTTPException, Response, Request, status

from sqlalchemy.orm import Session

from app.database import get_db
from app.auth_utils import get_password_hash, get_token_hash, verify_password, create_access_token, create_refresh_token
from app.dependencies import get_current_user 

from app.config.settings import settings
from datetime import datetime, timedelta, timezone
from .models import Usuario, UserRefreshToken 

from .schemas import UsuarioCreate, UsuarioLogin, UsuarioResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])


# [ROUTE] /regsister 
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


# [ROUTE] /login 
@router.post("/login")
def login(user_in: UsuarioLogin, response: Response, db: Session = Depends(get_db)):
    # 1. Autentica
    user = db.query(Usuario).filter(Usuario.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    # 📌 --- LIMPEZA DE TOKENS EXPIRADOS ---
    # Antes de criar o novo, limpamos o lixo antigo deste usuário específico
    db.query(UserRefreshToken).filter(
        UserRefreshToken.usuario_id == user.id,
        UserRefreshToken.expires_at < datetime.now(timezone.utc)
    ).delete()
    # -----------------------------------


    # 2. Cria os Tokens
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    # 3. Salva o Refresh Token no Banco (HASHED para segurança)
    # Usamos a mesma função de hash de senha, pois o token é um segredo
    refresh_hash = get_token_hash(refresh_token)
    
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    db_refresh_token = UserRefreshToken(
        token_hash=refresh_hash,
        usuario_id=user.id, # O UUID do usuário
        expires_at=expires_at,
        is_revoked=False,

        # WARN  Em produção, pegue do request.headers.get("User-Agent")
        user_agent="v1_browser" 
    )
    db.add(db_refresh_token)
    db.commit()
    
    # 4. Seta os Cookies
    
    # Cookie 1: Access Token (Vida curta, envia pra tudo)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False 
    )

    # Cookie 2: Refresh Token (Vida longa, SÓ ENVIA PRA ROTA /auth/refresh)
    # Isso impede que o token vaze em requests normais
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        expires=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
        path="/auth/refresh",  # <--- A MÁGICA DE SEGURANÇA
        secure=False
    )

    return {"message": "Login realizado", "username": user.username}




# [ROUTE] /refresh 
@router.post("/refresh")
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    # 1. Pega o Refresh Token do Cookie (Somente visível nessa rota por causa do path)
    refresh_token_cookie = request.cookies.get("refresh_token")
    
    if not refresh_token_cookie:
        raise HTTPException(status_code=401, detail="Refresh token ausente")

    # 2. Verifica no Banco
    token_hash = get_token_hash(refresh_token_cookie)
    
    db_token = db.query(UserRefreshToken).filter(UserRefreshToken.token_hash == token_hash).first()
    
    # 3. Validações de Segurança
    if not db_token:
        # Cenário: Token forjado ou não existe
        raise HTTPException(status_code=401, detail="Token inválido")
    
    if db_token.is_revoked:
        # CENÁRIO DE ROUBO DE SESSÃO (REUSE DETECTION)
        # Se alguém tentou usar um token que já foi 'gasto', é um ataque.
        # Ação recomendada: Revogar TODOS os tokens desse usuário (Logout forçado em todos os devices)
        # Por enquanto, vamos apenas bloquear esse request.
        raise HTTPException(status_code=401, detail="Token revogado (Sessão inválida)")

    if db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Token expirado. Faça login novamente.")

    # 4. ROTAÇÃO: Queima o token antigo
    db_token.is_revoked = True
    db.add(db_token) # Prepara o update
    
    # 5. Gera novos tokens (Renovando a validade - Sliding Expiration)
    # Precisamos do usuário para gerar o novo token
    user = db_token.usuario
    
    new_access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    
    # 6. Salva o NOVO Refresh Token no banco
    new_refresh_hash = get_token_hash(new_refresh_token)
    new_expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    new_db_token = UserRefreshToken(
        token_hash=new_refresh_hash,
        usuario_id=user.id,
        expires_at=new_expires_at,
        is_revoked=False,
        user_agent=request.headers.get("User-Agent")
    )
    db.add(new_db_token)
    db.commit() # Salva tudo (Revogação do velho + Criação do novo)
    
    # 7. Atualiza os Cookies
    response.set_cookie(
        key="access_token",
        value=f"Bearer {new_access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        expires=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
        path="/auth/refresh", # Importante manter o path restrito
        secure=False
    )
    
    return {"message": "Token renovado com sucesso"}



# [ROUTE] /logout 
@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    # 1. Tenta pegar o refresh token para invalidá-lo no banco
    refresh_token_cookie = request.cookies.get("refresh_token")
    
    if refresh_token_cookie:
        token_hash = get_token_hash(refresh_token_cookie)
        db_token = db.query(UserRefreshToken).filter(UserRefreshToken.token_hash == token_hash).first()
        
        # Se achou o token, revoga ele (mata a sessão no servidor)
        if db_token:
            db_token.is_revoked = True
            db.add(db_token)
            db.commit()
    
    # 2. Limpa os cookies no navegador (Client-side)
    response.delete_cookie("access_token")
    
    # ATENÇÃO: Para deletar cookie com path específico, tem que informar o path de novo!
    response.delete_cookie("refresh_token", path="/auth/refresh")
    
    return {"message": "Logout realizado com sucesso. Sessão encerrada."}


# [ROUTE] /me 
@router.get("/me", response_model=UsuarioResponse)
def get_me(current_user: Usuario = Depends(get_current_user)):
    return current_user