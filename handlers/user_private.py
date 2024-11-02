from aiogram import types, Router, F
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards import reply
from database.orm_queries import orm_add_portfolio, orm_get_portfolios, orm_delete_portfolio
from keyboards.inline import get_allback_buttons

user_private_router = Router()




class AddPortfolio(StatesGroup):
    name = State()
    description = State()
    tickers = State()


# Обработчик команды /start
@user_private_router.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Добро пожаловать!", reply_markup=reply.start_kb)

# Эхо
@user_private_router.message(Command('menu'))
async def main_menu_command(message: types.Message):
    await message.answer('Меню!')

# Меню управления портфелями
@user_private_router.message(F.text == 'Портфели')
async def main_menu_command(message: types.Message):
    await message.answer('Портфели!', reply_markup=reply.main_portfolio_kb)

# Меню создания портфеля
@user_private_router.message(StateFilter(None), F.text == 'Создать портфель')
async def portfolio_add_name_command(message: types.Message, state:FSMContext):
    await message.answer('Введите название портфеля! Для отмены создания портфеля напишите "отмена" на любом этапе', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddPortfolio.name)
    print("State set to AddPortfolio.name")  # Отладочное сообщение

# Хэндлер для сброса состояния
@user_private_router.message(StateFilter('*'), Command('отмена'))
@user_private_router.message(StateFilter('*'), F.text.casefold() == 'отмена')
async def cancel_handler(message: types.Message, state:FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer('Действия отменены', reply_markup=reply.start_kb)

# TODO хэндлер назад

# Сохранение описания портфеля
@user_private_router.message(StateFilter(AddPortfolio.name))
async def portfolio_add_description_command(message: types.Message, state:FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Введите описание портфеля!')
    await state.set_state(AddPortfolio.description)

# Сохранение структуры портфеля
@user_private_router.message(StateFilter(AddPortfolio.description))
async def set_portfolio_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите тикеры и их доли в формате: Тикер1 Доля1, Тикер2 Доля2 (например, YNDX 0.5, SBER 0.3)")
    await state.set_state(AddPortfolio.tickers)

# Завершение создания портфеля
@user_private_router.message(StateFilter(AddPortfolio.tickers))
async def set_portfolio_tickers(message: types.Message, state: FSMContext, session: AsyncSession):
    tickers_data = message.text.split(",")
    tickers = []
    for ticker_data in tickers_data:
        try:
            ticker, share = ticker_data.strip().split()
            tickers.append({"ticker": ticker, "share": float(share)})
        except ValueError:
            await message.answer("Ошибка ввода. Убедитесь, что формат правильный: Тикер1 Доля1, Тикер2 Доля2")
            return
    
    await state.update_data(tickers=tickers)
    data = await state.get_data()
    
    try:
        await orm_add_portfolio(session, data)
        await message.answer(f'Портфель создан!',reply_markup=reply.main_portfolio_kb)
    except Exception as e:
        await message.answer(f'Ошибка: \n{str(e)}',reply_markup=reply.main_portfolio_kb)
    
    await state.clear()


# Меню обзора портфелей
@user_private_router.message(F.text == 'Выбрать портфель')
async def portfolios_query_command(message: types.Message, session: AsyncSession):
    await message.answer('Ваши портфели:')
    for portfolio in await orm_get_portfolios(session):
        await message.answer(
            f'Название: {portfolio.name}\nОписание: {portfolio.description}',
            reply_markup=get_allback_buttons(btns={
                'Удалить': f'delete_portfolio_{portfolio.id}',
                'Изменить': f'change_ortfolio_{portfolio.id}',
                'Выбрать': f'select_ortfolio_{portfolio.id}',
                })
        )

# Удаление портфеля
@user_private_router.callback_query(F.data.startswith('delete_portfolio_'))
async def delete_portfolio_command(callback: types.CallbackQuery, session: AsyncSession):
    portfolio_id = callback.data.split('_')[-1]
    await orm_delete_portfolio(session,int(portfolio_id))
    await callback.answer(f'Портфель удален')
    # await callback.message.answer(f'Портфель удален')






# # Сохранение тикеров и завершение создания портфеля
# @user_private_router.message(state=PortfolioCreation.waiting_for_tickers)
# async def set_portfolio_tickers(message: types.Message, state: FSMContext, session: Session):
#     tickers_data = message.text.split(",")
#     tickers = []
#     for ticker_data in tickers_data:
#         try:
#             ticker, share = ticker_data.strip().split()
#             tickers.append({"ticker": ticker, "share": float(share)})
#         except ValueError:
#             await message.answer("Ошибка ввода. Убедитесь, что формат правильный: Тикер1 Доля1, Тикер2 Доля2")
#             return

#     # Достаем данные из FSMContext и сохраняем в базу данных
#     user_data = await state.get_data()
#     user_id = message.from_user.id

#     with session() as db_session:
#         # Проверка, зарегистрирован ли пользователь
#         user = db_session.query(User).filter_by(telegram_id=user_id).first()
#         if not user:
#             user = User(telegram_id=user_id)
#             db_session.add(user)
#             db_session.commit()

#         # Создание и сохранение портфеля
#         portfolio = Portfolio(user_id=user.id, name=user_data["name"], description=user_data["description"])
#         db_session.add(portfolio)
#         db_session.commit()

#         # Сохранение тикеров
#         for ticker_data in tickers:
#             stock = Stock(portfolio_id=portfolio.id, ticker=ticker_data["ticker"], share=ticker_data["share"])
#             db_session.add(stock)
#         db_session.commit()

#     await message.answer("Портфель успешно создан!", reply_markup=reply.main_portfolio_kb)
#     await state.clear()