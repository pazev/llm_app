from typing import List
from pydantic import BaseModel, ConfigDict, field_validator


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role_id: int
    name: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    roles: List[str] = []

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError(
                "username must not be empty"
            )
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError(
                "password must be at least 8 chars"
            )
        return v


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str
    email: str
    is_active: bool
    roles: List[RoleResponse] = []

    def has_role(self, *names: str) -> bool:
        """Return True if user has any of the
        given role names."""
        user_roles = {r.name for r in self.roles}
        return bool(user_roles & set(names))


class LoginSubmit(BaseModel):
    username: str
    password: str


class ChangePasswordSubmit(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError(
                "password must be at least 8 chars"
            )
        return v

    def passwords_match(self) -> bool:
        return self.new_password == self.confirm_password
