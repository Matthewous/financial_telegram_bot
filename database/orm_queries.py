from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Portfolio, Stock, Portfolio_Stocks

async def orm_add_portfolio(session: AsyncSession, data: dict):
    new_portfolio = Portfolio(
        name = data['name'],
        description = data['description']
    )
    
    session.add(new_portfolio)
    await session.commit()