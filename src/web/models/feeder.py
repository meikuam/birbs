from typing import Optional
from pydantic import BaseModel


class Feeder(BaseModel):
    feeder_box_angle: Optional[int]
    feeder_gate_angle: Optional[int]
    feeder_box_open_angle: Optional[int]
    feeder_box_close_angle: Optional[int]
    feeder_gate_open_angle: Optional[int]
    feeder_gate_close_angle: Optional[int]

    # def create_update_dict(self):
    #     return self.dict(exclude_unset=True)
