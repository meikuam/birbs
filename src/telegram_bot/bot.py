from typing import List
import numpy as np
import io
# import skimage.io as skio
from PIL import Image
import numpy as np

from aiogram import Bot, types
from src.utils import settings


bot = Bot(token=settings.telegram["token"])

chat_ids = [112643306]

async def get_chat_ids() -> List[int]:
    updates = await bot.get_updates()
    return [update.message.chat.id for update in updates]


async def send_message(chat_id: int, text: str):
    await bot.send_message(chat_id, text)


async def send_image(chat_id: int, image: np.ndarray):
    await bot.send_chat_action(chat_id, types.chat.ChatActions.UPLOAD_PHOTO)
    buffered = io.BytesIO()

    img = Image.fromarray(image)
    img.save(buffered, format="PNG")
    buffered.seek(0)
    await bot.send_photo(
        chat_id=chat_id,
        photo=buffered,
        caption='none'
    )

async def broadcast_message(chat_ids: List[int], text: str):
    for chat_id in chat_ids:
        await send_message(chat_id, text)


async def broadcast_image(chat_ids: List[int], image: np.ndarray):
    for chat_id in chat_ids:
        await send_image(chat_id, image)
