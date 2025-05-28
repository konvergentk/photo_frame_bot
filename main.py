from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import tempfile
import os
from photo_frame import add_frame_to_image

API_TOKEN = "YOUR_BOT_TOKEN_HERE"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

user_settings = {}

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    user_settings[message.from_user.id] = {
        "aspect_ratio": "1:1",
        "border_thickness": "5%",
        "border_color": "#ffffff",
        "quality": 95,
    }
    await message.answer(
        "Привет! Я добавляю рамку к фотографиям.\n\n"
        "\U0001F4D0 Изменить формат рамки: /ratio\n"
        "\U0001F3A8 Цвет рамки: /color\n"
        "\U0001F4CF Толщина: /thickness\n"
        "\U0001F5DC️ Качество JPEG: /quality\n\n"
        "Теперь просто пришли фото!"
    )

@dp.message_handler(commands=["ratio"])
async def cmd_ratio(message: types.Message):
    await message.answer(
        "Выберите соотношение сторон:\n"
        "\U0001F4F7 /square (1:1)\n"
        "\U0001F4F1 /portrait (4:5)\n"
        "\U0001F4D6 /story (9:16)\n"
        "\U0001F5BC️ /landscape (16:9)"
    )

@dp.message_handler(commands=["square", "portrait", "story", "landscape"])
async def set_preset_ratio(message: types.Message):
    user_id = message.from_user.id
    preset_map = {
        "square": "1:1",
        "portrait": "4:5",
        "story": "9:16",
        "landscape": "16:9",
    }
    preset = message.get_command()[1:]
    user_settings[user_id]["aspect_ratio"] = preset_map[preset]
    await message.answer(f"Соотношение установлено: {preset_map[preset]}")

@dp.message_handler(commands=["thickness"])
async def cmd_thickness(message: types.Message):
    await message.answer("Введите толщину рамки в % или пикселях (например, 5% или 30):")
    user_settings[message.from_user.id]["awaiting"] = "thickness"

@dp.message_handler(commands=["color"])
async def cmd_color(message: types.Message):
    await message.answer("Введите цвет рамки (например, #ffffff, red, rgb(255,0,0)):")
    user_settings[message.from_user.id]["awaiting"] = "color"

@dp.message_handler(commands=["quality"])
async def cmd_quality(message: types.Message):
    await message.answer("Введите качество JPEG (1–100):")
    user_settings[message.from_user.id]["awaiting"] = "quality"

@dp.message_handler(content_types=[types.ContentType.TEXT])
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    setting = user_settings.get(user_id, {}).get("awaiting")

    if not setting:
        return

    value = message.text

    if setting == "thickness":
        user_settings[user_id]["border_thickness"] = value
        await message.answer(f"Толщина установлена: {value}")

    elif setting == "color":
        from PIL import ImageColor
        try:
            ImageColor.getrgb(value)
            user_settings[user_id]["border_color"] = value
            await message.answer(f"Цвет установлен: {value}")
        except:
            await message.answer("Неверный формат цвета. Попробуйте ещё раз.")
            return

    elif setting == "quality":
        try:
            q = int(value)
            if 1 <= q <= 100:
                user_settings[user_id]["quality"] = q
                await message.answer(f"Качество установлено: {q}")
            else:
                await message.answer("Введите значение от 1 до 100.")
                return
        except:
            await message.answer("Введите целое число.")
            return

    user_settings[user_id].pop("awaiting", None)

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    user_id = message.from_user.id
    photo = message.photo[-1]
    settings = user_settings.get(user_id)
    if not settings:
        await message.answer("Пожалуйста, начните с команды /start")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.jpg")
        output_path = os.path.join(tmpdir, "output.jpg")

        await photo.download(destination_file=input_path)

        add_frame_to_image(
            input_path,
            output_path,
            aspect_ratio=settings["aspect_ratio"],
            border_thickness=settings["border_thickness"],
            border_color=settings["border_color"],
            quality=settings["quality"]
        )

        await message.answer_photo(InputFile(output_path))

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
