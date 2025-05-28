from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import os
from photo_frame import FrameSettings, FrameProcessor

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Нет TELEGRAM_BOT_TOKEN в переменных окружения!")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

settings = FrameSettings()
processor = FrameProcessor(settings)

# Цвета
COLOR_CHOICES = {
    "🔴 Красный": "red",
    "🟢 Зелёный": "green",
    "🔵 Синий": "blue",
    "⚫ Чёрный": "black",
    "⚪ Белый": "white",
    "🟡 Жёлтый": "yellow",
    "🟣 Фиолетовый": "purple",
    "🟤 Коричневый": "brown",
}

# Толщина рамки
THICKNESS_CHOICES = {
    "5%": "5%",
    "10%": "10%",
    "15%": "15%",
    "20%": "20%",
    "30%": "30%",
}

# Соотношения сторон
ASPECT_CHOICES = {
    "1:1 (square)": "square",
    "4:5 (portrait)": "portrait",
    "9:16 (story)": "story",
    "16:9 (landscape)": "landscape",
}

# Качество
QUALITY_CHOICES = {
    "🟢 95 (макс)": 95,
    "🟡 85": 85,
    "🔴 70 (эконом)": 70,
}


# Клавиатуры
def make_kb(options, prefix):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=f"{prefix}:{value}")]
            for label, value in options.items()
        ]
    )


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Привет! Отправь фото, и я добавлю к нему рамку.\n"
        "Ты можешь настроить параметры кнопками ниже:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🎨 Цвет рамки", callback_data="menu:color")],
                [InlineKeyboardButton(text="🧱 Толщина рамки", callback_data="menu:thickness")],
                [InlineKeyboardButton(text="📐 Соотношение сторон", callback_data="menu:aspect")],
                [InlineKeyboardButton(text="📸 Качество JPG", callback_data="menu:quality")],
            ]
        ),
    )


# Команда на установку цвета вручную
@dp.message(Command("setcolor"))
async def cmd_setcolor(message: Message, command: CommandObject):
    color = command.args
    if not color:
        await message.reply("❗ Используй `/setcolor <цвет>` (например: `/setcolor gold`)", parse_mode="Markdown")
        return

    try:
        settings.border_color = color
        await message.reply(f"✅ Цвет рамки установлен: `{color}`", parse_mode="Markdown")
    except Exception as e:
        await message.reply(f"❌ Ошибка цвета: {e}")


# Меню настроек
@dp.callback_query(F.data.startswith("menu:"))
async def open_menu(callback: CallbackQuery):
    menu = callback.data.split(":")[1]
    if menu == "color":
        await callback.message.edit_text("🎨 Выберите цвет рамки:", reply_markup=make_kb(COLOR_CHOICES, "color"))
    elif menu == "thickness":
        await callback.message.edit_text("🧱 Выберите толщину рамки:", reply_markup=make_kb(THICKNESS_CHOICES, "thickness"))
    elif menu == "aspect":
        await callback.message.edit_text("📐 Выберите соотношение сторон:", reply_markup=make_kb(ASPECT_CHOICES, "aspect"))
    elif menu == "quality":
        await callback.message.edit_text("📸 Выберите качество JPEG:", reply_markup=make_kb(QUALITY_CHOICES, "quality"))
    await callback.answer()


# Обработчики inline-настроек
@dp.callback_query(F.data.startswith("color:"))
async def set_color(callback: CallbackQuery):
    color = callback.data.split(":")[1]
    try:
        settings.border_color = color
        await callback.message.edit_text(f"✅ Цвет рамки установлен: <code>{color}</code>", parse_mode=ParseMode.HTML)
    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка цвета: {e}")
    await callback.answer()


@dp.callback_query(F.data.startswith("thickness:"))
async def set_thickness(callback: CallbackQuery):
    value = callback.data.split(":")[1]
    settings.border_thickness = value
    await callback.message.edit_text(f"✅ Толщина рамки установлена: <code>{value}</code>", parse_mode=ParseMode.HTML)
    await callback.answer()


@dp.callback_query(F.data.startswith("aspect:"))
async def set_aspect(callback: CallbackQuery):
    value = callback.data.split(":")[1]
    settings.aspect_ratio = value
    await callback.message.edit_text(f"✅ Соотношение сторон установлено: <code>{value}</code>", parse_mode=ParseMode.HTML)
    await callback.answer()


@dp.callback_query(F.data.startswith("quality:"))
async def set_quality(callback: CallbackQuery):
    value = int(callback.data.split(":")[1])
    settings.quality = value
    await callback.message.edit_text(f"✅ Качество JPEG установлено: <code>{value}</code>", parse_mode=ParseMode.HTML)
    await callback.answer()


# Фото
@dp.message(F.photo)
async def handle_photo(message: Message):
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    photo_bytes = await bot.download_file(file.file_path)

    output = processor.process(photo_bytes)
    await message.reply_document(document=output, caption="✅ Готово! Вот фото с рамкой.")


# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

