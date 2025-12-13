import json

from sqlalchemy import Table, Column, Integer, String, Text, SmallInteger, Numeric, MetaData, text, delete, Boolean
from sqlalchemy.dialects.postgresql import insert
import sqlalchemy as sa

# e depois referencie sa.Column, sa.Integer etc

# Importe 'engine' e 'config' se necessário no seu ambiente.
# from config import engine 

# Supondo que 'engine' está definido e configurado

metadata = MetaData(schema="academico")

# Definição das tabelas
curso = Table(
    "curso", metadata,
    sa.Column("id", Integer, primary_key=True),
    sa.Column("nome", String(100), unique=True),
    sa.Column("descricao", Text),
    sa.Column("carga_horaria", SmallInteger),
    sa.Column("preco_padrao", Numeric(10, 2)),
    schema="academico"
)

material = Table(
    "material", metadata,
    sa.Column("id", Integer, primary_key=True),
    sa.Column("nome", String(100), unique=True),
    sa.Column("descricao", Text),
    sa.Column("preco_venda", Numeric(10, 2)),
    sa.Column("estoque_atual", Integer),
    schema="academico"
)

tarefa_escolar = Table(
    "tarefa_escolar", metadata,
    sa.Column("id", Integer, primary_key=True),
    sa.Column("xid_aluno", Integer),
    sa.Column("titulo", String(150)),
    sa.Column("descricao", Text),
    sa.Column("tipo", String(50)),
    sa.Column("progresso_curso", SmallInteger),
    sa.Column("progresso_leitura", SmallInteger),
    sa.Column("data_entrega", String(10)),
    sa.Column("status", String(50)),
    schema="academico"
)

aluno = Table(
    "aluno", metadata,
    sa.Column("id", Integer, primary_key=True),
    sa.Column("nome_completo", String(100)),
    sa.Column("email", String(100), unique=True),
    sa.Column("telefone", String(15)),
    sa.Column("data_nascimento", String(10)),
    sa.Column("status_ativo", Boolean, nullable=False, server_default="true"),
    sa.Column("data_cadastro", String(10)),
    schema="academico"
    
   
)

inscricao = Table(
    "inscricao", metadata,
    sa.Column("id", Integer, primary_key=True),
    sa.Column("xid_aluno", Integer),
    sa.Column("xid_turma", Integer),
    sa.Column("data_inscricao", String(10)),
    schema="academico"
)

venda = Table(
    "venda", metadata,
    sa.Column("id", Integer, primary_key=True),
    sa.Column("xid_aluno", Integer),
    sa.Column("data_venda", String(10)),
    sa.Column("valor_total", Numeric(10, 2)),
    schema="academico"
)

intem_venda = Table(
    "item_venda", metadata,
    sa.Column("id", Integer, primary_key=True),
    sa.Column("xid_venda", Integer),
    sa.Column("xid_material", Integer),
    sa.Column("quantidade", Integer),
    sa.Column("preco_unitario", Numeric(10, 2)),
    schema="academico"
)

pagamento = Table(
    "pagamento", metadata,
    sa.Column("id", Integer, primary_key=True),
    sa.Column("xid_venda", Integer),
    sa.Column("data_pagamento", String(10)),
    sa.Column("valor_pago", Numeric(10, 2)),
    sa.Column("metodo_pagamento", String(50)),
    schema="academico"
)

usuario = Table(
    "usuario", metadata,
    sa.Column("id", Integer, primary_key=True),
    sa.Column("nome", String(50), unique=True),
    sa.Column("email", String(100), unique=True),
    sa.Column("senha", String(255)),
    sa.Column("role", String(50)),
    sa.Column("id_aluno", Integer),
    sa.Column("id_professor", Integer),
    schema="academico"
)

professor = Table(
    "professor", metadata,
    sa.Column("id", Integer, primary_key=True),
    sa.Column("nome", String(100)),
    sa.Column("email", String(100), unique=True),
    sa.Column("telefone", String(15)),
    sa.Column("especialidade", String(100)),
    sa.Column("data_contratacao", String(10)),
    schema="academico"
)

profesor_disciplina = Table(
    "professor_disciplina", metadata,
    sa.Column("id_professor_disciplina", Integer, primary_key=True),
    sa.Column("xid_professor", Integer),
    sa.Column("disciplina", String(100)),
    schema="academico"
)

tarefa_auxiliar = Table(
    "tarefa_auxiliar", metadata,
    sa.Column("id", Integer, primary_key=True),
    sa.Column("xid_tarefa_escolar", Integer),
    sa.Column("descricao", Text),
    schema="academico"
)

funcionario = Table(
    "funcionario", metadata,
    sa.Column("id", Integer, primary_key=True),
    sa.Column("nome", String(100)),
    sa.Column("cargo", String(100)),
    sa.Column("email", String(100), unique=True),
    schema="academico"
    
)

turma = Table(
    "turma", metadata,
    sa.Column("id", Integer, primary_key=True),
    sa.Column("nome_turma", String(100)),
    sa.Column("ano", Integer),
    sa.Column("semestre", SmallInteger),
    sa.Column("horario_inicio", String(5)),
    sa.Column("horario_fim", String(5)),
    sa.Column("id_professor", Integer),
    sa.Column("xid_curso", Integer),
    schema="academico"
)



def load_json(path):
    """Carrega o conteúdo de um arquivo JSON."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def upsert_data(engine, table, data_records, conflict_column):
    """
    Executa uma operação UPSERT (ON CONFLICT DO UPDATE) em uma tabela.
    Executa UPSERT genérico para qualquer tabela.
    Args:
        engine: Objeto de conexão SQLAlchemy Engine.
        table (Table): Objeto de tabela SQLAlchemy (ex: curso, material).
        data_records (list): Lista de dicionários com os dados a serem inseridos/atualizados.
        conflict_column (str): Nome da coluna usada para identificar conflitos (ex: 'nome').
        Remove PK se vier None
        Usa coluna de conflito definida no argumento
    """
    if not data_records:
        print(f"Aviso: Nenhuma linha para processar em '{table.name}'.")
        return

    try:
        with engine.begin() as conn:
            for record in data_records:

                # Remove PK se vier None
                cleaned_record = {
                    col: val for col, val in record.items()
                    if not (col in table.primary_key.columns.keys() and val is None)
                }

                # Mapeia colunas para atualizar (exceto PK e coluna de conflito)
                set_mapping = {
                    col.name: insert(table).excluded.get(col.name)
                    for col in table.columns
                    if not col.primary_key and col.name != conflict_column
                }

                stmt = (
                    insert(table)
                    .values(**cleaned_record)
                    .on_conflict_do_update(
                        index_elements=[conflict_column],
                        set_=set_mapping
                    )
                )

                conn.execute(stmt)

        print(f"✅ UPSERT concluído na tabela '{table.name}'")
    except Exception as e:
        print(f"❌ Erro ao executar UPSERT na tabela '{table.name}': {e}")


def create_aluno_e_usuario(engine, aluno_data, usuario_data):
    """
    Cria um novo aluno e um usuário associado na mesma transação.
    Se o usuário já existir (conflito na coluna 'email'), atualiza os dados do usuário.
    
    Args:
        engine: SQLAlchemy Engine
        aluno_data: dict com dados do aluno (nome_completo, email, telefone, data_nascimento, status_ativo)
        usuario_data: dict com dados do usuário (nome, email, senha, role)
    """
    with engine.begin() as conn:
        
        # Remove id_aluno se estiver presente
        aluno_data = {k: v for k, v in aluno_data.items() if k != "id_aluno"}
        # 1️⃣ Inserir o aluno e pegar o ID gerado
        stmt_aluno = insert(aluno).values(**aluno_data).returning(aluno.c.id_aluno)
        result = conn.execute(stmt_aluno)
        id_aluno = result.scalar()  # pega o id_aluno inserido

        # 2️⃣ Prepara os dados do usuário com o id_aluno correto
        usuario_data = usuario_data.copy()  # evita modificar o dict original
        usuario_data['id_aluno'] = id_aluno

        # 3️⃣ UPSERT do usuário baseado no email
        set_mapping = {
            col.name: insert(usuario).excluded.get(col.name)
            for col in usuario.columns
            if col.primary_key is False and col.name != 'email'
        }

        stmt_usuario = insert(usuario).values(**usuario_data).on_conflict_do_update(
            index_elements=['email'],
            set_=set_mapping
        )

        conn.execute(stmt_usuario)

        return id_aluno  # opcional, retorna o ID do aluno criado







    """
    Cria usuários do tipo Admin ou Professor no banco.
    Atualiza o usuário se já existir (UPSERT baseado no email).

    Args:
        engine: SQLAlchemy Engine
        usuarios_data: lista de dicts com dados dos usuários, cada dict deve ter:
            - nome
            - email
            - senha
            - role ('Admin' ou 'Professor')
            - id_professor (opcional, só se for professor)
    """
    with engine.begin() as conn:
        for udata in usuarios_data:
            # Preparar UPSERT
            set_mapping = {
                col.name: insert(usuario).excluded.get(col.name)
                for col in usuario.columns
                if col.primary_key is False and col.name != 'email'
            }

            stmt = insert(usuario).values(**udata).on_conflict_do_update(
                index_elements=['email'],  # usa email como chave de conflito
                set_=set_mapping
            )

            conn.execute(stmt)

    print(f"✅ {len(usuarios_data)} usuário(s) Admin/Professor criados ou atualizados com sucesso.")








def criar_usuarios_completos(engine, alunos=[], professores=[], funcionarios=[]):
    """
    Cria alunos, professores e funcionários no banco com seus respectivos usuários.

    Args:
        engine: SQLAlchemy Engine
        alunos: lista de dicts com dados do aluno
            - nome_completo, email, telefone, data_nascimento, status_ativo, data_cadastro
        professores: lista de dicts com dados do professor
            - nome, email
        funcionarios: lista de dicts com dados do funcionário
            - nome, email, role ('Admin' ou outro)
    """
    def filtrar_dados_para_tabela(data_dict, tabela):
        """Filtra apenas os campos que existem na tabela"""
        return {k: v for k, v in data_dict.items() if k in tabela.c.keys()}

    with engine.begin() as conn:
        # --- Inserir alunos e usuários ---
        if alunos:
            for a in alunos:
                aluno_data = filtrar_dados_para_tabela({k: v for k, v in a.items() if k != "id_aluno"}, aluno)
                stmt_aluno = insert(aluno).values(**aluno_data).returning(aluno.c.id_aluno)
                id_aluno = conn.execute(stmt_aluno).scalar()
            usuario_data = filtrar_dados_para_tabela({
                "nome": a.get("nome_completo", a["nome"]),
                "email": a["email"],
                "senha": a.get("senha", "senha123"),
                "role": "Aluno",
                "id_aluno": id_aluno,
                "id_professor": None
            }, usuario)

            set_mapping = {col.name: insert(usuario).excluded.get(col.name)
                           for col in usuario.columns if col.primary_key is False and col.name != "email"}
            stmt_usuario = insert(usuario).values(**usuario_data).on_conflict_do_update(
                index_elements=["email"],
                set_=set_mapping
            )
            conn.execute(stmt_usuario)

        # --- Inserir professores e usuários ---
        elif professores:
            for p in professores:
                professor_data = filtrar_dados_para_tabela({k: v for k, v in p.items() if k != "id_professor"}, professor)
                stmt_prof = insert(professor).values(**professor_data).returning(professor.c.id_professor)
                id_prof = conn.execute(stmt_prof).scalar()
            usuario_data = filtrar_dados_para_tabela({
                "nome": p.get("nome_usuario", p["nome"]),
                "email": p["email"],
                "senha": p.get("senha", "senha123"),
                "role": "Professor",
                "id_aluno": None,
                "id_professor": id_prof
            }, usuario)

            set_mapping = {col.name: insert(usuario).excluded.get(col.name)
                           for col in usuario.columns if col.primary_key is False and col.name != "email"}
            stmt_usuario = insert(usuario).values(**usuario_data).on_conflict_do_update(
                index_elements=["email"],
                set_=set_mapping
            )
            conn.execute(stmt_usuario)

        # --- Inserir funcionários/admins ---
        elif funcionarios:
            for f in funcionarios:
                funcionario_data = filtrar_dados_para_tabela({k: v for k, v in f.items() if k != "id_funcionario"}, funcionario)
                stmt_func = insert(funcionario).values(**funcionario_data).returning(funcionario.c.id_funcionario)
                id_func = conn.execute(stmt_func).scalar()

            usuario_data = filtrar_dados_para_tabela({
                "nome": f.get("nome_usuario", f["nome"]),
                "email": f["email"],
                "senha": f.get("senha", "senha123"),
                "role": f.get("role", "Admin"),
                "id_aluno": None,
                "id_professor": None
            }, usuario)
            set_mapping = {col.name: insert(usuario).excluded.get(col.name)
                        for col in usuario.columns if col.primary_key is False and col.name != "email"}
            stmt_usuario = insert(usuario).values(**usuario_data).on_conflict_do_update(
                index_elements=["email"],
                set_=set_mapping
            )
            conn.execute(stmt_usuario)

    print("✅ Todos os usuários (alunos, professores e funcionários/admins) foram criados/atualizados com sucesso.")
