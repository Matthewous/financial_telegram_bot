from aiogram import Bot,Dispatcher,types,executor
from aiogram.filters.command import Command
from decouple import config
import asyncio
import logging

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config('TOKEN'))
dp = Dispatcher()

@dp.message_handler(commands=['start'])
async def start_command(message=types.Message):
    await message.reply('Привет! Я - бот!')


if __name__ == '__main__':
    asyncio.run(start_command)