# tests/test_keyboards_inline.py
from keyboards.inline import get_allback_buttons, portfolio_analysis_buttons
from aiogram.types import InlineKeyboardMarkup

def test_get_allback_buttons():
    buttons = {"Button 1": "data1", "Button 2": "data2"}
    keyboard = get_allback_buttons(btns=buttons)
    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard[0]) == 2
    assert keyboard.inline_keyboard[0][0].text == "Button 1"
    assert keyboard.inline_keyboard[0][0].callback_data == "data1"
    assert keyboard.inline_keyboard[0][1].text == "Button 2"
    assert keyboard.inline_keyboard[0][1].callback_data == "data2"

def test_portfolio_analysis_buttons():
    keyboard = portfolio_analysis_buttons()
    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard[0]) == 3  # Теперь 3 кнопки
    assert keyboard.inline_keyboard[0][0].text == "Динамика портфеля"
    assert keyboard.inline_keyboard[0][0].callback_data == "portfolio_performance"
    assert keyboard.inline_keyboard[0][1].text == "Доходность портфеля"
    assert keyboard.inline_keyboard[0][1].callback_data == "portfolio_return"
    assert keyboard.inline_keyboard[0][2].text == "Динамика акций"
    assert keyboard.inline_keyboard[0][2].callback_data == "stocks_performance"