import os
import tempfile
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.utils import executor
from photo_frame import add_frame

import logging

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message()
async def handle_photo_with_caption(message: Message):
    if not message.photo or not message.caption:
        await message.reply("❗ Пожалуйста, отправьте одно фото с подписью из трёх строк:\n\n<цвет>\n<толщина>\n<соотношение>")
        return

    # Проверка и парсинг настроек
    lines = message.caption.strip().splitlines()
    if len(lines) != 3:
        await message.reply("❗ Подпись должна содержать ровно три строки:\n<цвет>\n<толщина>\n<соотношение>")
        return

    color, thickness, aspect = lines

    # Скачиваем фото
    photo = message.photo[-1]
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.jpg")
            output_path = os.path.join(tmpdir, "output.jpg")

            await photo.download_to_disk(input_path)
            try:
                add_frame(input_path, output_path, color, thickness, aspect)
            except Exception as e:
                await message.reply(f"❗ Ошибка обработки: {e}")
                return

            await message.reply_photo(types.FSInputFile(output_path), caption="✅ Готово!")
    except Exception:
        await message.reply("❗ Не удалось скачать или обработать изображение.")


if __name__ == "__main__":
    from aiogram import executor
    from aiogram import Router

    router = Router()
    dp.include_router(router)
    executor.start_polling(dp, skip_updates=True)
