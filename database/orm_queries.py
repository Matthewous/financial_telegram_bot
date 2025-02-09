import io
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import joinedload

from database.models import PortfolioGraph, User, Portfolio, Stock, Portfolio_Stocks

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


async def save_graph_to_db(session: AsyncSession, graph_buf: io.BytesIO):
    # Читаем данные из графика в бинарный формат
    graph_data = graph_buf.read()

    # Создаем объект модели
    graph_record = PortfolioGraph(graph_data=graph_data)

    # Сохраняем график в базу данных
    session.add(graph_record)
    await session.commit()

    return graph_record.id  # Возвращаем ID сохраненного графика

async def get_graph_from_db(session: AsyncSession, graph_id: int):
    # Извлекаем график по ID
    result = await session.execute(select(PortfolioGraph).filter_by(id=graph_id))
    graph_record = result.scalars().first()

    if graph_record:
        # Создаем BufferedInputFile из бинарных данных
        graph_buf = io.BytesIO(graph_record.graph_data)
        graph_buf.seek(0)
        return graph_buf
    return None

async def delete_graph_from_db(session: AsyncSession, graph_id: int):
    # Извлекаем график по ID
    result = await session.execute(select(PortfolioGraph).filter_by(id=graph_id))
    graph_record = result.scalars().first()

    if graph_record:
        # Удаляем график из базы данных
        await session.delete(graph_record)
        await session.commit()