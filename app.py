from sqlite3 import IntegrityError
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
menu = st.sidebar.selectbox("Navegação", ["Cadastrar Aluno", "Consultas",  "Cadastrar Curso", "Cadastrar Usuário", "Vídeos Aulas", "Cadastrar Material", "Cadastrar Tarefa Escolar", "Deletar Usuario", "Sobre", "Ajuda"])


# - videos aulas--
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
# --- Consultas ---
if menu == "Consultas":
    st.header("📊 Consultas das Tabelas")
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

# ...existing code...

# --- Deletar Usuario ---
elif menu == "Deletar Usuario":
    st.header("❌ Deletar Registros de Tabela")
    escolha = st.selectbox("Escolha a tabela:", tabelas)

    # Busca dados da tabela
    dados = fetch_table_data(escolha)
    df = pd.DataFrame(dados)

    # Mostra tabela
    st.dataframe(df)

    # Campo para digitar IDs
    ids = st.text_input(
        "Digite os IDs a serem deletados (separados por vírgula)",
        placeholder="Ex: 1, 3, 5"
    )

    # Confirmação adicional para evitar acidentes
    confirmacao = st.checkbox("Confirme que deseja deletar os registros selecionados (irreversível)")

    if st.button("Deletar"):
        if not confirmacao:
            st.warning("⚠️ Marque a confirmação para prosseguir.")
            st.stop()

        try:
            # Converte entrada em lista de inteiros
            lista_ids = [
                int(x.strip())
                for x in ids.split(",")
                if x.strip().isdigit()
            ]

            if not lista_ids:
                st.warning("⚠️ Informe pelo menos um ID válido.")
                st.stop()

            # Assume coluna 'id' como chave; ajuste se necessário (ex.: df.columns[0] para primeira coluna)
            if 'id' not in df.columns:
                st.error("❌ Tabela não possui coluna 'id'. Ajuste o código para a chave primária correta.")
                st.stop()

            ids_existentes = df["id"].tolist()

            # IDs que não existem
            ids_invalidos = [i for i in lista_ids if i not in ids_existentes]

            if ids_invalidos:
                st.error(
                    f"❌ Os seguintes IDs não existem na tabela {escolha}: {ids_invalidos}"
                )
            else:
                # Deleta via SQL DELETE (sem cascata; risco assumido)
                with engine.begin() as conn:
                    placeholders = ', '.join([':id' + str(i) for i in range(len(lista_ids))])
                    query = f"DELETE FROM {escolha} WHERE id IN ({placeholders})"
                    params = {f'id{i}': lista_ids[i] for i in range(len(lista_ids))}
                    conn.execute(text(query), params)

                st.success(
                    f"✅ Registros {lista_ids} deletados da tabela {escolha} com sucesso!"
                )
    
        except Exception as e:
            st.error("❌ Erro ao deletar registros. Verifique integridade e tente novamente.")
            st.exception(e)  # Descomente para debug, mas remova em prod

# ...existing code...

#  cadastrar usuario
elif menu == "Cadastrar Usuário":
    st.header("➕ Cadastrar Usuário")
    role = st.selectbox("Função", ["Admin", "Professor", "Aluno", "Funcionário"])
    if role == "Aluno":
        id_aluno = st.number_input("ID do Aluno (se aplicável)", min_value=0, value=0)
        nome_completo = st.text_input("Nome Completo do Aluno")
        email = st.text_input("Email do Aluno")
        telefone = st.text_input("Telefone do Aluno")
        data_nascimento = st.text_input("Data de Nascimento (DD/MM/AAAA)")
        status_ativo = st.selectbox("Status do Aluno", ["Ativo", "Inativo"])
        data_cadastro = st.text_input("Data de Cadastro (DD/MM/AAAA)")
    elif role == "Professor":
        id_professor = st.number_input("ID do Professor (se aplicável)", min_value=0, value=0)
        nome = st.text_input("Nome Completo do Professor")
        email = st.text_input("Email do Professor")
        telefone = st.text_input("Telefone do Professor")
        especialidade = st.text_input("Especialidade do Professor")
        data_contratacao = st.text_input("Data de Contratação (DD/MM/AAAA)")
        senha = st.text_input("Senha", type="password")
    elif role in ["Admin", "Funcionário"]:
        if role == "Funcionário":
            id_funcionario = st.number_input("ID do Funcionário (se aplicável)", min_value=0, value=0) 
            nome = st.text_input("Nome Completo do Funcionário") 
            cargo = st.text_input("Cargo do Funcionário")
            email = st.text_input("Email do Funcionário")
            senha = st.text_input("Senha", type="password")
        else:  # Admin
            nome = st.text_input("Nome Completo")
            email = st.text_input("Email")
            telefone = st.text_input("Telefone")
            senha = st.text_input("Senha", type="password")
            

    if st.button("Salvar Usuário"):
        senha_hash = hash(senha)  # Exemplo simples de hash, use uma função de hash segura na prática
         # Monta o usuário básico
        usuario_base = {
            "nome": nome,
            "email": email,
            "senha": senha,
            "role": role
        }      
        alunos_a_ser_inseridos = []
        professores_a_ser_inseridos = []
        funcionarios_a_ser_inseridos = []      
        # Decide o tipo de cadastro
        if role == "Aluno":
            alunos_a_ser_inseridos.append({
                "id_aluno": id_aluno if id_aluno != 0 else None,
                "nome_completo": username,
                "email": email,
                "telefone": telefone,
                "data_nascimento": "01/01/2000",  # se não existir no formulário
                "status_ativo": status_ativo == "Ativo",
                "data_cadastro": data_contratacao if data_contratacao else "01/01/2025"
            })

        elif role == "Professor":
            professores_a_ser_inseridos.append({
                "id_professor": id_professor if id_professor != 0 else None,
                "nome": username,
                "email": email,
                "telefone": telefone,
                "especialidade": especialidade,
                "data_contratacao": data_contratacao if data_contratacao else "01/01/2025"
            })

        else:  # Admin ou Funcionário
            funcionarios_a_ser_inseridos.append({
                "id_funcionario": None,
                "nome": nome,
                "cargo": cargo,
                "email": email,
                
            })

        try:
            # Chama corretamente a função de criação/upsert
            criar_usuarios_completos(engine, alunos_a_ser_inseridos, professores_a_ser_inseridos, funcionarios_a_ser_inseridos)
            upsert_data(engine, aluno, alunos_a_ser_inseridos, "id_aluno")
            upsert_data(engine, professor, professores_a_ser_inseridos, "id_professor")
            upsert_data(engine, funcionario, funcionarios_a_ser_inseridos, "email")
            
            # Se chegar até aqui sem erro
            st.success("✅ Usuário inserido/atualizado com sucesso!")

        except IntegrityError as e:
            # Caso haja violação de UNIQUE ou outro erro de integridade
            st.error("❌ Email duplicado ou dado inválido. Verifique e tente novamente.")
        except Exception as e:
            # Qualquer outro erro inesperado
            st.error(f"❌ Ocorreu um erro inesperado: {str(e)}")


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



