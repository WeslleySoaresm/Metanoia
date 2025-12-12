import json

from sqlalchemy import Table, Column, Integer, String, Text, SmallInteger, Numeric, MetaData, text, delete, Boolean
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

tarefa_escolar = Table(
    "tarefa_escolar", metadata,
    Column("id_tarefa_escolar", Integer, primary_key=True),
    Column("xid_aluno", Integer),
    Column("titulo", String(150)),
    Column("descricao", Text),
    Column("tipo", String(50)),
    Column("progresso_curso", SmallInteger),
    Column("progresso_leitura", SmallInteger),
    Column("data_entrega", String(10)),
    Column("status", String(50))
)

aluno = Table(
    "aluno", metadata,
    Column("id_aluno", Integer, primary_key=True),
    Column("nome_completo", String(100)),
    Column("email", String(100), unique=True),
    Column("telefone", String(15)),
    Column("data_nascimento", String(10)),
    Column("status_ativo", Boolean, nullable=False, server_default="true"),
    Column("data_cadastro", String(10))
    
   
)

inscricao = Table(
    "inscricao", metadata,
    Column("id_inscricao", Integer, primary_key=True),
    Column("xid_aluno", Integer),
    Column("xid_turma", Integer),
    Column("data_inscricao", String(10))
)

venda = Table(
    "venda", metadata,
    Column("id_venda", Integer, primary_key=True),
    Column("xid_aluno", Integer),
    Column("data_venda", String(10)),
    Column("valor_total", Numeric(10, 2))
)

intem_venda = Table(
    "item_venda", metadata,
    Column("id_item_venda", Integer, primary_key=True),
    Column("xid_venda", Integer),
    Column("xid_material", Integer),
    Column("quantidade", Integer),
    Column("preco_unitario", Numeric(10, 2))
)

pagamento = Table(
    "pagamento", metadata,
    Column("id_pagamento", Integer, primary_key=True),
    Column("xid_venda", Integer),
    Column("data_pagamento", String(10)),
    Column("valor_pago", Numeric(10, 2)),
    Column("metodo_pagamento", String(50))
)

usuario = Table(
    "usuario", metadata,
    Column("id_usuario", Integer, primary_key=True),
    Column("nome", String(50), unique=True),
    Column("email", String(100), unique=True),
    Column("senha", String(255)),
    Column("role", String(50)),
    Column("id_aluno", Integer),
    Column("id_professor", Integer)
)

professor = Table(
    "professor", metadata,
    Column("id_professor", Integer, primary_key=True),
    Column("nome", String(100)),
    Column("email", String(100), unique=True)
)

profesor_disciplina = Table(
    "professor_disciplina", metadata,
    Column("id_professor_disciplina", Integer, primary_key=True),
    Column("xid_professor", Integer),
    Column("disciplina", String(100))
)

tarefa_auxiliar = Table(
    "tarefa_auxiliar", metadata,
    Column("id_tarefa_auxiliar", Integer, primary_key=True),
    Column("xid_tarefa_escolar", Integer),
    Column("descricao", Text)
)

funcionario = Table(
    "funcionario", metadata,
    Column("id_funcionario", Integer, primary_key=True),
    Column("nome", String(100)),
    Column("email", String(100), unique=True)
)

turma = Table(
    "turma", metadata,
    Column("id_turma", Integer, primary_key=True),
    Column("nome_turma", String(100)),
    Column("ano", Integer),
    Column("semestre", SmallInteger),
    Column("horario_inicio", String(5)),
    Column("horario_fim", String(5)),
    Column("id_professor", Integer),
    Column("xid_curso", Integer)
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
