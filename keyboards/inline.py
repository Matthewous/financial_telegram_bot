from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Инлайновые кнопки с текстом
def get_allback_buttons(
    *,
    btns: dict[str, str, str],
    sizes: tuple[int] = (3,),):

    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
    return keyboard.adjust(*sizes).as_markup()

# Инлайновые кнопки со ссылками
def get_url_buttons(
    *,
    btns: dict[str, str],
    sizes: tuple[int] = (2,),): 

    keyboard = InlineKeyboardBuilder()

    for text, url in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, url=url))
    return keyboard.adjust(*sizes).as_markup()  
