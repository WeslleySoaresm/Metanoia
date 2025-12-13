"""
Arquivo principal do Alembic.

Responsável por:
- Conectar no banco
- Comparar o estado atual do banco com o metadata do projeto
- Executar migrations (upgrade/downgrade)
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Importa o metadata do seu projeto
# Aqui estão definidas TODAS as tabelas (Table, Column, etc.)
from db.upsert import metadata

# Configuração do Alembic (lê alembic.ini)
config = context.config

# Configura logging (opcional, mas recomendado)
fileConfig(config.config_file_name)

# Diz ao Alembic qual metadata ele deve observar
# IMPORTANTE: como você usa SQLAlchemy Core, isso substitui Base.metadata
target_metadata = metadata


def run_migrations_offline():
    """
    Executa migrations em modo OFFLINE.

    Usado quando:
    - Você quer gerar SQL sem se conectar ao banco
    - Exemplo: alembic upgrade head --sql
    """
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,  # substitui parâmetros pelos valores reais
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    Executa migrations em modo ONLINE.

    Usado normalmente:
    - Conecta de fato no banco
    - Executa ALTER TABLE, CREATE, DROP, etc.
    """

    # Cria a engine a partir do alembic.ini
    configuration = config.get_section(config.config_ini_section)
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # Abre conexão real com o banco
    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=metadata,
            version_table_schema="academico",   # faz o Alembic usar esse schema para versionamento
            include_schemas=True                 # importante para incluir outros schemas
        )       

        with context.begin_transaction():
            context.run_migrations()


# Decide automaticamente qual modo usar
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
