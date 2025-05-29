import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F
from aiohttp import web

from photo_frame import process_image_from_message, parse_settings, InvalidSettingsError

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- Ручка, чтобы Render видел порт ---
async def handle(request):
    return web.Response(text="Bot is running.")

async def start_http_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=int(os.getenv("PORT", 10000)))
    await site.start()

# --- Обработка сообщений с фото и подписью ---
@dp.message(F.photo & F.caption)
async def handle_photo_with_caption(message: Message):
    try:
        photo = message.photo[-1]
        settings_text = message.caption.strip()
        settings = parse_settings(settings_text)

        output_path = await process_image_from_message(photo, settings)
        await message.reply_photo(types.FSInputFile(output_path), caption="Готово!")
        os.remove(output_path)

    except InvalidSettingsError as e:
        await message.reply(f"Ошибка настроек: {e}")
    except Exception as e:
        await message.reply(f"Ошибка обработки: {e}")

@dp.message()
async def handle_invalid_input(message: Message):
    await message.reply("Пожалуйста, пришлите одно фото с подписью, содержащей настройки:\n\n"
                        "Пример:\n#ffcc00\n10%\n4:5")

# --- Основной запуск ---
async def main():
    await start_http_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
