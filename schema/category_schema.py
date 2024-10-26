from pydantic import BaseModel
from datetime import datetime

class CategoryCreate(BaseModel):
    category_name: str

class CategoryResponse(BaseModel):
    category_id: int
    category_name: str
    date_added: datetime
    update_date: datetime


class RemoveCategoryResponse(BaseModel):
    message: str