from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    tenant_id: str
    created_at: datetime


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str = ""
    role: str = "analyst"
