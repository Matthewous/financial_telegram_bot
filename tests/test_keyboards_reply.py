# tests/test_keyboards_reply.py
from keyboards.reply import start_kb, main_portfolio_kb
from aiogram.types import ReplyKeyboardMarkup

def test_start_kb():
    keyboard = start_kb
    assert isinstance(keyboard, ReplyKeyboardMarkup)
    assert len(keyboard.keyboard[0]) == 2  # Две кнопки в первом ряду
    assert keyboard.keyboard[0][0].text == "Портфели"
    assert keyboard.keyboard[0][1].text == "О боте"

def test_main_portfolio_kb():
    keyboard = main_portfolio_kb
    assert isinstance(keyboard, ReplyKeyboardMarkup)
    assert len(keyboard.keyboard[0]) == 2
    assert keyboard.keyboard[0][0].text == "Создать портфель"
    assert keyboard.keyboard[0][1].text == "Выбрать портфель"