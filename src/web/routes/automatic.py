from typing import Optional, Tuple
import datetime
from fastapi import APIRouter, Response, status, Depends

from src.web.models.automatic import AutomaticDrinker, AutomaticFeeder, AutomaticFeederFeedTimes
from src.web.database.user_manager import current_superuser
from src.web.database.users import User
from src.automatic.automatic import blade_runner

automatic_router = APIRouter()


@automatic_router.get("/{controller_id}/drinker", response_model=AutomaticDrinker)
async def get_state_drinker_endpoint(controller_id: int, user: User = Depends(current_superuser)):
    updater = blade_runner.drinkers.get(controller_id, None)
    if updater:
        return updater.state
    else:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)


@automatic_router.post("/{controller_id}/drinker")
async def set_state_drinker_endpoint(
        controller_id: int,
        automatic_drinker: AutomaticDrinker,
        user: User = Depends(current_superuser)
):
    try:
        updater = blade_runner.drinkers.get(controller_id, None)
        if updater:
            await updater.update_state(automatic_drinker)
            return Response(status_code=status.HTTP_200_OK)
        else:
            return Response(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@automatic_router.get("/{controller_id}/feeder", response_model=Tuple[AutomaticFeeder, AutomaticFeederFeedTimes])
async def get_state_feeder_endpoint(controller_id: int, user: User = Depends(current_superuser)):
    updater = blade_runner.feeders.get(controller_id, None)
    if updater:
        return [updater.state, AutomaticFeederFeedTimes(feed_times=updater.feed_times)]
    else:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)


@automatic_router.post("/{controller_id}/feeder")
async def set_state_feeder_endpoint(
        controller_id: int,
        automatic_feeder: AutomaticFeeder,
        user: User = Depends(current_superuser)
):
    try:
        updater = blade_runner.feeders.get(controller_id, None)
        if updater:
            print(automatic_feeder)
            await updater.update_state(automatic_feeder)
            return Response(status_code=status.HTTP_200_OK)
        else:
            return Response(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
