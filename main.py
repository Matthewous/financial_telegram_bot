from aiogram import Bot,Dispatcher,types
from aiogram.filters.command import Command
from decouple import config
import asyncio

from database.engine import create_db, drop_db, session_maker
from middlewares.database import DataBaseSession
from handlers.user_private import user_private_router
from common.bot_commands import private

from common.bot_config import bot, dp
# import logging
# Включаем логирование, чтобы не пропустить важные сообщения
# logging.basicConfig(level=logging.INFO)

# ALLOWED_UPDATES = ['message','edited_message', 'callback_query']




dp.include_router(user_private_router)


async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()
    await create_db()
    print('Бот начал работу')

async def on_shutdown(bot):
    print('Бот завершил работу')

async def main():

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)  ### пропускаем обновления, полученные, пока бот не работал
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats()) ### обозначение команд главного меню
    await dp.start_polling(bot,allowed_updates=dp.resolve_used_update_types()) ### Запуск polling

if __name__ == '__main__':
    asyncio.run(main())
