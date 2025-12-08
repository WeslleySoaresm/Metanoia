from anyio import Path
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from tabulate import tabulate
from db.config import *
from db.run_queries import deletar_aluno_e_dependencias, fetch_table_data, queries_dicts_type, select_all_from, execute_join_query
import json

from db.upsert import *



#conectando ao banco de dados
engine = get_db_engine(db_config)

print("=== CONSULTAS DAS TABELAS (DataFrame) ===")
            
#consultas para buscar dados das tabelas
print(tabulate(fetch_table_data('academico.aluno'), headers="keys", tablefmt="psql"))  # nome da tabela a ser buscada
print(tabulate(fetch_table_data('academico.curso'), headers="keys", tablefmt="psql"))  # nome da tabela a ser buscada
print(tabulate(fetch_table_data('academico.turma'), headers="keys", tablefmt="psql"))  # nome da tabela a ser buscada
print(tabulate(fetch_table_data('academico.inscricao'), headers="keys", tablefmt="psql"))  # nome da tabela a ser buscada
print(tabulate(fetch_table_data('academico.material'), headers="keys", tablefmt="psql"))  # nome da tabela a ser buscada
print(tabulate(fetch_table_data('academico.venda'), headers="keys", tablefmt="psql"))  # nome da tabela a ser buscada
print(tabulate(fetch_table_data('academico.item_venda'), headers="keys", tablefmt="psql"))  # nome da tabela a ser buscada
print(tabulate(fetch_table_data('academico.pagamento'), headers="keys", tablefmt="psql"))  # nome da tabela a ser buscada

#consultas com diferentes tipos de JOIN
print("\n=== CONSULTAS COM DIFERENTES TIPOS DE JOIN (DataFrame) ===")

df_inner = queries_dicts_type('inner')
print("\n--- INNER JOIN ---")
print(tabulate(df_inner, headers="keys", tablefmt="psql"))

df_left = queries_dicts_type('left')
print("\n--- LEFT JOIN ---")
print(tabulate(df_left, headers="keys", tablefmt="psql"))

df_right = queries_dicts_type('right')
print("\n--- RIGHT JOIN ---")
print(tabulate(df_right, headers="keys", tablefmt="psql"))


#consultas SELECT e UNION ALL
df_select = select_all_from()
print("\n--- SELECT ALL FROM ---")
print(tabulate(df_select, headers="keys", tablefmt="psql"))


# --- 1. Preparação dos Dados ---
base = Path(__file__).parent.parent / "json"
    
    # Carrega dados dos arquivos JSON
try:
        cursos = load_json(base / "/Users/weslleysoares/Metanoia/curso_upsert.json")
        materiais = load_json(base / "/Users/weslleysoares/Metanoia/material_upsert.json")
        delete = load_json(base / "/Users/weslleysoares/Metanoia/material_delete.json")
except FileNotFoundError as e:
        print(f"Erro: Arquivo JSON não encontrado. Verifique o caminho. {e}")
        exit()
except Exception as e:
        print(f"Erro ao carregar JSON: {e}")
        exit()

    # --- 2. Execução dos UPSERTs ---
    
    # Executa o UPSERT para Cursos, usando 'nome' como coluna de conflito.
upsert_data(engine, curso, cursos, "nome")
    
    # Executa o UPSERT para Materiais, usando 'nome' como coluna de conflito.
upsert_data(engine, material, materiais, "nome")

    # --- 3. Execução dos DELETEs ---

Alunos = fetch_table_data('academico.aluno')
print("\n=== Tabela Aluno Antes da Exclusão ===")
print(tabulate(Alunos, headers="keys", tablefmt="psql"))    
lista_ids_de_alunos = input(f"Digite o Ids dos alunos a serem deletados, separados por vírgula: ") # IDs dos alunos a serem deletados    
lista_ids_de_alunos = [int(id.strip()) for id in lista_ids_de_alunos.split(",")] # Converte a entrada em uma lista de inteiros
deletar_aluno_e_dependencias(engine, lista_ids_de_alunos)