import asyncio
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from photo_frame import FrameSettings, process_photo

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Нет TELEGRAM_BOT_TOKEN в переменных окружения!")
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_settings = {}


def get_user_settings(user_id: int) -> FrameSettings:
    return user_settings.setdefault(user_id, FrameSettings())


def get_settings_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="📐 Соотношение", callback_data="set_ratio")
    builder.button(text="🧱 Толщина", callback_data="set_thickness")
    builder.button(text="🎨 Цвет", callback_data="set_color")
    builder.adjust(2, 1)

    return builder.as_markup()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_settings[message.from_user.id] = FrameSettings()
    await message.answer(
        "👋 Привет! Отправь фото, чтобы добавить рамку. Настройки можно изменить ниже:",
        reply_markup=get_settings_keyboard(),
    )


@dp.message(F.photo)
async def handle_photo(message: Message):
    user_id = message.from_user.id
    settings = get_user_settings(user_id)

    photo = await message.photo[-1].download(destination=bytes)
    result_io = await process_photo(photo, settings)

    await bot.send_photo(
        chat_id=user_id,
        photo=result_io,
        caption="✅ Готово! Можешь изменить настройки и отправить следующее фото.",
        reply_markup=get_settings_keyboard()
    )


@dp.callback_query(F.data == "set_ratio")
async def choose_ratio(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    for label in ["square", "portrait", "story", "landscape"]:
        builder.button(text=label, callback_data=f"ratio:{label}")
    builder.adjust(2, 2)
    await callback.message.edit_text("Выбери соотношение сторон:", reply_markup=builder.as_markup())


@dp.callback_query(F.data.startswith("ratio:"))
async def set_ratio(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    ratio = callback.data.split(":")[1]
    get_user_settings(user_id).aspect_ratio = ratio
    await callback.message.edit_text(
        f"✅ Соотношение установлено: {ratio}", reply_markup=get_settings_keyboard()
    )


@dp.callback_query(F.data == "set_thickness")
async def choose_thickness(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    for label in ["2%", "5%", "10%", "20px", "50px", "100px"]:
        builder.button(text=label, callback_data=f"thickness:{label}")
    builder.adjust(3, 3)
    await callback.message.edit_text("Выбери толщину рамки:", reply_markup=builder.as_markup())


@dp.callback_query(F.data.startswith("thickness:"))
async def set_thickness(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    thickness = callback.data.split(":")[1]
    get_user_settings(user_id).border_thickness = thickness
    await callback.message.edit_text(
        f"✅ Толщина установлена: {thickness}", reply_markup=get_settings_keyboard()
    )


@dp.callback_query(F.data == "set_color")
async def ask_color_input(callback: types.CallbackQuery):
    await callback.message.answer("🎨 Введите цвет в формате `#RRGGBB` или название (например, red):")


@dp.message(F.text)
async def handle_color_or_error(message: types.Message):
    text = message.text.strip()
    user_id = message.from_user.id

    if text.startswith("#") or text.lower() in {"red", "white", "black", "blue", "green", "yellow"}:
        try:
            get_user_settings(user_id).border_color = text
            await message.answer(f"✅ Цвет установлен: {text}", reply_markup=get_settings_keyboard())
        except Exception:
            await message.answer("❌ Неверный формат цвета. Пример: `#ffcc00` или `green`")
    else:
        await message.answer("❓ Я не понимаю это сообщение. Пожалуйста, отправь фото или настройку.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
