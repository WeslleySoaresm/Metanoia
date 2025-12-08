from sqlalchemy import text
from tabulate import tabulate
from db.config import create_engine, db_config, get_db_engine

engine = get_db_engine(db_config)


def queries_dicts():
    """
    Retorna um dicionário contendo consultas SQL predefinidas (usando SQLAlchemy text) 
    com diferentes tipos de JOINs (INNER, LEFT, RIGHT) aplicadas a um esquema 'academico'.

    As chaves do dicionário ("inner", "left", "right") indicam o tipo de JOIN primário 
    demonstrado na respectiva consulta. Cada consulta ilustra como diferentes tipos de JOINs afetam os resultados
    ao combinar dados de várias tabelas relacionadas: academico.aluno, academico.curso, academico.turma e academico.inscricao.
    
    Detalhes das consultas:
    
    (INNER JOIN)
                Consulta: Busca o nome completo do aluno, o nome da turma e o nome do curso.
                Comportamento do JOIN: O INNER JOIN só retorna registros quando há correspondência em todas as tabelas envolvidas:
                Um registro de inscricao (inscrição) deve corresponder a um aluno, uma turma e, por sua vez, a turma deve corresponder a um curso.
                Resultado: Apenas alunos que estão efetivamente inscritos em uma turma e essa turma está associada a um curso.
   
    (LEFT JOIN)
                Consulta: Busca o nome do curso e o nome da turma associada.
                Comportamento do JOIN: O LEFT JOIN (ou LEFT OUTER JOIN) garante que todos os registros da tabela esquerda (academico.curso neste caso) sejam incluídos no resultado.
                Se um curso tem uma turma correspondente, ambos são retornados.
                Se um curso não tiver nenhuma turma associada, o nome do curso será retornado, mas a coluna da turma (t.nome_turma) será preenchida com NULL.
                Resultado: Todos os cursos, listando suas turmas se existirem, ou NULL caso contrário.
    
    (RIGHT JOIN)
                Consulta: Busca o nome completo do aluno e o nome da turma.
                Comportamento do JOIN: O RIGHT JOIN (ou RIGHT OUTER JOIN) garante que todos os registros das tabelas à direita (principalmente academico.aluno e academico.turma no segundo e terceiro joins) sejam incluídos no resultado.
                O comentário no código sugere: "-- RIGHT JOIN: todos os alunos mesmo sem inscrição".
                Consulta 1 (RIGHT JOIN academico.aluno): Garante que todos os alunos (academico.aluno) sejam incluídos, mesmo que não estejam na tabela academico.inscricao.
                Consulta 2 (RIGHT JOIN academico.turma): Garante que todas as turmas (academico.turma) sejam incluídas, mesmo que não haja alunos ou inscrições correspondentes.
                Resultado: Uma lista abrangente de alunos e turmas. Os alunos aparecem mesmo sem inscrição; as turmas aparecem mesmo sem alunos inscritos (os campos correspondentes da tabela 'esquerda' – i ou a – serão NULL).
                Resultado: Todos os cursos, listando suas turmas se existirem, ou NULL caso contrário.
        
    Returns:
        dict: Um dicionário onde as chaves são nomes de tipos de JOIN e os valores 
              são objetos de consulta SQL (usando a função 'text').
    """

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
    
    return queries

def to_dicts(rows, keys):
    return [dict(zip(keys, row)) for row in rows]
