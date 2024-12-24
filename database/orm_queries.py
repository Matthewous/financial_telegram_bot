from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import joinedload

from database.models import User, Portfolio, Stock, Portfolio_Stocks

async def orm_add_portfolio(session: AsyncSession, data: dict):
    new_portfolio = Portfolio(
        name = data['name'],
        description = data['description'],
        initial_summ = data['initial_summ'],
        start_date = data['start_date'],
    )
    
    session.add(new_portfolio)
    await session.commit()

# Получение портфелей
async def orm_get_portfolios(session: AsyncSession):
    query = select(Portfolio)
    result = await session.execute(query)
    return result.scalars().all()

#  Получение портфеля
async def orm_get_portfolio(session: AsyncSession, portfolio_id: int):
    query = select(Portfolio).where(Portfolio.id == portfolio_id)
    result = await session.execute(query)
    return result.scalar()

#  Изменение портфеля
# TODO Добавить изменение параметров акций
async def orm_update_portfolio(session: AsyncSession, portfolio_id: int, data):
    query = update(Portfolio).where(Portfolio.id == portfolio_id).values(
        name = data['name'],
        description = data['description'],
        initial_summ = data['initial_summ'],
        start_date = data['start_date']
    )
    await session.execute(query)
    await session.commit()

#  Удаление портфеля
async def orm_delete_portfolio(session: AsyncSession, portfolio_id: int):
    query = delete(Portfolio).where(Portfolio.id == portfolio_id)
    await session.execute(query)
    await session.commit()

# выбрать даты для получения инфы по портфелю
async def get_portfolio_income(session: AsyncSession, portfolio_id: int):
    portfolio_query = orm_get_portfolio(portfolio_id)

# # Получить структуру портфеля
# async def get_portfolio_structure(session: AsyncSession, portfolio_id: int):
#     query = select(Portfolio_Stocks).where(Portfolio_Stocks.portfolio_id == portfolio_id)
#     result = await session.execute(query)
#     return result.scalars().all()

# # Получить структуру портфеля (синхронная версия)
# def get_portfolio_structure(session: Session, portfolio_id: int):
#     # Выполняем синхронный запрос для получения данных
#     query = select(Portfolio_Stocks).where(Portfolio_Stocks.portfolio_id == portfolio_id)
#     result = session.execute(query)
#     return result.scalars().all()

# Асинхронная версия функции получения структуры портфеля
async def get_portfolio_structure(session: AsyncSession, portfolio_id: int):
    query = select(Portfolio_Stocks).where(Portfolio_Stocks.portfolio_id == portfolio_id).options(joinedload(Portfolio_Stocks.stock))
    result = await session.execute(query)  # Асинхронный запрос
    portfolio_structure = result.scalars().all()
    
    print(f"Portfolio structure for portfolio_id {portfolio_id}: {portfolio_structure}")  # Логирование результата
    
    return portfolio_structure