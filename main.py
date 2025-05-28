import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiogram.enums import ParseMode

from photo_frame import add_frame_to_image  # твоя функция из другого файла

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Нет TELEGRAM_BOT_TOKEN в переменных окружения!")
# Логгирование
logging.basicConfig(level=logging.INFO)

# Бот и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилище настроек на пользователя
user_settings = {}


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_settings[message.from_user.id] = {
        "color": "white",
        "thickness": "5%",
        "aspect": "1:1",
        "quality": 95,
    }
    await message.answer("Привет! Отправь фото, а я добавлю рамку.\n"
                         "Настрой: /setcolor /setthickness /setaspect /setquality")


@dp.message(Command("setcolor"))
async def set_color(message: types.Message):
    user_settings[message.from_user.id]["color"] = message.text.split(maxsplit=1)[1]
    await message.answer(f"Цвет рамки установлен: {message.text.split(maxsplit=1)[1]}")


@dp.message(Command("setthickness"))
async def set_thickness(message: types.Message):
    user_settings[message.from_user.id]["thickness"] = message.text.split(maxsplit=1)[1]
    await message.answer(f"Толщина рамки установлена: {message.text.split(maxsplit=1)[1]}")


@dp.message(Command("setaspect"))
async def set_aspect(message: types.Message):
    user_settings[message.from_user.id]["aspect"] = message.text.split(maxsplit=1)[1]
    await message.answer(f"Соотношение сторон установлено: {message.text.split(maxsplit=1)[1]}")


@dp.message(Command("setquality"))
async def set_quality(message: types.Message):
    user_settings[message.from_user.id]["quality"] = int(message.text.split(maxsplit=1)[1])
    await message.answer(f"Качество JPEG установлено: {message.text.split(maxsplit=1)[1]}")


@dp.message(F.photo)
async def handle_photo(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_settings:
        await message.answer("Сначала отправь /start")
        return

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    input_path = f"{user_id}_input.jpg"
    output_path = f"{user_id}_output.jpg"

    await bot.download_file(file.file_path, input_path)

    # Обработка в отдельном потоке
    def process_file():
        add_frame_to_image(
            input_path,
            output_path,
            aspect_ratio=user_settings[user_id]["aspect"],
            border_thickness=user_settings[user_id]["thickness"],
            border_color=user_settings[user_id]["color"],
            quality=user_settings[user_id]["quality"],
        )

    await asyncio.to_thread(process_file)

    # Отправка результата
    output = FSInputFile(output_path)
    await message.answer_photo(output)

    # Удаление временных файлов
    os.remove(input_path)
    os.remove(output_path)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
