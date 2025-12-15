from utils.security import hash_password, is_probably_bcrypt_hash
from sqlite3 import IntegrityError
import streamlit as st
import pandas as pd
from sqlalchemy import text
from db.config import get_db_engine, db_config
from db.run_queries import fetch_table_data, deletar_aluno_e_dependencias, upsert_table_data
from db.upsert import *
import streamlit as st
from pages.navbar import *
from pages.login import *
from utils.security import hash_password  # bcrypt util

st.markdown("""
<style>

.carousel-container {
    width: 100%;
    overflow-x: auto;
    overflow-y: hidden;
    white-space: nowrap;
    padding: 20px 0;
}

.carousel-container::-webkit-scrollbar {
    height: 10px;
}

.carousel-container::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 10px;
}

.carousel-container::-webkit-scrollbar-thumb:hover {
    background: #555;
}

.carousel-item {
    display: inline-block;
    width: 280px;
    margin-right: 20px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    overflow: hidden;
    vertical-align: top;
    transition: 0.3s;
}

.carousel-item:hover {
    transform: translateY(-5px);
}

.carousel-item img {
    width: 100%;
    height: 160px;
    object-fit: cover;
}

.carousel-title {
    font-size: 18px;
    font-weight: 700;
    padding: 10px;
    text-align: center;
}

.carousel-desc {
    padding: 0 10px 10px 10px;
    font-size: 14px;
    color: #444;
    text-align: center;
}

.carousel-footer {
    background: #f1f1f1;
    padding: 8px;
    text-align: center;
    font-size: 13px;
    color: #555;
    border-top: 1px solid #ddd;
}

.carousel-link {
    text-decoration: none;
    color: inherit;
}

</style>
""", unsafe_allow_html=True)
#Conexão
engine = get_db_engine(db_config)
# Menu e autenticação
selected = menu()

if selected is None:
    st.stop()


# DEBUG - remova depois
#st.write(f"DEBUG: selected = '{selected}'")
#st.write(f"DEBUG: type(selected) = {type(selected)}")


st.title("📚 Escola Metanoia - Painel Acadêmico")

# Mapeamento de tabelas
tabelas_map = {
    "Aluno": "academico.aluno",
    "Curso": "academico.curso",
    "Turma": "academico.turma",
    "Inscrição": "academico.inscricao",
    "Material": "academico.material",
    "Venda": "academico.venda",
    "Item Venda": "academico.item_venda",
    "Pagamento": "academico.pagamento",
    "Usuário": "academico.usuario",
    "Tarefa Escolar": "academico.tarefa_escolar",
    "Curso Aluno": "academico.curso_aluno",
    "Professor": "academico.professor",
    "Funcionário": "academico.funcionario",
    "Professor Disciplina": "academico.professor_disciplina",
    "Tarefa Auxiliar": "academico.tarefa_auxiliar",
}

tabelas_nomes = list(tabelas_map.keys())

if selected == "Página Inicial":

   # Mantém seu navbar atual
    st.header("🏠 Bem-vindo ao Painel Acadêmico")
    st.write(f"Olá, {st.session_state.email}! Role: {st.session_state.role}")

    # LOGO (opcional)
    st.markdown("""
        <div style="width:100%; text-align:center; margin-top:10px;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Logo_Blue.png/600px-Logo_Blue.png"
                style="width:140px;">
        </div>
    """, unsafe_allow_html=True)

    # ============================
    #  CARROSSEL DE CARDS
    # ============================

    cards = [
        {
            "titulo": "Gerenciar Alunos",
            "img": "https://images.pexels.com/photos/3184328/pexels-photo-3184328.jpeg",
            "desc": "Cadastre, edite e visualize informações dos alunos.",
            "rodape": "Acesso rápido ao módulo de alunos",
            "link": "/?page=alunos"
        },
        {
            "titulo": "Professores",
            "img": "https://images.pexels.com/photos/5212345/pexels-photo-5212345.jpeg",
            "desc": "Controle de professores, disciplinas e horários.",
            "rodape": "Gestão acadêmica",
            "link": "/?page=professores"
        },
        {
            "titulo": "Funcionários",
            "img": "https://images.pexels.com/photos/3184465/pexels-photo-3184465.jpeg",
            "desc": "Gerencie cargos, permissões e dados administrativos.",
            "rodape": "Administração interna",
            "link": "/?page=funcionarios"
        },
        {
            "titulo": "Relatórios",
            "img": "https://images.pexels.com/photos/669615/pexels-photo-669615.jpeg",
            "desc": "Acompanhe métricas, desempenho e indicadores.",
            "rodape": "Visão estratégica",
            "link": "/?page=relatorios"
        }
    ]

    # Renderiza o carrossel
    st.markdown("<div class='carousel-container'>", unsafe_allow_html=True)

    for card in cards:
        st.markdown(f"""
            <a href="{card['link']}" class="carousel-link">
                <div class="carousel-item">
                    <img src="{card['img']}">
                    <div class="carousel-title">{card['titulo']}</div>
                    <div class="carousel-desc">{card['desc']}</div>
                    <div class="carousel-footer">{card['rodape']}</div>
                </div>
            </a>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# --- Consultas ---
if selected == "Consultas":
    st.header("📊 Consultas das Tabelas")
    escolha_nome = st.selectbox("Escolha a tabela:", tabelas_nomes)
    escolha =  tabelas_map[escolha_nome]
    df = pd.DataFrame(fetch_table_data(escolha))
    st.dataframe(df)
    
    

elif selected == "Cadastrar Aluno":
    st.header("➕ Cadastrar Aluno")
    id_aluno = st.number_input("ID do Aluno (deixe 0 para novo)", min_value=0, value=0)
    nome_completo = st.text_input("Nome do Aluno")
    senha = st.text_input("Senha", type="password")
    role = "aluno"
    email = st.text_input("Email do Aluno")
    telefone = st.text_input("Telefone do Aluno")
    data_nascimento = st.text_input("Data de Nascimento (DD/MM/AAAA)")
    status_ativo = st.selectbox("Status do Aluno", ["Ativo", "Inativo"])
    data_cadastro = st.text_input("Data de Cadastro (DD/MM/AAAA)")

    if st.button("Salvar Aluno"):
        # Validações defensivas
        if not nome_completo:
            st.error("Nome do aluno é obrigatório.")
            st.stop()
        if not email:
            st.error("Email é obrigatório.")
            st.stop()
        if not senha:
            st.error("Senha é obrigatória.")
            st.stop()

        # Gera hash da senha aqui, na camada de aplicação
        try:
            senha_hash = hash_password(senha)  # bcrypt, rounds controlado no utilitário
        except Exception as e:
            st.error(f"Erro ao gerar hash da senha: {e}")
            st.stop()

        # Monta payloads
        dados_aluno = {
            "id": None,
            "nome_completo": nome_completo,
            "email": email,
            "telefone": telefone,
            "data_nascimento": data_nascimento,
            "status_ativo": True if status_ativo == "Ativo" else False,
            "data_cadastro": data_cadastro
        }

        dados_usuario = {
            "nome": nome_completo,
            "email": email,
            "senha": senha_hash,  # **hash** aqui
            "role": "aluno"
        }

        # Chamar função de persistência no modo seguro (esperando hash)
        try:
            create_aluno_e_usuario(engine, dados_aluno, dados_usuario)
        except ValueError as ve:
            # Mensagem clara para desenvolvedor/operador
            st.error(f"Erro ao salvar: {ve}")
        except Exception as exc:
            st.error("Erro inesperado ao salvar aluno. Verifique logs.")
            # log exc em servidor
        else:
            st.success("Aluno inserido/atualizado com sucesso!")
# --- Cadastro de Curso ---
elif selected == "Cadastrar Curso":
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
elif selected == "Cadastrar Material":
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
elif selected == "Cadastrar Tarefa Escolar":
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


# --- Deletar Usuario ---
elif selected == "Deletar Usuario":
    st.header("❌ Deletar Registros de Tabela")
    escolha_nome = st.selectbox("Escolha a tabela:", tabelas_nomes)
    escolha = tabelas_map[escolha_nome]
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
                    f"❌ Os seguintes IDs não existem na tabela  {ids_invalidos}"
                )
            else:
                # Deleta via SQL DELETE (sem cascata; risco assumido)
                with engine.begin() as conn:
                    placeholders = ', '.join([':id' + str(i) for i in range(len(lista_ids))])
                    query = f"DELETE FROM {escolha} WHERE id IN ({placeholders})"
                    params = {f'id{i}': lista_ids[i] for i in range(len(lista_ids))}
                    conn.execute(text(query), params)

                st.success(
                    f"✅ Registros {lista_ids} deletados da tabela com sucesso!"
                )
    
        except Exception as e:
            st.error("❌ Erro ao deletar registros. Verifique integridade e tente novamente.")
            #st.exception(e)  # Descomente para debug, mas remova em prod


#cadastro aluno
elif selected == "Cadastrar Usuário":
    st.header("➕ Cadastrar Usuário")
    role = st.selectbox("Função", ["Admin", "Professor", "Aluno", "Funcionário"])

    # inicializa variáveis
    id_aluno = id_professor = id_funcionario = 0
    nome = email = telefone = senha = None
    cargo = especialidade = None
    data_nascimento = data_cadastro = data_contratacao = None
    status_ativo = "Ativo"

    if role == "Aluno":
        id_aluno = st.number_input("ID do Aluno (se aplicável)", min_value=0, value=0)
        nome = st.text_input("Nome Completo do Aluno")
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

    elif role == "Funcionário":
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
        # validações
        if not nome or not email:
            st.error("Preencha pelo menos Nome e Email.")
            st.stop()
        if not senha:
            st.error("Senha é obrigatória.")
            st.stop()

        # hash seguro
        try:
            senha_hash = hash_password(senha)
        except Exception as e:
            st.error(f"Erro ao gerar hash da senha: {e}")
            st.stop()

        # preparar linhas para upsert nas tabelas de pessoa
        alunos_rows = []
        prof_rows = []
        func_rows = []

        if role == "Aluno":
            data_nasc = parse_date_br(data_nascimento)
            data_cad = parse_date_br(data_cadastro) or datetime.utcnow().date()
            alunos_rows.append({
                "id": int(id_aluno) if id_aluno and id_aluno > 0 else None,
                "nome_completo": nome,
                "email": email,
                "telefone": telefone or None,
                "data_nascimento": data_nasc,
                "status_ativo": True if status_ativo == "Ativo" else False,
                "data_cadastro": data_cad
            })
        elif role == "Professor":
            data_contrat = parse_date_br(data_contratacao) or None
            prof_rows.append({
                "id": int(id_professor) if id_professor and id_professor > 0 else None,
                "nome": nome,
                "email": email,
                "telefone": telefone or None,
                "especialidade": especialidade or None,
                "data_contratacao": data_contrat
            })
        else:  # admin/funcionario
            func_rows.append({
                "id": int(id_funcionario) if id_funcionario and id_funcionario > 0 else None,
                "nome": nome,
                "cargo": cargo or None,
                "email": email
            })

        try:
            # 1) Upsert pessoas e obter mapping email->id
            alunos_map = upsert_data(engine, ("academico", "aluno"), alunos_rows, pk_field="id", conflict_target="email") if alunos_rows else {}
            prof_map = upsert_data(engine, ("academico", "professor"), prof_rows, pk_field="id", conflict_target="email") if prof_rows else {}
            func_map = upsert_data(engine, ("academico", "funcionario"), func_rows, pk_field="id", conflict_target="email") if func_rows else {}

            # 2) Criar/atualizar usuário vinculando FK corretas (não usar id da pessoa como usuario.id)
            usuario_payload = {
                "nome": nome,
                "email": email,
                "senha": senha_hash,
                "role": role.lower()
            }
            new_user_id = criar_usuarios_completos(engine, usuario_payload, alunos_map, prof_map, func_map)

            st.success(f"✅ Usuário inserido/atualizado com sucesso! (id={new_user_id})")

        except IntegrityError:
            st.error("❌ Email duplicado ou dado inválido. Verifique e tente novamente.")
        except Exception as e:
            st.error(f"❌ Ocorreu um erro inesperado: {str(e)}")


# --- Vídeos Aulas ---
elif selected == "Vídeos Aulas":
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
        
        selected = "Vídeos Aulas"
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
                    selected = "Vídeos Aulas"          
        elif button_aulas_gravadas:
            
            link_video_1 = "https://drive.google.com/file/d/10R9qGZzA6L2QqBiN_koUaO3e2pSQYaIe/view?usp=drive_link"
            st.header("Assista Aula Gravada")
            st.markdown(f"[AULA 2]({link_video_1})")
            
            if  st.button(f"Voltar"):
                    selected = "Vídeos Aulas"
                    
   
        
#--- Sobre ---
elif selected == "Sobre":
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
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2024 Escola Metanoia")    
# --- Ajuda ---
elif selected == "Ajuda":
    st.header("❓ Ajuda")
    st.markdown("""
    **Como usar o Painel Acadêmico:**
    
    1. **Consultas:** Selecione uma tabela para visualizar seus dados.
    2. **Cadastrar Curso/Material:** Preencha os campos e clique em "Salvar" para inserir ou atualizar registros.
    3. **Cadastrar Tarefa Escolar:** Forneça os detalhes da tarefa e clique em "Salvar Tarefa".
    4. **Deletar Aluno:** Insira os IDs dos alunos a serem deletados e clique em "Deletar".
    
    Para mais informações, entre em contato com o suporte técnico.
    """)
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2024 Escola Metanoia")  



# -- Rodapé --  
    
 
  
# --- Fim do arquivo app.py ---



