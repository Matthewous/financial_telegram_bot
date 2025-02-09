import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Portfolio
from tests.conftest import async_session
from datetime import date

@pytest.mark.asyncio
async def test_orm_add_portfolio(async_session: AsyncSession):
    portfolio_data = {
        "name": "Test Portfolio",
        "description": "Test Description",
        "initial_summ": 100000.0,
        "start_date": date(2023, 1, 1)  # Преобразуем в datetime.date
    }

    portfolio = Portfolio(name=portfolio_data["name"], description=portfolio_data["description"],initial_summ=portfolio_data["initial_summ"], start_date=portfolio_data["start_date"])

    async_session.add(portfolio)
    await async_session.commit()
    await async_session.refresh(portfolio)

    assert portfolio.id is not None
    assert portfolio.name == portfolio_data["name"]

    await async_session.delete(portfolio)
    await async_session.commit()

@pytest.mark.asyncio
async def test_orm_get_portfolio(async_session: AsyncSession):
    # First, create a portfolio
    portfolio = Portfolio(name="Test Portfolio", description="Test Description", initial_summ=100000, start_date=date(2023, 1, 1))  # Преобразуем в datetime.date
    async_session.add(portfolio)
    await async_session.commit()
    await async_session.refresh(portfolio)
    portfolio_id = portfolio.id

    # Now, retrieve the portfolio
    retrieved_portfolio = await async_session.get(Portfolio, portfolio_id)

    assert retrieved_portfolio is not None
    assert retrieved_portfolio.name == "Test Portfolio"

    # Clean up
    await async_session.delete(retrieved_portfolio)
    await async_session.commit()

@pytest.mark.asyncio
async def test_orm_update_portfolio(async_session: AsyncSession):
    # First, create a portfolio
    portfolio = Portfolio(name="Test Portfolio", description="Test Description", initial_summ=100000, start_date=date(2023, 1, 1))  # Преобразуем в datetime.date
    async_session.add(portfolio)
    await async_session.commit()
    await async_session.refresh(portfolio)
    portfolio_id = portfolio.id

    # Now, update the portfolio
    new_name = "Updated Portfolio Name"
    portfolio.name = new_name
    await async_session.commit()

    # Retrieve the updated portfolio and assert it has the new name
    updated_portfolio = await async_session.get(Portfolio, portfolio_id)
    assert updated_portfolio is not None
    assert updated_portfolio.name == new_name

    # Clean up
    await async_session.delete(updated_portfolio)
    await async_session.commit()

@pytest.mark.asyncio
async def test_orm_delete_portfolio(async_session: AsyncSession):
    # First, create a portfolio
    portfolio = Portfolio(name="Test Portfolio", description="Test Description", initial_summ=100000, start_date=date(2023, 1, 1))  # Преобразуем в datetime.date
    async_session.add(portfolio)
    await async_session.commit()
    await async_session.refresh(portfolio)
    portfolio_id = portfolio.id

    # Now, delete the portfolio
    await async_session.delete(portfolio)
    await async_session.commit()

    # Try to retrieve the portfolio and assert it is None
    deleted_portfolio = await async_session.get(Portfolio, portfolio_id)
    assert deleted_portfolio is None

@pytest.mark.asyncio
async def test_get_portfolio_structure(async_session: AsyncSession):
    # Создайте моковые объекты
    portfolio = Portfolio(name="Test Portfolio", description="Test Description", initial_summ=100000, start_date=date(2023, 1, 1))  # Преобразуем в datetime.date
    async_session.add(portfolio)
    await async_session.commit()
    await async_session.refresh(portfolio)

    #  Здесь нужно добавить логику для создания и связывания Stock и Portfolio_Stocks
    #  Пример:
    # stock = Stock(ticker="TEST")
    # async_session.add(stock)
    # await async_session.commit()
    # await async_session.refresh(stock)
    # portfolio_stock = Portfolio_Stocks(portfolio_id=portfolio.id, stock_id=stock.id, share=0.5)
    # async_session.add(portfolio_stock)
    # await async_session.commit()

    # Вызовите функцию get_portfolio_structure
    # result = await get_portfolio_structure(async_session, portfolio.id)

    #  Добавьте проверки, что result содержит ожидаемые данные

    # Очистка
    await async_session.delete(portfolio)
    # await async_session.delete(stock) #если добавляли stock
    await async_session.commit()