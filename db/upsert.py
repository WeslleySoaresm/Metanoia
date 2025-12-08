import json
from pathlib import Path
from sqlalchemy import Table, Column, Integer, String, Text, SmallInteger, Numeric, MetaData, text, delete
from sqlalchemy.dialects.postgresql import insert
# Importe 'engine' e 'config' se necessário no seu ambiente.
# from config import engine 

# Supondo que 'engine' está definido e configurado

metadata = MetaData(schema="academico")

# Definição das tabelas
curso = Table(
    "curso", metadata,
    Column("id_curso", Integer, primary_key=True),
    Column("nome", String(100), unique=True),
    Column("descricao", Text),
    Column("carga_horaria", SmallInteger),
    Column("preco_padrao", Numeric(10, 2))
)

material = Table(
    "material", metadata,
    Column("id_material", Integer, primary_key=True),
    Column("nome", String(100), unique=True),
    Column("descricao", Text),
    Column("preco_venda", Numeric(10, 2)),
    Column("estoque_atual", Integer)
)

def load_json(path):
    """Carrega o conteúdo de um arquivo JSON."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def upsert_data(engine, table, data_records, conflict_column):
    """
    Executa uma operação UPSERT (ON CONFLICT DO UPDATE) em uma tabela.
    
    Args:
        engine: Objeto de conexão SQLAlchemy Engine.
        table (Table): Objeto de tabela SQLAlchemy (ex: curso, material).
        data_records (list): Lista de dicionários com os dados a serem inseridos/atualizados.
        conflict_column (str): Nome da coluna usada para identificar conflitos (ex: 'nome').
    """
    if not data_records:
        print(f"Aviso: Nenhuma linha para processar em '{table.name}'.")
        return

    # Mapeia as colunas a serem atualizadas, excluindo a chave primária e a coluna de conflito
    set_mapping = {
        col.name: insert(table).excluded.get(col.name)
        for col in table.columns
        if col.primary_key is False and col.name != conflict_column
    }

    try:
        with engine.begin() as conn:
            for r in data_records:
                # Cria a instrução UPSERT
                stmt = insert(table).values(**r).on_conflict_do_update(
                    index_elements=[conflict_column],
                    set_=set_mapping
                )
                conn.execute(stmt)
        print(f"✅ UPSERT concluído para a tabela '{table.name}' usando '{conflict_column}'.")
    except Exception as e:
        print(f"❌ Erro ao executar UPSERT na tabela '{table.name}': {e}")
     
        
