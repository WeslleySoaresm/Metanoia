import json
# importe utils de senha
from utils.security import is_probably_bcrypt_hash, hash_password
from sqlalchemy import Table, Column, Integer, String, Text, SmallInteger, Numeric, MetaData, text, delete, Boolean
from sqlalchemy.dialects.postgresql import insert
import sqlalchemy as sa
from datetime import datetime, date

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


def upsert_data(engine, schema_table, rows, pk_field="id", conflict_target="email"):
    """
    Upsert rows into schema.table.
    - schema_table: tuple (schema, table_name) or SQLAlchemy Table-like with .name/.schema
    - rows: list[dict]
    - pk_field: primary key field name (default "id")
    - conflict_target: unique column to use when id not provided (default "email")
    Returns: mapping { email: id }
    """
    if not rows:
        return {}

    # resolve table name and schema
    if hasattr(schema_table, "name"):
        table_name = schema_table.name
        schema = getattr(schema_table, "schema", None) or "academico"
    else:
        schema, table_name = schema_table

    full_table = f"{schema}.{table_name}"
    mapping = {}

    with engine.begin() as conn:
        for row in rows:
            payload = {k: v for k, v in row.items() if v is not None}  # omit None values
            email = payload.get("email")
            provided_id = row.get(pk_field)

            # Build insert columns/values from payload keys (already filtered)
            insert_keys = list(payload.keys())
            insert_cols = ", ".join(insert_keys)
            insert_vals = ", ".join(":" + k for k in insert_keys)

            if provided_id:
                # ensure pk_field present in payload
                if pk_field not in insert_keys:
                    insert_keys.append(pk_field)
                    insert_cols = ", ".join(insert_keys)
                    insert_vals = ", ".join(":" + k for k in insert_keys)
                    payload[pk_field] = provided_id

                set_clause = ", ".join(f"{k}=excluded.{k}" for k in insert_keys if k != pk_field)
                sql = text(f"""
                    INSERT INTO {full_table} ({insert_cols})
                    VALUES ({insert_vals})
                    ON CONFLICT ({pk_field}) DO UPDATE
                    SET {set_clause}
                    RETURNING {pk_field}
                """)
                res = conn.execute(sql, payload).scalar_one()
                mapping[email] = res
            else:
                # id not provided: conflict on unique column (email)
                set_clause = ", ".join(f"{k}=excluded.{k}" for k in insert_keys if k != conflict_target)
                sql = text(f"""
                    INSERT INTO {full_table} ({insert_cols})
                    VALUES ({insert_vals})
                    ON CONFLICT ({conflict_target}) DO UPDATE
                    SET {set_clause}
                    RETURNING {pk_field}
                """)
                res = conn.execute(sql, payload).scalar_one()
                mapping[email] = res

    return mapping



def converter_data_para_iso(data_str, formato_entrada="%d/%m/%Y"):
    if not data_str or data_str.strip() == "":
        return None
    try:
        data_obj = datetime.strptime(data_str.strip(), formato_entrada)
        return data_obj.strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Formato de data inválido: {data_str}. Use DD/MM/YYYY")

def create_aluno_e_usuario(engine, aluno_data, usuario_data, auto_hash: bool = False):
    """
    Cria aluno e usuário na mesma transação.
    - Por padrão exige que usuario_data['senha'] seja um hash bcrypt.
    - Se auto_hash=True, aceita senha em texto e gera o hash (uso apenas para migração controlada).
    """
    if "senha" not in usuario_data or not usuario_data["senha"]:
        raise ValueError("usuario_data deve conter a chave 'senha' não vazia")

    # Se auto_hash ativado, gere hash se necessário
    if auto_hash:
        if not is_probably_bcrypt_hash(usuario_data["senha"]):
            usuario_data = usuario_data.copy()
            usuario_data["senha"] = hash_password(usuario_data["senha"])
    else:
        # modo seguro: exigir hash já gerado
        if not is_probably_bcrypt_hash(usuario_data["senha"]):
            raise ValueError("create_aluno_e_usuario espera senha já hasheada com bcrypt. Use auto_hash=True apenas para migração.")

    with engine.begin() as conn:
        # Remove id se presente
        aluno_data = {k: v for k, v in aluno_data.items() if k != "id"}

        # Converter datas
        if "data_nascimento" in aluno_data:
            aluno_data["data_nascimento"] = converter_data_para_iso(aluno_data["data_nascimento"])
        if "data_cadastro" in aluno_data:
            aluno_data["data_cadastro"] = converter_data_para_iso(aluno_data["data_cadastro"])

        # Inserir aluno
        stmt_aluno = insert(aluno).values(**aluno_data).returning(aluno.c.id)
        result = conn.execute(stmt_aluno)
        id_aluno = result.scalar()

        # Preparar usuario
        usuario_payload = usuario_data.copy()
        usuario_payload["id_aluno"] = id_aluno

        # Construir set_mapping para upsert
        set_mapping = {
            col.name: insert(usuario).excluded.get(col.name)
            for col in usuario.columns
            if col.primary_key is False and col.name != 'email'
        }

        stmt_usuario = insert(usuario).values(**usuario_payload).on_conflict_do_update(
            index_elements=['email'],
            set_=set_mapping
        )

        conn.execute(stmt_usuario)
        return id_aluno



def parse_date_br(value):
    """
    Converte datas no formato 'DD/MM/AAAA' para datetime.date.
    Retorna None se a string estiver vazia, inválida ou None.
    """
   
    if isinstance(value, date):
        return value

        if not value or not isinstance(value, str):
            return None

        value = value.strip()

        try:
            if "-" in value and len(value.split("-")[0]) == 4:
                return datetime.strptime(value, "%Y-%m-%d").date()
        except:
            pass

        try:
            return datetime.strptime(value, "%d/%m/%Y").date()
        except:
            return None

def criar_usuarios_completos(engine, usuario_payload, alunos_map=None, professores_map=None, funcionarios_map=None):
    """
    Insere/atualiza um registro em academico.usuario.
    - usuario_payload: dict com nome,email,senha(hasheada),role
    - alunos_map/professores_map/funcionarios_map: mapping email->id retornado por upsert_data
    Retorna id do usuario criado/atualizado.
    """
    alunos_map = alunos_map or {}
    professores_map = professores_map or {}
    funcionarios_map = funcionarios_map or {}

    schema = "academico"
    table = "usuario"
    email = usuario_payload["email"]

    # Somente as FKs que existem no schema atual
    id_aluno = alunos_map.get(email)
    id_professor = professores_map.get(email)
    # NÃO usar id_funcionario: coluna não existe no schema

    payload = {
        "nome": usuario_payload.get("nome"),
        "email": email,
        "senha": usuario_payload.get("senha"),  # já hasheada
        "role": usuario_payload.get("role"),
        "id_aluno": id_aluno,
        "id_professor": id_professor
    }

    # Remover chaves None para não inserir colunas desnecessárias
    insert_keys = [k for k, v in payload.items() if v is not None]
    insert_cols = ", ".join(insert_keys)
    insert_vals = ", ".join(":" + k for k in insert_keys)
    set_clause = ", ".join(f"{k}=excluded.{k}" for k in insert_keys if k != "email")

    sql = text(f"""
        INSERT INTO {schema}.{table} ({insert_cols})
        VALUES ({insert_vals})
        ON CONFLICT (email) DO UPDATE
        SET {set_clause}
        RETURNING id
    """)

    with engine.begin() as conn:
        new_id = conn.execute(sql, payload).scalar_one()
        return new_id