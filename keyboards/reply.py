from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Меню'),
            KeyboardButton(text='О боте'),
        ],
        [
            KeyboardButton(text='Портфели'),
            KeyboardButton(text='Структурные продукты'),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите команду',
)

del_kb = ReplyKeyboardRemove()

main_portfolio_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Создать портфель'),
            KeyboardButton(text='Выбрать портфель'),
        ],
        [
            KeyboardButton(text='В главное меню'),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите команду',
)