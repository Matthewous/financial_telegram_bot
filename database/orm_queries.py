from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from database.models import User, Portfolio, Stock, Portfolio_Stocks

async def orm_add_portfolio(session: AsyncSession, data: dict):
    new_portfolio = Portfolio(
        name = data['name'],
        description = data['description']
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
        description = data['description']
    )
    await session.execute(query)
    await session.commit()

#  Удаление портфеля
async def orm_delete_portfolio(session: AsyncSession, portfolio_id: int):
    query = delete(Portfolio).where(Portfolio.id == portfolio_id)
    await session.execute(query)
    await session.commit()