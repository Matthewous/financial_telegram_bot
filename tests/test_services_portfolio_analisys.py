import pytest
from datetime import date
from services.portfolio_analisys import calculate_portfolio_performance
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Portfolio, Stock, Portfolio_Stocks

@pytest.mark.asyncio
async def test_calculate_portfolio_performance(async_session: AsyncSession):
    # Create mock portfolio and stock objects
    portfolio = Portfolio(name="Test Portfolio", description="Test Description", initial_summ=100000, start_date=date(2024, 12, 2))

    async_session.add(portfolio)
    await async_session.commit()
    await async_session.refresh(portfolio)
   
    # Helper function to get or create a Stock
    async def get_or_create_stock(ticker: str):
        result = await async_session.execute(select(Stock).where(Stock.ticker == ticker))
        stock = result.scalar_one_or_none()
        if not stock:
            stock = Stock(ticker=ticker)
            async_session.add(stock)
            await async_session.commit()
            await async_session.refresh(stock)
        return stock

    stock1 = await get_or_create_stock("LKOH")
    stock2 = await get_or_create_stock("AFLT")

    portfolio_stock1 = Portfolio_Stocks(portfolio_id=portfolio.id, stock_id=stock1.id, share=0.5)
    portfolio_stock2 = Portfolio_Stocks(portfolio_id=portfolio.id, stock_id=stock2.id, share=0.5)
    async_session.add(portfolio_stock1)
    async_session.add(portfolio_stock2)
    await async_session.commit()
    await async_session.refresh(portfolio_stock1)
    await async_session.refresh(portfolio_stock2)
    # Mock the fetch_shares_quotes function

    # Call the function with mocked data
    start_date = date(2024, 12, 2)
    end_date = date(2024, 12, 3)
    performance = await calculate_portfolio_performance(async_session, portfolio, start_date, end_date)

    # Add assertions to check the result
    assert isinstance(performance, list)
    assert len(performance) > 0
    assert isinstance(performance[0], dict)
    assert "date" in performance[0]
    assert "portfolio_value" in performance[0]
    assert "return" in performance[0]

    # Clean up
    await async_session.delete(portfolio_stock1)
    await async_session.delete(portfolio_stock2)
    await async_session.delete(stock1)
    await async_session.delete(stock2)
    await async_session.delete(portfolio)
    await async_session.commit()