


from sqlalchemy import text
from tabulate import tabulate
from db.config import create_engine, db_config, get_db_engine

engine = get_db_engine(db_config)


def queries_select():
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
"""
    queries = {
        "Selects": text("""SELECT 'aluno' AS tabela, COUNT(*) FROM academico.aluno
                        UNION ALL SELECT 'curso', COUNT(*) FROM academico.curso
                        UNION ALL SELECT 'turma', COUNT(*) FROM academico.turma
                        UNION ALL SELECT 'inscricao', COUNT(*) FROM academico.inscricao
                        UNION ALL SELECT 'material', COUNT(*) FROM academico.material
                        UNION ALL SELECT 'venda', COUNT(*) FROM academico.venda
                        UNION ALL SELECT 'item_venda', COUNT(*) FROM academico.item_venda
                        UNION ALL SELECT 'pagamento', COUNT(*) FROM academico.pagamento;
                        """)
    }
    return queries


def to_lists(rows):
    return [list(row) for row in rows]

