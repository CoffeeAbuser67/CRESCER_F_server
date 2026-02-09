import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context



# 1. Adiciona o diretório raiz ao path para conseguir importar 'app'
sys.path.append(os.getcwd())

# 2. Importa configs e models
from app.config.settings import settings  # Para pegar a URL segura
from app.database import Base             # Para pegar o Metadata


# MODELS: 
from app.modules.usuarios.models import Usuario, UserRefreshToken
from app.modules.financeiro.models import Paciente, Profissional, Servico, Lancamento

# ------------------------------------------------------------------

# Objeto de configuração do Alembic
config = context.config

# Sobrescreve a URL do alembic.ini com a URL do seu settings.py (ENV)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Configura o Log
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata



def run_migrations_offline() -> None:
    """Roda as migrações no modo 'offline'.
    
    Isso configura o contexto apenas com a URL.
    Não precisamos de uma Engine (conexão real) aqui.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Roda as migrações no modo 'online'.
    
    Neste cenário, criamos uma Engine e conectamos de verdade ao banco.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# O ponto de entrada que decide qual modo usar
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()