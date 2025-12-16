from sqlalchemy import text
from db.config import get_db_engine, db_config
from tabulate import tabulate
import pandas as pd

engine = get_db_engine(db_config)

# Função para buscar dados de uma tabela específica
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
# Função para consultas SELECT e UNION ALL
def select_all_from():
    """
        Documentação e Análise da Consulta SQL (SELECT e UNION ALL).

        Este documento descreve e analisa a função `queries_select()`, que retorna 
        um dicionário contendo uma única consulta SQL complexa, utilizando a função 
        `text()` (presumivelmente do SQLAlchemy) e aplicada ao esquema de banco de dados 
        'academico'. A consulta é projetada para realizar uma contagem de linhas (ROW COUNT) 
        em múltiplas tabelas.

        Parâmetros:
            Nenhum. A função não aceita argumentos.

        Retorna:
            dict: Um dicionário contendo a chave "Selects", cujo valor é um objeto 
                de consulta SQL.

        Detalhes da Análise da Consulta "Selects":
            - Objetivo: Fornecer um relatório de auditoria e saúde do banco de dados, 
            listando o nome da tabela e o número total de registros (linhas) contidos nela.
            
            - Cláusulas Utilizadas:
                - SELECT: Usada para contar os registros de cada tabela (`COUNT(*)`) 
                e definir o nome da tabela como uma string literal (ex: 'aluno') 
                na coluna 'tabela'.
                - UNION ALL: Combina os resultados de cada instrução SELECT individual 
                (uma para cada tabela) em um único conjunto de resultados. O uso de 
                UNION ALL é mais eficiente do que o UNION, pois evita a remoção 
                desnecessária de duplicatas.

            - Tabelas Contadas: A consulta abrange as seguintes tabelas do esquema 'academico':
                - aluno
                - curso
                - turma
                - inscricao
                - material
                - venda
                - item_venda
                - pagamento
                - usuario
                - tarefa_escolar
                - curso_aluno       
            
"""
    try:
        query = f"""SELECT 'aluno' AS tabela, COUNT(*) FROM academico.aluno
                        UNION ALL SELECT 'curso', COUNT(*) FROM academico.curso
                        UNION ALL SELECT 'turma', COUNT(*) FROM academico.turma
                        UNION ALL SELECT 'inscricao', COUNT(*) FROM academico.inscricao
                        UNION ALL SELECT 'material', COUNT(*) FROM academico.material
                        UNION ALL SELECT 'venda', COUNT(*) FROM academico.venda
                        UNION ALL SELECT 'item_venda', COUNT(*) FROM academico.item_venda
                        UNION ALL SELECT 'pagamento', COUNT(*) FROM academico.pagamento;
                        union all select 'usuario', count(*) from academico.usuario;
                        union all select 'tarefa_escolar', count(*) from academico.tarefa_escolar;
                        union all select 'curso_aluno', count(*) from academico.curso_aluno;
                        union all select 'material', count(*) from academico.material;  
                        union all select 'professor', count(*) from academico.professor;
                        union all select 'funcionario', count(*) from academico.funcionario;
                        union all select 'professor_disciplina', count(*) from academico.professor_disciplina;
                        union all select 'tarefa_auxiliar', count(*) from academico.tarefa_auxiliar;
                        union all select 'turma', count(*) from academico.turma;
                        
                        
                        
                        """
        df = pd.read_sql(query, engine)
        print("select * from")
        print("Data fetched successfully:")
        return df
    except Exception as e:
        print(tabulate([[f"Error fetching data from table {table_name}: {e}"]], tablefmt="psql"))
        return 

# Função para consultas com diferentes tipos de JOIN em dicionários
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
    return execute_join_query(queries, join_type, engine)

# Função para consultas com diferentes tipos de JOIN em listas
def queries_lists(type_join):
    """
        Documentação e Análise das Consultas SQL (INNER, LEFT, RIGHT JOIN).

        Este documento descreve e analisa a função `queries_lists()`, que retorna 
        um dicionário de consultas SQL predefinidas, utilizando a função `text()` 
        (presumivelmente do SQLAlchemy) e aplicadas a um esquema de banco de dados 
        'academico'. Cada consulta é projetada para demonstrar um tipo específico 
        de JOIN.

        Parâmetros:
            Nenhum. A função não aceita argumentos.

        Retorna:
            dict: Um dicionário contendo três pares chave-valor:
                - "inner": Consulta SQL usando INNER JOIN.
                - "left": Consulta SQL usando LEFT JOIN com COALESCE.
                - "right": Consulta SQL usando RIGHT JOIN.

        Detalhes da Análise das Consultas:
            - INNER JOIN ("inner"): Garante que apenas registros com correspondência em
            TODAS as tabelas ('inscricao', 'aluno', 'turma', 'curso') sejam retornados, 
            listando inscrições válidas.

            - LEFT JOIN ("left"): Garante que TODOS os registros da tabela da esquerda 
            ('academico.material') sejam incluídos. Utiliza a função SQL COALESCE 
            para substituir NULL por 0 na coluna de quantidade ('qtd_vendida') 
            para materiais que não foram vendidos.

            - RIGHT JOIN ("right"): Garante que TODOS os registros da tabela da direita 
            ('academico.aluno') sejam incluídos, listando todos os alunos e seus 
            respectivos status de pagamento (que podem ser NULL).
"""
    queries = {
        "inner": text("""
            SELECT a.nome_completo AS aluno, c.nome AS curso, t.nome_turma AS turma
            FROM academico.inscricao i
            INNER JOIN academico.aluno a ON a.id_aluno = i.xid_aluno
            INNER JOIN academico.turma t ON t.id_turma = i.xid_turma
            INNER JOIN academico.curso c ON c.id_curso = t.xid_curso;
        """),
        "left": text("""
            SELECT m.nome AS material, COALESCE(iv.quantidade, 0) AS qtd_vendida
            FROM academico.material m
            LEFT JOIN academico.item_venda iv ON iv.xid_material = m.id_material;
        """),
        "right": text("""
            SELECT a.nome_completo, p.status, p.valor
            FROM academico.pagamento p
            RIGHT JOIN academico.aluno a ON a.id_aluno = p.xid_aluno;
        """)
    }
    return execute_join_query(queries, type_join, engine)
        
# Função auxiliar para executar consultas de JOIN
def execute_join_query(queries, join_type, engine):
    """
    Executa uma consulta SQL específica a partir de um dicionário de consultas.

    Verifica se o tipo de JOIN é válido no dicionário fornecido e tenta executar 
    a consulta usando o Pandas e o engine de conexão.

    Args:
        queries (dict): Dicionário onde as chaves são tipos de JOIN (ex: 'inner') 
                        e os valores são objetos de consulta SQL (ex: text(...)).
        join_type (str): A chave (tipo de JOIN) da consulta a ser executada.
        engine (Engine): O objeto de conexão do SQLAlchemy para o banco de dados.

    Returns:
        pd.DataFrame ou None: Um DataFrame com os resultados da consulta, ou None 
                               se ocorrer um erro (chave inválida, problema de conexão, etc.).
    """
    try:
        # 1. Verifica se a chave do JOIN é válida
        if join_type not in queries:
            print(f"Erro: Tipo de JOIN '{join_type}' não encontrado. Use uma das chaves do dicionário.")
            return None
            
        # 2. Obtém a consulta (objeto text)
        query_text_object = queries[join_type]
        
        # 3. Executa a consulta usando Pandas e o engine definido
        df = pd.read_sql(query_text_object, engine)
        
        print(f"Executando a consulta: {join_type} JOIN")
        print("Dados buscados com sucesso:")
        return df
        
    except NameError as ne:
        print(f"Erro de Variável: {ne}. Verifique se 'pd', 'engine' e 'tabulate' estão acessíveis ou definidos.")
        return None
    except Exception as e:
        # 4. Trata erros gerais de execução (SQL, conexão)
        # Assumindo que 'tabulate' está definido e importado
        # Se 'tabulate' não estiver disponível, substitua por: print(f"Erro: {e}")
        try:
            print(tabulate([[f"Erro ao buscar dados com o JOIN '{join_type}': {e}"]], tablefmt="psql"))
        except NameError:
             print(f"Erro ao buscar dados com o JOIN '{join_type}': {e}")
        return None
    
    
    
def upsert_table_data(table_name, data):
    """Upsert data into the specified table.
        
        table : upsert into table_name
        data : list of dictionaries representing rows to be upserted
    """
    try:
        df = pd.DataFrame(data)
        df.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"Data upserted successfully into table {table_name}.")
    except Exception as e:
        print(tabulate([[f"Error upserting data into table {table_name}: {e}"]], tablefmt="psql"))
               
        
        
def deletar_aluno_e_dependencias(engine, ids_alunos: list):
    """
    Deleta alunos e suas dependências (venda, pagamento, inscrição, etc.) na ordem correta, 
    garantindo a integridade referencial.
    """
    
    # --- Passo Pré-Exclusão: Encontrar IDs de Vendas (NECESSÁRIO para deletar item_venda) ---
    # É necessário obter os IDs das vendas que pertencem aos alunos antes de deletá-las
    sql_select_venda_ids = text("SELECT id_venda FROM academico.venda WHERE xid_aluno = ANY(:ids);")
    
    # --- Funções de Exclusão (Da ponta para a raiz) ---
    
    # 1. DELETE: Tabela 'item_venda' (Neto)
    # ATENÇÃO: Esta exclusão usa a lista de id_venda, não o id_aluno diretamente!
    sql_delete_item_venda = text("DELETE FROM academico.item_venda WHERE xid_venda = ANY(:venda_ids);")
    
    # 2. DELETE: Tabela 'pagamento'
    sql_delete_pagamento = text("DELETE FROM academico.pagamento WHERE xid_aluno = ANY(:ids);")
    
    # 3. DELETE: Tabela 'inscricao'
    sql_delete_inscricao = text("DELETE FROM academico.inscricao WHERE xid_aluno = ANY(:ids);")
    
    # 4. DELETE: Tabela 'curso_aluno'
    sql_delete_curso_aluno = text("DELETE FROM academico.curso_aluno WHERE xid_aluno = ANY(:ids);")
    
    # 5. DELETE: Tabela 'venda' (Pai de item_venda)
    sql_delete_venda = text("DELETE FROM academico.venda WHERE xid_aluno = ANY(:ids);")
    
    # 6. DELETE: Tabela 'aluno' (O Pai principal)
    sql_delete_aluno = text("DELETE FROM academico.aluno WHERE id_aluno = ANY(:ids);")
    
    # NOVO DELETE: Tabela 'tarefa_escolar'
    sql_delete_tarefa = text("DELETE FROM academico.tarefa_escolar WHERE xid_aluno = ANY(:ids);")

    try:
        with engine.begin() as conn:
            
            # A) Obter IDs das vendas associadas
            venda_ids_result = conn.execute(sql_select_venda_ids, {"ids": ids_alunos}).scalars().all()
            
            if venda_ids_result:
                # B) Excluir itens de venda antes de excluir as vendas
                conn.execute(sql_delete_item_venda, {"venda_ids": venda_ids_result})
            
            # C) Excluir as outras dependências na ordem correta
            conn.execute(sql_delete_pagamento, {"ids": ids_alunos})
            conn.execute(sql_delete_inscricao, {"ids": ids_alunos})
            conn.execute(sql_delete_curso_aluno, {"ids": ids_alunos})
            
            # D) Excluir as vendas (agora que item_venda está limpa)
            conn.execute(sql_delete_venda, {"ids": ids_alunos})
            conn.execute(sql_delete_tarefa, {"ids": ids_alunos})
            
            # E) Excluir o aluno (agora que todas as dependências foram removidas)
            result_a = conn.execute(sql_delete_aluno, {"ids": ids_alunos})
            
            if not result_a.rowcount:
                print("⚠️ Aviso: Nenhum aluno foi deletado. Verifique os IDs fornecidos.")
            else:  
                print("--- Exclusão de Alunos Concluída ---")
                print(f"✅ Total de alunos deletados: {result_a.rowcount} linhas.")

    except Exception as e:
        print(f"❌ ERRO GRAVE. Transação desfeita (ROLLBACK): {e}")
        
        
def consulta_inner_join(engine):
    sql = """
        SELECT 
            a.id AS aluno_id,
            a.nome_completo,
            t.nome_turma,
            t.ano,
            t.semestre
        FROM academico.aluno a
        INNER JOIN academico.inscricao i ON i.xid_aluno = a.id
        INNER JOIN academico.turma t ON t.id = i.xid_turma;
    """
    with engine.connect() as conn:
        return conn.execute(text(sql)).fetchall()       
    
    
    



def buscar_tarefas_por_aluno(id_aluno: int):
    query = """
        SELECT id, titulo, descricao, status
        FROM academico.tarefa_escolar
        WHERE xid_aluno = :id_aluno
        ORDER BY id DESC
    """

    with engine.connect() as conn:
        result = conn.execute(text(query), {"id_aluno": id_aluno}).fetchall()

    return [
        {
            "id": r[0],
            "titulo": r[1],
            "descricao": r[2],
            "status": r[3]
        }
        for r in result
    ]