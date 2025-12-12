import streamlit as st
import pandas as pd
from sqlalchemy import text
from db.config import get_db_engine, db_config
from db.run_queries import fetch_table_data, deletar_aluno_e_dependencias, upsert_table_data
from db.upsert import *


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



#Conexão
engine = get_db_engine(db_config)
 #-- login --
 
 
 
 

st.title("📚 Escola Metanoia - Painel Acadêmico")

# --- Menu lateral ---
menu = st.sidebar.selectbox("Navegação", ["Cadastrar Aluno", "Consultas",  "Cadastrar Curso", "Cadastrar Usuário", "Vídeos Aulas", "Cadastrar Material", "Cadastrar Tarefa Escolar", "Deletar Aluno", "Sobre", "Ajuda"])


# - videos aulas--


# --- Consultas ---
if menu == "Consultas":
    st.header("📊 Consultas das Tabelas")
    
    lista_academico = ["academico.aluno", "academico.curso", "academico.turma", "academico.inscricao",
               "academico.material", "academico.venda", "academico.item_venda", "academico.pagamento",
               "academico.usuario",
               "academico.tarefa_escolar",
               "academico.curso_aluno",
                "academico.professor",
                "academico.funcionario",
                "academico.professor_disciplina",
                "academico.tarefa_auxiliar",
                "academico.material",
                "academico.turma"
    ]
    tabelas = [ 
               
               lista_academico[i] for i in range(len(lista_academico)) 
               
               ]

    escolha = st.selectbox("Escolha a tabela:", tabelas)
    df = pd.DataFrame(fetch_table_data(escolha))
    st.dataframe(df)
# cadastrar aluno
elif menu == "Cadastrar Aluno":
    st.header("➕ Cadastrar Aluno")
    id_aluno = st.number_input("ID do Aluno (deixe 0 para novo)", min_value=0, value=0)
    nome_completo = st.text_input("Nome do Aluno")
    senha = st.text_input("Senha", type="password")
    role = "aluno"  # Perfil fixo para aluno
    email = st.text_input("Email do Aluno")
    telefone = st.text_input("Telefone do Aluno")
    data_nascimento = st.text_input("Data de Nascimento (DD/MM/AAAA)")
    status_ativo = st.selectbox("Status do Aluno", ["Ativo", "Inativo"])
    data_cadastro = st.text_input("Data de Cadastro (DD/MM/AAAA)")
    

    if st.button("Salvar Aluno"):
        dados_aluno = {"id_aluno": None, "nome_completo": nome_completo, "email": email, "telefone": telefone, "data_nascimento": data_nascimento, "status_ativo": True if status_ativo == "Ativo" else False, "data_cadastro": data_cadastro}
        dados_usuario = {"nome": nome_completo, "email": email, "senha": senha, "role": "aluno"}  # Ajuste conforme necessário
        create_aluno_e_usuario(engine, dados_aluno, dados_usuario)
        st.success("Aluno inserido/atualizado com sucesso!")    

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

        # IDs que existem no banco
        ids_existentes = df["id_aluno"].tolist()

        # IDs inválidos (não encontrados)
        ids_invalidos = [i for i in lista_ids if i not in ids_existentes]

        if ids_invalidos:
            st.error(f"Os seguintes IDs não existem na tabela de alunos: {ids_invalidos}")
        else:
            deletar_aluno_e_dependencias(engine, lista_ids)
            st.success(f"✅ Alunos {lista_ids} deletados com sucesso!")

#  cadastrar usuario
elif menu == "Cadastrar Usuário":
    st.header("➕ Cadastrar Usuário")
    username = st.text_input("Nome de usuário")
    senha = st.text_input("Senha", type="password")
    role = st.selectbox("Função", ["Admin", "Professor", "Aluno", "Funcionário"])
    email = st.text_input("Email")
    id_aluno = st.number_input("ID do Aluno (se aplicável)", min_value=0, value=0)
    id_professor = st.number_input("ID do Professor (se aplicável)", min_value=0, value=0)

    if st.button("Salvar Usuário"):
        senha_hash = hash(senha)  # Exemplo simples de hash, use uma função de hash segura na prática
        dados = [{"nome": username, "senha": senha, "role": role, "email": email, "id_aluno": id_aluno if id_aluno > 0 else None, "id_professor": id_professor if id_professor > 0 else None}]
        criar_usuarios_completos(engine, dados, dados, dados)
        st.success("Usuário inserido/atualizado com sucesso!")   



# --- Vídeos Aulas ---
elif menu == "Vídeos Aulas":
    st.header("🎥 Vídeos Aulas")
    st.markdown("""
    Aqui você pode acessar vídeos aulas relacionados ao conteúdo acadêmico.
    
    **Em breve mais conteúdos serão adicionados!**
    """
    )
    aulas_tema = st.sidebar.selectbox("Selecione Disciplina", ["Bibliologia", "Pentateuco", "Teontologia"])
    
    if aulas_tema == "Bibliologia":
        st.subheader("📚 Bibliologia")
        st.markdown("Vídeo aula sobre os livros da Bíblia e sua importância.")
        
        menu = "Vídeos Aulas"
        AO_VIVO = "https://metanoia.com/aulas-ao-vivo"
        AULAS_GRAVADAS = "https://metanoia.com/aulas-gravadas"
        button_ao_vivo = st.button("Assistir Aula AO VIVO")
        button_voltar =  "Vídeos Aulas"
        button_aulas_gravadas = st.button("Assistir Aula AULAS GRAVADAS")
        
        if button_ao_vivo:
            
            link_video_1 = "https://drive.google.com/file/d/1z1Yk2bXKJfX1Z4nU5r8q3F5G7H6I9J0K/view?usp=drive_link"
            st.header("Assista Aula AO VIVO ")
            st.markdown(f"[Clique aqui para assistir ao vivo]({link_video_1})")
            
            if  st.button(f"Voltar"):
                    menu = "Vídeos Aulas"          
        elif button_aulas_gravadas:
            
            link_video_1 = "https://drive.google.com/file/d/10R9qGZzA6L2QqBiN_koUaO3e2pSQYaIe/view?usp=drive_link"
            st.header("Assista Aula Gravada")
            st.markdown(f"[AULA 2]({link_video_1})")
            
            if  st.button(f"Voltar"):
                    menu = "Vídeos Aulas"
                    
   
        
#--- Sobre ---
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
    2. **Cadastrar Curso/Material:** Preencha os campos e clique em "Salvar" para inserir ou atualizar registros.
    3. **Cadastrar Tarefa Escolar:** Forneça os detalhes da tarefa e clique em "Salvar Tarefa".
    4. **Deletar Aluno:** Insira os IDs dos alunos a serem deletados e clique em "Deletar".
    
    Para mais informações, entre em contato com o suporte técnico.
    """)




# -- Rodapé --  
    
 
st.sidebar.markdown("---")
st.sidebar.markdown("© 2024 Escola Metanoia")    
# --- Fim do arquivo app.py ---



