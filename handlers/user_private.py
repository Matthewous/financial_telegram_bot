from aiogram import types, Router
from aiogram.filters.command import Command

from keyboards import reply

user_private_router = Router()

# Обработчик команды /start
@user_private_router.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Добро пожаловать!", reply_markup=reply.start_kb)

# Эхо
@user_private_router.message(Command('menu'))
async def main_menu_command(message: types.Message):
    await message.answer('Меню!')


