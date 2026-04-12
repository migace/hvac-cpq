from pydantic import BaseModel


class OrderCodeResponse(BaseModel):
    order_code: str