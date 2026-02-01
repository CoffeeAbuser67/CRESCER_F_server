from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Banco de Dados (Obrigatório vir do .env)
    DATABASE_URL: str

    # Autenticação (Padrões definidos, mas idealmente sobrescreva no .env)
    SECRET_KEY: str = "sua_chave_secreta_aqui"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()