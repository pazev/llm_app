"""add_users_roles_and_user_roles_tables

Revision ID: e1f7d300d1ba
Revises: a1953ca7333f
Create Date: 2026-04-20 13:09:20.930014

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'e1f7d300d1ba'
down_revision: Union[str, Sequence[str], None] = (
    'a1953ca7333f'
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column(
            "role_id",
            sa.Integer(),
            primary_key=True,
            index=True,
        ),
        sa.Column(
            "name",
            sa.String(50),
            nullable=False,
            unique=True,
        ),
    )
    op.create_table(
        "users",
        sa.Column(
            "user_id",
            sa.Integer(),
            primary_key=True,
            index=True,
        ),
        sa.Column(
            "username",
            sa.String(100),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "email",
            sa.String(255),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "password_hash",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.create_table(
        "user_roles",
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.user_id"),
            primary_key=True,
        ),
        sa.Column(
            "role_id",
            sa.Integer(),
            sa.ForeignKey("roles.role_id"),
            primary_key=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("user_roles")
    op.drop_table("users")
    op.drop_table("roles")
