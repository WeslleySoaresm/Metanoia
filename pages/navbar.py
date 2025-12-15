from streamlit_option_menu import option_menu
import streamlit as st
from pages.login import fazer_login

def get_menu_por_role(role):
    """Retorna opções de menu baseado na role do usuário"""
    
    menus_base = {
        "admin": {
            "opcoes": ["Página Inicial", "Consultas", "Cadastrar Aluno", "Cadastrar Curso", 
                      "Cadastrar Usuário", "Cadastrar Material", "Cadastrar Tarefa Escolar", 
                      "Deletar Usuario", "Sobre", "Ajuda"],
            "icons": ["house", "search", "person-plus", "book", "users", "box", 
                     "clipboard", "trash", "info-circle", "question-circle"]
        },
        "professor": {
            "opcoes": ["Página Inicial", "Cadastrar Tarefa Escolar", "Sobre", "Ajuda"],
            "icons": ["house", "clipboard", "info-circle", "question-circle"]
        },
        "aluno": {
            "opcoes": ["Página Inicial", "Minhas Tarefas", "Sobre", "Ajuda"],
            "icons": ["house", "clipboard-check", "info-circle", "question-circle"]
        }
    }
    
    return menus_base.get(role, menus_base["aluno"])

def menu():
    # Inicializar session_state
    if "usuario_id" not in st.session_state:
        st.session_state.usuario_id = None
    if "role" not in st.session_state:
        st.session_state.role = None
    
    st.set_page_config(
        page_title="Metanoia - Painel Acadêmico",
        page_icon="img/metanoia.ico",
        layout="wide",
    )
    
    # Remover sidebar
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] { display: none !important; }
            [data-testid="stSidebar"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)
    
    # Se não autenticado, redirecionar para login
    if not st.session_state.usuario_id:
        fazer_login()
        return None
    
    # Navbar com menu dinâmico
    menu_config = get_menu_por_role(st.session_state.role)
    
    col1, col2 = st.columns([0.9, 0.1])
    
    with col1:
        selected = option_menu(
            menu_title=None,
            options=menu_config["opcoes"],
            icons=menu_config["icons"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
        )
    
    with col2:
        if st.button("🚪 Sair"):
            st.session_state.usuario_id = None
            st.session_state.role = None
            st.session_state.email = None
            st.rerun()
    
    st.markdown("---")
    
    return selected