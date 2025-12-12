import streamlit as st
import pandas as pd
from sqlalchemy import text
from db.config import get_db_engine, db_config
from db.run_queries import fetch_table_data, deletar_aluno_e_dependencias
from db.upsert import upsert_data, curso, material

# --- Configuração da página ---
st.set_page_config(
    page_title="Metanoia - Painel Acadêmico",
    page_icon="img/metanoia.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

engine = get_db_engine(db_config)

# --- Função de login ---
def login():
    st.title("🔐 Login - Escola Metanoia")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    perfil = st.selectbox("Perfil", ["Admin", "Professor", "Aluno"])

    if st.button("Entrar"):
        # Protótipo: validação simples
        if usuario and senha:
            st.session_state["logged_in"] = True
            st.session_state["role"] = perfil
            st.success(f"Bem-vindo {usuario} ({perfil})!")
        else:
            st.error("Usuário ou senha inválidos.")

# --- Painéis por perfil ---
def painel_admin():
    menu = st.sidebar.selectbox("Navegação", [
        "Consultas", "Cadastrar Curso", "Cadastrar Material", "Cadastrar Tarefa Escolar",
        "Inserir Aula", "Ver Trabalhos", "Deletar Aluno", "Pagamentos", "Sobre", "Ajuda"
    ])
    executar_menu(menu)

def painel_professor():
    menu = st.sidebar.selectbox("Navegação", [
        "Cadastrar Tarefa Escolar", "Inserir Aula", "Cadastrar Curso",
        "Cadastrar Material", "Ver Trabalhos", "Sobre", "Ajuda"
    ])
    executar_menu(menu)

def painel_aluno():
    menu = st.sidebar.selectbox("Navegação", [
        "Enviar Tarefa", "Ver Turma e Cursos", "Ver Tarefas Escolares",
        "Pagamentos", "Sobre", "Ajuda"
    ])
    executar_menu(menu)

# --- Função para executar menus comuns ---
def executar_menu(menu):
    if menu == "Consultas":
        st.header("📊 Consultas das Tabelas")
        tabelas = ["academico.aluno", "academico.curso", "academico.turma", "academico.inscricao",
                   "academico.material", "academico.venda", "academico.item_venda", "academico.pagamento"]
        escolha = st.selectbox("Escolha a tabela:", tabelas)
        df = pd.DataFrame(fetch_table_data(escolha))
        st.dataframe(df)

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

    elif menu == "Deletar Aluno":
        st.header("❌ Deletar Aluno e Dependências")
        df = pd.DataFrame(fetch_table_data("academico.aluno"))
        st.dataframe(df)
        ids = st.text_input("Digite os IDs dos alunos a serem deletados (separados por vírgula)")
        if st.button("Deletar"):
            lista_ids = [int(x.strip()) for x in ids.split(",") if x.strip().isdigit()]
            ids_existentes = df["id_aluno"].tolist()
            ids_invalidos = [i for i in lista_ids if i not in ids_existentes]
            if ids_invalidos:
                st.error(f"IDs inválidos: {ids_invalidos}")
            else:
                deletar_aluno_e_dependencias(engine, lista_ids)
                st.success(f"✅ Alunos {lista_ids} deletados com sucesso!")

    elif menu == "Pagamentos":
        st.header("💳 Pagamentos")
        df = pd.DataFrame(fetch_table_data("academico.pagamento"))
        st.dataframe(df)

    elif menu == "Sobre":
        st.header("ℹ️ Sobre a Escola Metanoia")
        st.markdown("Este painel foi desenvolvido para gerenciar as operações acadêmicas da Escola Metanoia.")

    elif menu == "Ajuda":
        st.header("❓ Ajuda")
        st.markdown("Selecione uma opção no menu lateral para acessar as funcionalidades disponíveis.")

# --- Execução principal ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login()
else:
    role = st.session_state["role"]
    if role == "Admin":
        painel_admin()
    elif role == "Professor":
        painel_professor()
    elif role == "Aluno":
        painel_aluno()