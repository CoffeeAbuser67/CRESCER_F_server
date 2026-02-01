from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "sua_chave_secreta"
    ALGORITHM: str = "HS256"
    
    # Access Token CURTO (Segurança)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1
    
    # Refresh Token LONGO (Conveniência)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7 

    class Config:
        env_file = ".env"

settings = Settings()
