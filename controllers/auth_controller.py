from typing import List, Optional

from db.session import get_db
from repositories.user_repository import UserRepository
from schemas.user import (
    ChangePasswordSubmit,
    LoginSubmit,
    UserCreate,
    UserResponse,
)


class AuthController:
    def login(
        self, username: str, password: str
    ) -> Optional[UserResponse]:
        dto = LoginSubmit(
            username=username, password=password
        )
        with get_db() as db:
            user = UserRepository(db).authenticate(
                dto.username, dto.password
            )
            if user is None:
                return None
            return UserResponse.model_validate(user)

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        roles: List[str],
    ) -> UserResponse:
        dto = UserCreate(
            username=username,
            email=email,
            password=password,
            roles=roles,
        )
        with get_db() as db:
            user = UserRepository(db).create(
                username=dto.username,
                email=dto.email,
                password=dto.password,
                roles=dto.roles,
            )
            return UserResponse.model_validate(user)

    def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
        confirm_password: str,
    ) -> tuple[bool, str]:
        dto = ChangePasswordSubmit(
            current_password=current_password,
            new_password=new_password,
            confirm_password=confirm_password,
        )
        if not dto.passwords_match():
            return False, "New passwords do not match."
        with get_db() as db:
            repo = UserRepository(db)
            user = repo.get_by_id(user_id)
            if user is None:
                return False, "User not found."
            authenticated = repo.authenticate(
                user.username, dto.current_password
            )
            if authenticated is None:
                return (
                    False,
                    "Current password is incorrect.",
                )
            repo.update_password(user, dto.new_password)
            return True, "Password changed successfully."

    def reset_password(
        self, user_id: int, new_password: str
    ) -> None:
        with get_db() as db:
            repo = UserRepository(db)
            user = repo.get_by_id(user_id)
            if user is None:
                raise ValueError("User not found.")
            repo.update_password(user, new_password)

    def list_users(self) -> List[UserResponse]:
        with get_db() as db:
            users = UserRepository(db).list_all()
            return [
                UserResponse.model_validate(u)
                for u in users
            ]

    def set_user_roles(
        self, user_id: int, roles: List[str]
    ) -> UserResponse:
        with get_db() as db:
            repo = UserRepository(db)
            user = repo.get_by_id(user_id)
            repo.assign_roles(user, roles)
            return UserResponse.model_validate(user)

    def set_user_active(
        self, user_id: int, active: bool
    ) -> None:
        with get_db() as db:
            repo = UserRepository(db)
            user = repo.get_by_id(user_id)
            repo.set_active(user, active)
