from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import relationship

from db.base import Base


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id",
        Integer,
        ForeignKey("users.user_id"),
        primary_key=True,
    ),
    Column(
        "role_id",
        Integer,
        ForeignKey("roles.role_id"),
        primary_key=True,
    ),
)


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(
        Integer, primary_key=True, index=True
    )
    name = Column(
        String(50), unique=True, nullable=False
    )

    users = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
    )


class User(Base):
    __tablename__ = "users"

    user_id = Column(
        Integer, primary_key=True, index=True
    )
    username = Column(
        String(100), unique=True, nullable=False
    )
    email = Column(
        String(255), unique=True, nullable=False
    )
    password_hash = Column(
        String(255), nullable=False
    )
    is_active = Column(
        Boolean, default=True, nullable=False
    )

    roles = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
    )
