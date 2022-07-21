from typing import List
import numpy as np
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from src.utils import settings


bot = Bot(token=settings.telegram["token"])


async def get_chat_ids() -> List[int]:
    updates = await bot.get_updates()
    return [update.message.chat.id for update in updates]


async def send_message(chat_id: int, text: str):
    await bot.send_message(chat_id, text)


async def send_image(chat_id: int, image: np.ndarray):
    await bot.send_chat_action(chat_id, types.chat.ChatActions.UPLOAD_PHOTO)
    image
    with open('img.jpg', 'rb') as file:
        await bot.send_photo(
            chat_id=chat_id,
            photo=file,
            caption='none'
        )