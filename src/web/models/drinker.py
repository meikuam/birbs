from typing import Optional
from pydantic import BaseModel

class Drinker(BaseModel):
    drinker_input_angle: Optional[int]
    drinker_output_angle: Optional[int]
    drinker_water_level_current: Optional[int]
    drinker_empty_flag: Optional[bool]
    drinker_fill_flag: Optional[bool]
    drinker_input_open_angle: Optional[int]
    drinker_input_close_angle: Optional[int]
    drinker_output_open_angle: Optional[int]
    drinker_output_close_angle: Optional[int]
    water_level_measure_iterations: Optional[int]
    water_level_max_cm_distance: Optional[int]
    water_level_max_level: Optional[int]
    water_level_min_level: Optional[int]


    # def create_update_dict(self):
    #     return self.dict(exclude_unset=True)
