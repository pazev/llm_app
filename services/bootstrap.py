"""
One-time DB bootstrap: create default roles and a
seed admin user if no users exist yet.

Called at app startup; safe to run repeatedly.
"""

import os

from db.session import get_db
from repositories.user_repository import UserRepository

DEFAULT_ROLES = ["user", "business_admin", "admin"]
SEED_USERNAME = os.environ.get(
    "SEED_ADMIN_USERNAME", "admin"
)
SEED_PASSWORD = os.environ.get(
    "SEED_ADMIN_PASSWORD", "changeme1"
)
SEED_EMAIL = os.environ.get(
    "SEED_ADMIN_EMAIL", "admin@localhost"
)


def bootstrap() -> None:
    with get_db() as db:
        repo = UserRepository(db)
        for role_name in DEFAULT_ROLES:
            repo.get_or_create_role(role_name)
        if not repo.list_all():
            repo.create(
                username=SEED_USERNAME,
                email=SEED_EMAIL,
                password=SEED_PASSWORD,
                roles=DEFAULT_ROLES,
            )
