
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
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Este painel foi desenvolvido para gerenciar as operações acadêmicas da Escola Metanoia.",
        'Get Help': 'https://metanoia.com/help',
        'Report a bug': "https://metanoia.com/bug-report",
    }
)

# --- Conexão ---
engine = get_db_engine(db_config)

# --- Cabeçalho principal ---
st.title("📚 Escola Metanoia - Painel Acadêmico")

st.markdown("""
<div style='background-color:black;padding:15px;border-radius:10px; margin-bottom:20px'>
    <h3 style='color:white'>🗓️ Período Letivo: <span style='color:#2980b9'>06/OUT/2025 à 19/DEZ/2025</span></h3>
    <p><strong>Dia da semana:</strong> Quarta-feira<br>
    <strong>Horário:</strong> 20:00</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.button("▶️ Assistir ao Vivo")
with col2:
    st.button("📚 Aulas Gravadas")
with col3:
    st.button("📤 Entrega de Trabalhos")
st.markdown("---")

# --- Menu lateral ---
menu = st.sidebar.selectbox(
    "Navegação",
    ["Consultas", "Cadastrar Curso", "Cadastrar Material", "Cadastrar Tarefa Escolar", "Vídeos Aulas", "Deletar Aluno", "Sobre", "Ajuda"]
)
if admin_user := st.sidebar.checkbox("Admin User"):
    st.sidebar.write("Você está logado como Admin.")
    # --- Consultas ---
    if menu == "Consultas":
        st.header("📊 Consultas das Tabelas")
        tabelas = [
            "academico.aluno", "academico.curso", "academico.turma", "academico.inscricao",
            "academico.material", "academico.venda", "academico.item_venda", "academico.pagamento",
            "academico.usuario"
        ]
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
        ids_existentes = df["id_aluno"].tolist()
        ids_invalidos = [i for i in lista_ids if i not in ids_existentes]

        if ids_invalidos:
            st.error(f"Os seguintes IDs não existem na tabela de alunos: {ids_invalidos}")
        else:
            deletar_aluno_e_dependencias(engine, lista_ids)
            st.success(f"✅ Alunos {lista_ids} deletados com sucesso!")

# --- Vídeos Aulas ---
elif menu == "Vídeos Aulas":
    st.header("🎥 Vídeos Aulas")
    st.markdown("Aqui você pode acessar vídeos aulas relacionados ao conteúdo acadêmico.")

    aulas = [
        {"data": "06/10/2025", "titulo": "Aula 01", "video": True, "chat": True, "transcricao": True},
        {"data": "13/10/2025", "titulo": "Aula 02", "video": True, "chat": True, "transcricao": True},
        {"data": "27/10/2025", "titulo": "Aula 03", "video": True, "chat": True, "transcricao": False},
        {"data": "03/11/2025", "titulo": "Aula 04", "video": True, "chat": True, "transcricao": True},
    ]

    for aula in aulas:
        st.markdown(f"**{aula['titulo']} - {aula['data']}**")
        col1, col2, col3 = st.columns(3)
        if aula["video"]: col1.button("🎥 Vídeo", key=aula["titulo"] + "_video")
        if aula["chat"]: col2.button("💬 Chat", key=aula["titulo"] + "_chat")
        if aula["transcricao"]: col3.button("📄 Transcrição", key=aula["titulo"] + "_trans")

# --- Sobre ---
elif menu == "Sobre":
    st.header("ℹ️ Sobre o Painel Acadêmico")
    st.markdown("""
    Este painel foi desenvolvido para gerenciar as operações acadêmicas da Escola Metanoia.
    
    **Funcionalidades:**
    - Consultar dados das tabelas acadêmicas.
    - Cadastrar e atualizar cursos e materiais.
    - Inserir tarefas escolares para os alunos.
    - Deletar alunos e suas dependências no sistema.
    
    **Tecnologias Utilizadas:**
    - Streamlit para a interface web.
    - SQLAlchemy para interação com o banco de dados.
    
    Desenvolvido por Weslley Soares.
    """)

# --- Ajuda ---
elif menu == "Ajuda":
    st.header("❓ Ajuda")
    st.markdown("""
    **Como usar o Painel Acadêmico:**
    
    1. **Consultas:** Selecione uma tabela para visualizar seus dados.
    2. **Cadastrar Curso/Material:** Preencha os campos e clique em "Salvar".
    3. **Cadastrar Tarefa Escolar:** Forneça os detalhes e clique em "Salvar Tarefa".
    4. **Deletar Aluno:** Insira os IDs e clique em "Deletar".
    
    Para mais informações, entre em contato com o suporte técnico.
    """)

