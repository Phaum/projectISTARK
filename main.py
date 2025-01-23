import asyncio
from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs


from app.handlers import router, main_window, dialog


async def main():
    bot = Bot(token='7137679858:AAFXnHeXtRONQQ8XIPKm5dzVwEXEZEhd8zc')
    dp = Dispatcher()
    dp.include_router(router)
    dp.include_router(dialog)
    setup_dialogs(dp)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot is offline')
