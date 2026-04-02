"""add message_context json column to messages

Revision ID: 07a6ff0a3fbb
Revises: 7d6125b5a2ca
Create Date: 2026-03-30 17:58:29.497941

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '07a6ff0a3fbb'
down_revision: Union[str, Sequence[str], None] = '7d6125b5a2ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('messages') as batch_op:
        batch_op.add_column(sa.Column('message_context', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('messages') as batch_op:
        batch_op.drop_column('message_context')
