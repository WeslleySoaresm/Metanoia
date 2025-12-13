from sqlalchemy.dialects.postgresql import insert

def testar_upsert(engine):
    with engine.begin() as conn:
        # --- Teste Aluno ---
        aluno_data = {
            "nome_completo": "João da Silva",
            "email": "joao@teste.com",
            "telefone": "123456789",
            "data_nascimento": "2000-01-01",
            "status_ativo": True,
            "data_cadastro": "2025-12-12"
        }
        stmt_aluno = insert(aluno).values(**aluno_data).on_conflict_do_update(
            index_elements=["email"],
            set_={col.name: insert(aluno).excluded.get(col.name)
                  for col in aluno.columns if col.name != "id_aluno" and col.name != "email"}
        )
        conn.execute(stmt_aluno)
        print("✅ UPSERT Aluno executado.")

        # --- Teste Professor ---
        professor_data = {
            "nome": "Maria Oliveira",
            "email": "maria@teste.com"
        }
        stmt_professor = insert(professor).values(**professor_data).on_conflict_do_update(
            index_elements=["email"],
            set_={col.name: insert(professor).excluded.get(col.name)
                  for col in professor.columns if col.name != "id_professor" and col.name != "email"}
        )
        conn.execute(stmt_professor)
        print("✅ UPSERT Professor executado.")

        # --- Teste Funcionario ---
        funcionario_data = {
            "nome": "Carlos Souza",
            "email": "carlos@teste.com",
            "cargo": "TI"
        }
        stmt_funcionario = insert(funcionario).values(**funcionario_data).on_conflict_do_update(
            index_elements=["email"],
            set_={col.name: insert(funcionario).excluded.get(col.name)
                  for col in funcionario.columns if col.name != "id_funcionario" and col.name != "email"}
        )
        conn.execute(stmt_funcionario)
        print("✅ UPSERT Funcionário executado.")

# Chame a função de teste
testar_upsert(engine)
