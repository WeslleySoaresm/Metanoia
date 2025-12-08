import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from tabulate import tabulate
from db.config import *
from run_queries_dicts import queries_dicts
from run_queries_lists import queries_lists, to_lists
from run_queries_from import fetch_table_data, queries_dicts_type, select_all_from
import json



#conectando ao banco de dados
engine = get_db_engine(db_config)

# Executando consultas e exibindo resultados

"""#consultas como dicionários
queries_dicts = queries_dicts()
with engine.connect() as conn:
        for label, q in queries_dicts.items():
            result = conn.execute(q)
            rows = result.fetchall()
            keys = result.keys()
            dicts = [dict(zip(keys, row)) for row in rows]
            print(f"\n=== {label.upper()} JOIN (dicionários) ===")
            print(tabulate(dicts, headers="keys", tablefmt="psql"))"""
           
"""#consultas como listas
queries_lists = queries_lists()
with engine.connect() as conn:
        for label, q in queries_lists.items():
            result = conn.execute(q)
            rows = result.fetchall()
            lists = to_lists(rows)
            print(f"\n=== {label.upper()} JOIN (listas) ===")
            print(tabulate(lists, headers=["Aluno", "Curso", "Turma"], tablefmt="psql"))

#consultas SELECT e UNION ALL
queries_select = queries_select()
with engine.connect() as conn:
        for label, q in queries_select.items():
            result = conn.execute(q)
            rows = result.fetchall()
            lists = to_lists(rows)
            print(f"\n=== {label.upper()} CONTAGEM ===")
            print(tabulate(lists, headers=["Tabela", "Contagem"], tablefmt="psql"))"""
            
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