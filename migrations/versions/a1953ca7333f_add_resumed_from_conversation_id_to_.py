"""add_resumed_from_conversation_id_to_conversations

Revision ID: a1953ca7333f
Revises: 07a6ff0a3fbb
Create Date: 2026-04-01 01:03:37.009454

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1953ca7333f'
down_revision: Union[str, Sequence[str], None] = '07a6ff0a3fbb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('conversations') as batch_op:
        batch_op.add_column(sa.Column('resumed_from_conversation_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_conversations_resumed_from_conversation_id',
            'conversations',
            ['resumed_from_conversation_id'],
            ['conversation_id'],
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('conversations') as batch_op:
        batch_op.drop_constraint('fk_conversations_resumed_from_conversation_id', type_='foreignkey')
        batch_op.drop_column('resumed_from_conversation_id')
