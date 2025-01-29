import numpy as np
import io
from PIL import Image

from aiogram import Bot, types
from src.utils import settings


bot = Bot(token=settings.telegram["token"])

chat_ids = [112643306]


async def get_chat_ids() -> list[int]:
    updates = await bot.get_updates()
    return [update.message.chat.id for update in updates]


async def send_message(chat_id: int, text: str):
    await bot.send_message(chat_id, text)


async def send_image(chat_id: int, image: np.ndarray, caption: str = None):
    buffered = io.BytesIO()

    img = Image.fromarray(image)
    img.save(buffered, format="PNG")
    buffered.seek(0)
    buffered_input_file = types.BufferedInputFile(
        buffered.read(),
        filename="image.png"
    )
    await bot.send_photo(
        chat_id=chat_id,
        photo=buffered_input_file,
        caption=caption
    )


async def broadcast_message(chat_ids: list[int], text: str):
    for chat_id in chat_ids:
        await send_message(chat_id, text)


async def broadcast_image(chat_ids: list[int], image: np.ndarray, caption: str = None):
    for chat_id in chat_ids:
        await send_image(chat_id, image, caption)
