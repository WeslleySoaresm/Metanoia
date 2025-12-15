import streamlit as st
from db.config import get_db_engine, db_config
from sqlalchemy import text
import hashlib
import bcrypt
from typing import Optional

BCRYPT_PREFIXES = ("$2b$", "$2a$", "$2y$")

def is_probably_bcrypt_hash(s: Optional[str]) -> bool:
    return isinstance(s, str) and any(s.startswith(p) for p in BCRYPT_PREFIXES)

def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Verifica senha suportando:
    - bcrypt (recomendado)
    - fallback SHA-256 hex (legado) — temporário
    """
    if not plain_password or not stored_hash:
        return False

    # bcrypt
    if is_probably_bcrypt_hash(stored_hash):
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), stored_hash.encode("utf-8"))
        except Exception:
            return False

    # fallback SHA-256 hex (LEGADO)
    try:
        sha = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
        return sha == stored_hash
    except Exception:
        return False

def fazer_login():
    st.set_page_config(page_title="Login - Metanoia", layout="centered")
    st.title("🔐 Login - Escola Metanoia")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        email = st.text_input("Email:")
        senha = st.text_input("Senha:", type="password")
        
        if st.button("Entrar", use_container_width=True):
            if not email or not senha:
                st.error("Preencha todos os campos.")
                return False
            
            engine = get_db_engine(db_config)
            
            try:
                with engine.connect() as conn:
                    query = text("""
                        SELECT u.id, u.senha, u.role, COALESCE(a.id, p.id) as pessoa_id
                        FROM academico.usuario u
                        LEFT JOIN academico.aluno a ON u.id_aluno = a.id
                        LEFT JOIN academico.professor p ON u.id_professor = p.id
                        WHERE u.email = :email
                    """)
                    result = conn.execute(query, {"email": email}).fetchone()
                    
                    if result and verify_password(senha, result[1]):
                        st.session_state.usuario_id = result[0]
                        st.session_state.role = result[2]
                        st.session_state.pessoa_id = result[3]
                        st.session_state.email = email
                        st.success("Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Email ou senha incorretos.")
            except Exception as e:
                st.error(f"Erro na conexão: {e}")
                
    return False