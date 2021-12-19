from fastapi import APIRouter, Response, status

from src.controller.controller_api import controller_api
from src.web.models.leds import Leds

leds_router = APIRouter()


@leds_router.get("/", response_model=Leds)
async def get_leds_state_endpoint():
    state, value = controller_api.leds_get()
    return Leds(
        state=state,
        value=value
    )


@leds_router.post("/")
async def set_leds_state_endpoint(leds: Leds):
    if leds.state is not None:
        controller_api.leds_status_set(leds.state)
    if leds.value is not None:
        controller_api.leds_value_set(leds.value)
    return Response(status_code=status.HTTP_200_OK)
