from fastapi import APIRouter, Response, status, Depends

from src.controller.controller_api import controller_api
from src.web.models.leds import Leds
from src.web.database.user_manager import current_superuser
from src.web.database.users import User

leds_router = APIRouter()


@leds_router.get("/", response_model=Leds)
async def get_leds_state_endpoint(user: User = Depends(current_superuser)):
    state, value = controller_api.leds_get()
    return Leds(
        state=state,
        value=value
    )


@leds_router.post("/")
async def set_leds_state_endpoint(leds: Leds, user: User = Depends(current_superuser)):
    if leds.state is not None:
        controller_api.leds_status_set(leds.state)
    if leds.value is not None:
        controller_api.leds_value_set(leds.value)
    return Response(status_code=status.HTTP_200_OK)
