from sqlalchemy import text
from db.config import get_db_engine, db_config
from tabulate import tabulate
import pandas as pd

engine = get_db_engine(db_config)

def fetch_table_data(table_name):
    """Fetch all data from the specified table and return it as a DataFrame.
        
        table : select * from table_name
    """
    try:
        query = f"SELECT * FROM {table_name};"
        df = pd.read_sql(query, engine)
        print("select * from", table_name)
        print("Data fetched successfully:")
        return df
    except Exception as e:
        print(tabulate([[f"Error fetching data from table {table_name}: {e}"]], tablefmt="psql"))
        return None
    




def queries_dicts_type(join_type):
    """
    Retorna os resultados de uma consulta SQL predefinida (usando diferentes tipos de JOINs) 
    aplicada a um esquema 'academico', executando a consulta e retornando os dados como 
    um DataFrame do Pandas.

    O tipo de JOIN é selecionado pela chave de entrada.

    Parâmetros:
        join_type (str): O tipo de JOIN a ser executado. Deve ser 'inner', 'left' ou 'right'.

    Returns:
        pd.DataFrame ou None: Um DataFrame contendo os resultados da consulta SQL, 
                               ou None se ocorrer um erro.
    """
    
    # ⚠️ IMPORTANTE: A função 'text' deve estar definida (importada do SQLAlchemy)
    # ⚠️ A variável 'engine' (conexão com o banco de dados) deve estar definida e ativa.
    
    # Definição das consultas SQL
    queries = {
       
        "inner": text("""
            SELECT a.nome_completo AS aluno, t.nome_turma AS turma, c.nome AS curso
            FROM academico.inscricao i
            INNER JOIN academico.aluno a ON a.id_aluno = i.xid_aluno
            INNER JOIN academico.turma t ON t.id_turma = i.xid_turma
            INNER JOIN academico.curso c ON c.id_curso = t.xid_curso;
        """),
        "left": text("""
            SELECT c.nome AS curso, t.nome_turma AS turma
            FROM academico.curso c
            LEFT JOIN academico.turma t ON t.xid_curso = c.id_curso;
        """),
        "right": text("""
            -- RIGHT JOIN: todos os alunos mesmo sem inscrição
            SELECT a.nome_completo AS aluno, t.nome_turma AS turma
            FROM academico.inscricao i
            RIGHT JOIN academico.aluno a ON a.id_aluno = i.xid_aluno
            RIGHT JOIN academico.turma t ON t.id_turma = i.xid_turma;
        """)
        
    }
    
    # Lógica para executar a consulta
    try:
        # 1. Verifica se a chave do JOIN é válida
        if join_type not in queries:
            print(f"Erro: Tipo de JOIN '{join_type}' não encontrado. Use 'inner', 'left' ou 'right'.")
            return None
            
        # 2. Obtém a consulta (objeto text)
        query_text_object = queries[join_type]
        
        # 3. Executa a consulta usando Pandas e o engine definido
        # Nota: pd.read_sql aceita o objeto text do SQLAlchemy diretamente.
        df = pd.read_sql(query_text_object, engine)
        
        print(f"Executando a consulta: {join_type} JOIN")
        print("Dados buscados com sucesso:")
        return df
        
    except NameError as ne:
        print(f"Erro de Variável: {ne}. Certifique-se de que as variáveis 'text', 'pd', 'engine' e 'tabulate' estão definidas (importadas).")
        return None
    except Exception as e:
        # 4. Trata erros na execução da consulta (como problemas de conexão ou SQL inválido)
        # Assumindo que 'tabulate' está definido
        print(tabulate([[f"Erro ao buscar dados com o JOIN '{join_type}': {e}"]], tablefmt="psql"))
        return None

# A função não deve ter um 'return queries' no final da lógica de execução,
# pois o objetivo é retornar o DataFrame (df) ou None.