import os
import tempfile
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from photo_frame import add_frame

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


@dp.message()
async def handle_photo_with_caption(message: Message):
    if not message.photo or not message.caption:
        await message.reply("❗ Пожалуйста, отправьте одно фото с подписью из трёх строк:\n<цвет>\n<толщина>\n<соотношение>")
        return

    lines = message.caption.strip().splitlines()
    if len(lines) != 3:
        await message.reply("❗ Подпись должна содержать ровно три строки:\n<цвет>\n<толщина>\n<соотношение>")
        return

    color, thickness, aspect = lines

    try:
        photo = message.photo[-1]
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.jpg")
            output_path = os.path.join(tmpdir, "output.jpg")

            await photo.download(destination=input_path)

            try:
                add_frame(input_path, output_path, color, thickness, aspect)
            except Exception as e:
                await message.reply(f"❗ Ошибка обработки: {e}")
                return

            await message.reply_photo(types.FSInputFile(output_path), caption="✅ Готово!")
    except Exception as e:
        await message.reply("❗ Не удалось обработать фото.")
        logging.exception(e)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
