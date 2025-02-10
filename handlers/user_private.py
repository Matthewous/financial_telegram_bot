from logging import config
from aiogram import types, Router, F
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, or_f
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from aiogram.types import BufferedInputFile, InputFile, InputMediaPhoto

from common.bot_functions import send_graph_func
from database.models import Portfolio
from keyboards import reply
from database.orm_queries import delete_graph_from_db, get_graph_from_db, orm_add_portfolio, orm_get_portfolios, orm_delete_portfolio, orm_get_portfolio, orm_update_portfolio, save_graph_to_db
from keyboards.inline import get_allback_buttons, portfolio_analysis_buttons
# from services.moex_api import fetch_shares_quotes
from services.portfolio_analisys import calculate_portfolio_performance, plot_portfolio_performance

user_private_router = Router()

class AddPortfolio(StatesGroup):
    name = State()
    description = State()
    start_date = State()
    tickers = State()
    initial_summ = State()

    portfolio_for_change = None

class PortfolioAnalisys(StatesGroup):
    end_date = State()

    portfolio_for_analisys = None


# Обработчик команды /start
@user_private_router.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Добро пожаловать!", reply_markup=reply.start_kb)

# Эхо
@user_private_router.message(Command('menu'))
async def main_menu_command(message: types.Message):
    await message.answer('Меню!')

# Меню
@user_private_router.message(F.text == 'О боте')
async def main_menu_command(message: types.Message):
    await message.answer('Этот бот умеет сохранять ваши инвестиционные портфели и выдавать инфомрацию по ним на любую дату', reply_markup=reply.start_kb)

# Меню управления портфелями
@user_private_router.message(F.text == 'Портфели')
async def main_menu_command(message: types.Message):
    await message.answer('Портфели!', reply_markup=reply.main_portfolio_kb)

# Изменение портфеля
@user_private_router.callback_query(StateFilter(None),F.data.startswith('change_portfolio_'))
async def change_portfolio_command(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    portfolio_id = callback.data.split('_')[-1]
    portfolio_for_change = await orm_get_portfolio(session, int(portfolio_id))
    
    AddPortfolio.portfolio_for_change = portfolio_for_change
    await callback.answer()
    if AddPortfolio.portfolio_for_change:
        await callback.message.answer('Вы изменяете портфель! Чтобы оставить поле без изменений введите точку! Для отмены изменений - "отмена"')
    await callback.message.answer('Введите навание портфеля:',reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddPortfolio.name)

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
    if AddPortfolio.portfolio_for_change:
        AddPortfolio.portfolio_for_change = None
    await state.clear()
    await message.answer('Действия отменены', reply_markup=reply.start_kb)

# TODO хэндлер назад

# Сохранение описания портфеля
@user_private_router.message(StateFilter(AddPortfolio.name,or_f(F.text, F.text=='.')))
async def portfolio_add_description_command(message: types.Message, state:FSMContext):
    if message.text and message.text == '.':
        await state.update_data(name=AddPortfolio.portfolio_for_change.name)
    else:
        await state.update_data(name=message.text)
    await message.answer('Введите описание портфеля!')
    await state.set_state(AddPortfolio.description)

# Сохранение cуммы портфеля
@user_private_router.message(StateFilter(AddPortfolio.description,or_f(F.text, F.text=='.')))
async def portfolio_add_initial_summ_command(message: types.Message, state:FSMContext):
    if message.text and message.text == '.':
        await state.update_data(description=AddPortfolio.portfolio_for_change.description)
    else:
        await state.update_data(description=message.text)
    await message.answer('Введите изначальную сумму портфеля!')
    await state.set_state(AddPortfolio.initial_summ)

# Сохранение cуммы портфеля
@user_private_router.message(StateFilter(AddPortfolio.initial_summ,or_f(F.text, F.text=='.')))
async def portfolio_add_start_date_command(message: types.Message, state:FSMContext):
    if message.text and message.text == '.':
        await state.update_data(initial_summ=AddPortfolio.portfolio_for_change.initial_summ)
    else:
        await state.update_data(initial_summ=float(message.text))
    await message.answer('Введите дату фиксации портфеля в формате "ГГГГ-ММ-ДД"!')
    await state.set_state(AddPortfolio.start_date)

# Сохранение структуры портфеля
@user_private_router.message(StateFilter(AddPortfolio.start_date,or_f(F.text, F.text=='.')))
async def set_portfolio_description(message: types.Message, state: FSMContext):
    if message.text and message.text == '.':
        try:
            start_date = datetime.strptime(message.text, "%Y-%m-%d").date()
            await state.update_data(start_date=start_date)
            await message.answer("Введите тикеры и их доли в формате: Тикер1 Доля1, Тикер2 Доля2 (например, YNDX 0.5, SBER 0.5)")
            await state.set_state(AddPortfolio.tickers)
        except ValueError:
            await message.answer('Некорректный формат даты. Попробуйте снова в формате "ГГГГ-ММ-ДД".')
    else:
        try:
            await state.update_data(start_date=datetime.strptime(message.text, "%Y-%m-%d").date())
            await message.answer("Введите тикеры и их доли в формате: Тикер1 Доля1, Тикер2 Доля2 (например, LKOH 0.5, SBER 0.5)")
            await state.set_state(AddPortfolio.tickers)
        except ValueError:
            await message.answer('Некорректный формат даты. Попробуйте снова в формате "ГГГГ-ММ-ДД".')
    

# Завершение создания портфеля
@user_private_router.message(StateFilter(AddPortfolio.tickers,or_f(F.text, F.text=='.')))
async def set_portfolio_tickers(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text and message.text == '.':
        await state.update_data(tickers=AddPortfolio.portfolio_for_change.tickers)
    else:
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
        if AddPortfolio.portfolio_for_change:
            await orm_update_portfolio(session, AddPortfolio.portfolio_for_change.id, data)
            await message.answer(f'Портфель изменен!',reply_markup=reply.main_portfolio_kb)
        else:
            await orm_add_portfolio(session, data)
            await message.answer(f'Портфель создан!',reply_markup=reply.main_portfolio_kb)
    except Exception as e:
        await message.answer(f'Ошибка: \n{str(e)}',reply_markup=reply.main_portfolio_kb)
    
    AddPortfolio.portfolio_for_change = None
    await state.clear()


# Меню обзора портфелей
@user_private_router.message(F.text == 'Выбрать портфель')
async def portfolios_query_command(message: types.Message, session: AsyncSession):
    portfolios = await orm_get_portfolios(session)
    if len(portfolios) == 0:
        await message.answer('У вас нет портфелей!')
    else:
        await message.answer('Ваши портфели:')
        for portfolio in portfolios:
            await message.answer(
                f'Название: {portfolio.name}\nОписание: {portfolio.description}\nИзначальная сумма: {portfolio.initial_summ}\nДата фиксации: {portfolio.start_date}',
                reply_markup=get_allback_buttons(btns={
                    'Удалить': f'delete_portfolio_{portfolio.id}',
                    'Изменить': f'change_portfolio_{portfolio.id}',
                    'Выбрать': f'select_portfolio_{portfolio.id}',
                    })
            )

# Удаление портфеля
@user_private_router.callback_query(F.data.startswith('delete_portfolio_'))
async def delete_portfolio_command(callback: types.CallbackQuery, session: AsyncSession):
    portfolio_id = callback.data.split('_')[-1]
    await orm_delete_portfolio(session,int(portfolio_id))
    await callback.answer(f'Портфель удален')
    await callback.message.answer(f'Портфель удален')

@user_private_router.callback_query(F.data.startswith('select_portfolio_'))
async def portfolio_analisys_command(callback: types.CallbackQuery, state:FSMContext, session: AsyncSession):
    portfolio_id = callback.data.split('_')[-1]
    portfolio_for_analisys = await orm_get_portfolio(session, int(portfolio_id))
    PortfolioAnalisys.portfolio_for_analisys = portfolio_for_analisys
    await callback.message.answer('Выберите дату для анализа в формате "ГГГГ-ММ-ДД"!')
    await state.set_state(PortfolioAnalisys.end_date)

# Обработка ввода даты
@user_private_router.message(StateFilter(PortfolioAnalisys.end_date))
async def handle_end_date(message: types.Message, state: FSMContext, session: AsyncSession):
    from common.bot_config import bot
    if message.text.lower() == 'отмена':
        await message.answer('Операция отменена.')
        await state.finish()
        return

    try:
        # Проверим, что дата введена в правильном формате
        end_date = datetime.strptime(message.text, "%Y-%m-%d").date()
        
        # Получаем портфель из состояния
        portfolio = PortfolioAnalisys.portfolio_for_analisys

        if portfolio.start_date >= end_date: raise IndexError

        # Расчитываем динамику портфеля и доходность на указанную дату
        performance = await calculate_portfolio_performance(session, portfolio, portfolio.start_date, end_date)

        # Отправляем стоимость портфеля и доходность
        total_value = performance[-1]["portfolio_value"]  # Стоимость портфеля на указанную дату
        total_initial_value = performance[0]["portfolio_value"]  # Изначальная стоимость
        portfolio_return = (total_value - total_initial_value) / total_initial_value * 100

        await message.answer(f'Стоимость портфеля на {end_date}: {total_value:.2f} RUB')
        await message.answer(f'Доходность портфеля на {end_date}: {portfolio_return:.2f}%')

        # Строим график динамики стоимости портфеля
        graph_buf = await plot_portfolio_performance(message, performance, session)

        await state.clear()
        
    except ValueError as e:
        await message.answer(f'Неверный формат даты! Пожалуйста, введите дату в формате "ГГГГ-ММ-ДД".')

    except IndexError as e:
        await message.answer(f'Ошибка! Укажите дату, которая больше даты фиксации портфеля!')



# Меню
@user_private_router.message(F.text == 'В главное меню')
async def main_menu_command(message: types.Message):
    await message.answer('Меню!', reply_markup=reply.start_kb)



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