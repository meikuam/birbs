from typing import Optional
from pydantic import BaseModel


class Leds(BaseModel):
    state: Optional[bool]
    value: Optional[int]