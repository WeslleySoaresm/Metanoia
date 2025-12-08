-- Contagens rápidas
"""SELECT 'aluno' AS tabela, COUNT(*) FROM academico.aluno
UNION ALL SELECT 'curso', COUNT(*) FROM academico.curso
UNION ALL SELECT 'turma', COUNT(*) FROM academico.turma
UNION ALL SELECT 'inscricao', COUNT(*) FROM academico.inscricao
UNION ALL SELECT 'material', COUNT(*) FROM academico.material
UNION ALL SELECT 'venda', COUNT(*) FROM academico.venda
UNION ALL SELECT 'item_venda', COUNT(*) FROM academico.item_venda
UNION ALL SELECT 'pagamento', COUNT(*) FROM academico.pagamento;"""