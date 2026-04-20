from typing import List, Optional

from sqlalchemy.orm import Session

from db.models.user import Role, User
from services.auth import hash_password, verify_password


class UserRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_role(self, name: str) -> Optional[Role]:
        return (
            self._session.query(Role)
            .filter(Role.name == name)
            .first()
        )

    def get_or_create_role(self, name: str) -> Role:
        role = self.get_role(name)
        if role is None:
            role = Role(name=name)
            self._session.add(role)
            self._session.flush()
        return role

    def list_roles(self) -> List[Role]:
        return self._session.query(Role).all()

    def create(
        self,
        username: str,
        email: str,
        password: str,
        roles: List[str],
    ) -> User:
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
        )
        for role_name in roles:
            user.roles.append(
                self.get_or_create_role(role_name)
            )
        self._session.add(user)
        self._session.flush()
        return user

    def get_by_id(
        self, user_id: int
    ) -> Optional[User]:
        return self._session.get(User, user_id)

    def get_by_username(
        self, username: str
    ) -> Optional[User]:
        return (
            self._session.query(User)
            .filter(User.username == username)
            .first()
        )

    def authenticate(
        self, username: str, password: str
    ) -> Optional[User]:
        user = self.get_by_username(username)
        if user is None or not user.is_active:
            return None
        if not verify_password(
            password, user.password_hash
        ):
            return None
        return user

    def update_password(
        self, user: User, new_password: str
    ) -> None:
        user.password_hash = hash_password(
            new_password
        )
        self._session.flush()

    def list_all(self) -> List[User]:
        return self._session.query(User).all()

    def set_active(
        self, user: User, active: bool
    ) -> None:
        user.is_active = active
        self._session.flush()

    def assign_roles(
        self, user: User, role_names: List[str]
    ) -> None:
        user.roles = [
            self.get_or_create_role(n)
            for n in role_names
        ]
        self._session.flush()
