from datetime import datetime

from pydantic import BaseModel, UUID4


class PlanInfoSchema(BaseModel):
    name: str
    price: int
    tokens: int

    model_config = {"from_attributes": True}


class SubscriptionSchema(BaseModel):
    status: str
    expires_at: datetime
    activated_at: datetime
    used_tokens: int
    plan: PlanInfoSchema

    model_config = {
        "from_attributes": True
    }


class BaseUserSchema(BaseModel):
    id: UUID4
    subscription: SubscriptionSchema

    model_config = {
        "from_attributes": True
    }
