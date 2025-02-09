from aiogram import Bot, Dispatcher
from decouple import config


bot = Bot(token=config('TOKEN'))
dp = Dispatcher() ### фильтрация сообщений от пользователей