from aiogram import Bot,Dispatcher,types
from aiogram.filters.command import Command
from decouple import config
import asyncio

from handlers.user_private import user_private_router
from common.bot_commands import private

# import logging
# Включаем логирование, чтобы не пропустить важные сообщения
# logging.basicConfig(level=logging.INFO)

ALLOWED_UPDATES = ['message','edited_message']

bot = Bot(token=config('TOKEN'))
dp = Dispatcher() ### фильтрация сообщений от пользователей

dp.include_router(user_private_router)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)  ### пропускаем обновления, полученные, пока бот не работал
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats()) ### обозначение команд главного меню
    await dp.start_polling(bot,allowed_updates=ALLOWED_UPDATES) ### Запуск polling

if __name__ == '__main__':
    asyncio.run(main())
