from sqlalchemy import text
from tabulate import tabulate
from db.config import create_engine, db_config, get_db_engine

engine = get_db_engine(db_config)


def queries_lists():
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
    return queries


def to_lists(rows):
    return [list(row) for row in rows]


    