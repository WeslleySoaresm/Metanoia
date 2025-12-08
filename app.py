import streamlit as st
import pandas as pd
from sqlalchemy import text
from db.config import get_db_engine, db_config
from db.run_queries import fetch_table_data, deletar_aluno_e_dependencias
from db.upsert import upsert_data, curso, material

# Conexão
engine = get_db_engine(db_config)

st.title("📚 Escola Metanoia - Painel Acadêmico")

# --- Menu lateral ---
menu = st.sidebar.radio("Navegação", ["Consultas", "Cadastrar Curso", "Cadastrar Material", "Cadastrar Tarefa Escolar", "Deletar Aluno"])

# --- Consultas ---
if menu == "Consultas":
    st.header("📊 Consultas das Tabelas")
    tabelas = ["academico.aluno", "academico.curso", "academico.turma", "academico.inscricao",
               "academico.material", "academico.venda", "academico.item_venda", "academico.pagamento"]

    escolha = st.selectbox("Escolha a tabela:", tabelas)
    df = pd.DataFrame(fetch_table_data(escolha))
    st.dataframe(df)

# --- Cadastro de Curso ---
elif menu == "Cadastrar Curso":
    st.header("➕ Inserir/Atualizar Curso")
    nome = st.text_input("Nome do curso")
    descricao = st.text_area("Descrição")
    carga = st.number_input("Carga horária", min_value=1)
    preco = st.number_input("Preço padrão", min_value=0.0)

    if st.button("Salvar Curso"):
        dados = [{"nome": nome, "descricao": descricao, "carga_horaria": carga, "preco_padrao": preco}]
        upsert_data(engine, curso, dados, "nome")
        st.success("Curso inserido/atualizado com sucesso!")

# --- Cadastro de Material ---
elif menu == "Cadastrar Material":
    st.header("➕ Inserir/Atualizar Material")
    nome = st.text_input("Nome do material")
    descricao = st.text_area("Descrição")
    preco = st.number_input("Preço de venda", min_value=0.0)
    estoque = st.number_input("Estoque atual", min_value=0)

    if st.button("Salvar Material"):
        dados = [{"nome": nome, "descricao": descricao, "preco_venda": preco, "estoque_atual": estoque}]
        upsert_data(engine, material, dados, "nome")
        st.success("Material inserido/atualizado com sucesso!")

# --- Cadastro de Tarefa Escolar ---
elif menu == "Cadastrar Tarefa Escolar":
    st.header("➕ Inserir Tarefa Escolar")
    aluno_id = st.number_input("ID do Aluno", min_value=1)
    titulo = st.text_input("Título da tarefa")
    descricao = st.text_area("Descrição")
    tipo = st.selectbox("Tipo", ["prova", "trabalho", "leitura", "pratica", "oracao"])
    progresso_curso = st.slider("Progresso Curso (%)", 0, 100)
    progresso_leitura = st.slider("Progresso Leitura (%)", 0, 100)
    data_entrega = st.date_input("Data de entrega")
    status = st.selectbox("Status", ["pendente", "entregue", "corrigida", "revisao"])

    if st.button("Salvar Tarefa"):
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO academico.tarefa_escolar
                (xid_aluno, titulo, descricao, tipo, progresso_curso, progresso_leitura, data_entrega, status)
                VALUES (:aluno, :titulo, :descricao, :tipo, :pc, :pl, :data, :status)
            """), {
                "aluno": aluno_id, "titulo": titulo, "descricao": descricao,
                "tipo": tipo, "pc": progresso_curso, "pl": progresso_leitura,
                "data": data_entrega, "status": status
            })
        st.success("Tarefa escolar cadastrada com sucesso!")

# --- Deletar Aluno ---
elif menu == "Deletar Aluno":
    st.header("❌ Deletar Aluno e Dependências")
    df = pd.DataFrame(fetch_table_data("academico.aluno"))
    st.dataframe(df)

    ids = st.text_input("Digite os IDs dos alunos a serem deletados (separados por vírgula)")
    if st.button("Deletar"):
        lista_ids = [int(x.strip()) for x in ids.split(",") if x.strip().isdigit()]
        deletar_aluno_e_dependencias(engine, lista_ids)
        st.success(f"Alunos {lista_ids} deletados com sucesso!")