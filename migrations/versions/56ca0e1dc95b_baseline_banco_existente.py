"""baseline banco existente

Revision ID: 56ca0e1dc95b
Revises: 
Create Date: 2025-12-12 21:53:48.006312

"""

"""
Baseline do banco existente.

Essa migration NÃO cria tabelas.
Ela apenas marca o estado atual do banco
como ponto inicial do Alembic.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56ca0e1dc95b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona UNIQUE na coluna email da tabela funcionario."""
    op.create_unique_constraint(
        "uq_funcionario_email",  # nome do constraint
        "funcionario",           # tabela
        ["email"],               # coluna
        schema="academico"       # schema
    )


def downgrade() -> None:
    """Remove UNIQUE da coluna email da tabela funcionario."""
    op.drop_constraint(
        "uq_funcionario_email",
        "funcionario",
        type_="unique",
        schema="academico"
    )
