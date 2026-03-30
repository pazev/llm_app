"""sender string, drop unique constraint on feedback

Revision ID: 7d6125b5a2ca
Revises: 1aee85319616
Create Date: 2026-03-30 12:06:31.615116

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d6125b5a2ca'
down_revision: Union[str, Sequence[str], None] = '1aee85319616'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Batch mode required for SQLite to support constraint/column changes via copy-and-move
    with op.batch_alter_table('message_feedback') as batch_op:
        batch_op.drop_constraint('uq_message_feedback_message_id', type_='unique')

    with op.batch_alter_table('messages') as batch_op:
        batch_op.alter_column('sender',
                              existing_type=sa.VARCHAR(length=4),
                              type_=sa.String(length=10),
                              existing_nullable=False)


def downgrade() -> None:
    with op.batch_alter_table('messages') as batch_op:
        batch_op.alter_column('sender',
                              existing_type=sa.String(length=10),
                              type_=sa.VARCHAR(length=4),
                              existing_nullable=False)

    with op.batch_alter_table('message_feedback') as batch_op:
        batch_op.create_unique_constraint('uq_message_feedback_message_id', ['message_id'])
