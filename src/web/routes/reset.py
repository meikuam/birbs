from fastapi import APIRouter, Response, status

from src.web.models.controller import ControllerIds
from src.web.models.drinker import Drinker

from src.controller.controller_api import controller_api
from src.controller.serial_api import reset_serial

reset_router = APIRouter()

@reset_router.post("/serial")
async def reset_serial_controller_endpoint():
    # we open serial port and it resets controller
    if reset_serial():
        return Response(status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@reset_router.post("/spi")
async def reset_spi_controller_endpoint():
    # we send order 66 command to controller and it does software reset
    try:
        controller_api.controller_reset()
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
