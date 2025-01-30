import logging
import numpy as np
import io
from PIL import Image

from aiogram import Bot, types
from src.utils import settings


logger = logging.getLogger(name=__name__)

bot = Bot(token=settings.telegram["token"])

chat_ids = [112643306]


async def get_chat_ids() -> list[int]:
    updates = await bot.get_updates()
    return [update.message.chat.id for update in updates]


async def send_message(chat_id: int, text: str):
    logger.info(f"send message: {chat_id} {text}")
    await bot.send_message(chat_id, text)


async def send_image(chat_id: int, image: np.ndarray, caption: str = None):
    logger.info(f"send image: {chat_id} {caption}")
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


async def log_message(message: str):
    try:
        await broadcast_message(
            chat_ids=chat_ids,
            text=message
        )
    except Exception as e:
        logger.error(f"Error log_message: {message} {e}")


async def log_image(image: np.ndarray,  caption: str = None):
    try:
        await broadcast_image(
            chat_ids=chat_ids,
            image=image,
            caption=caption
        )
    except Exception as e:
        logger.error(f"Error log_image: {caption} {e}")
