from pydantic import BaseModel
from datetime import datetime

class HistoryCreate(BaseModel):
    user_id: str
    command: str
    response: str

class HistoryOut(BaseModel):
    user_id: str
    command: str
    response: str
    created_at: datetime
