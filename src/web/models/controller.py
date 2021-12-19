from typing import List
from pydantic import BaseModel


class ControllerIds(BaseModel):
    controller_ids: List[int]