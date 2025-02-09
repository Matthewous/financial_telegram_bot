# tests/test_services_portfolio_analisys.py
import pytest
from datetime import date
from services.portfolio_analisys import calculate_portfolio_performance
from unittest.mock import patch
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Portfolio, Stock, Portfolio_Stocks

@pytest.mark.asyncio
async def test_calculate_portfolio_performance(async_session: AsyncSession):
    # Создайте моковые объекты портфеля и акций
    portfolio = Portfolio(name="Test Portfolio", description="Test Description", initial_summ=100000, start_date=date(2024, 12, 2))

    async_session.add(portfolio)
    await async_session.commit()
    await async_session.refresh(portfolio)

    stock1 = Stock(ticker="LKOH")
    stock2 = Stock(ticker="AFLT")
    async_session.add(stock1)
    async_session.add(stock2)
    await async_session.commit()
    await async_session.refresh(stock1)
    await async_session.refresh(stock2)

    portfolio_stock1 = Portfolio_Stocks(portfolio_id=portfolio.id, stock_id=stock1.id, share=0.5)
    portfolio_stock2 = Portfolio_Stocks(portfolio_id=portfolio.id, stock_id=stock2.id, share=0.5)
    async_session.add(portfolio_stock1)
    async_session.add(portfolio_stock2)
    await async_session.commit()
    await async_session.refresh(portfolio_stock1)
    await async_session.refresh(portfolio_stock2)
    # Mock the fetch_shares_quotes function
    async def mock_fetch_shares_quotes(start_date: str, end_date: str, ticker: str):
        if ticker == "LKOH":
            return [{"date": "2024-12-02", "close_price": 6826.5}, {"date": "2024-12-03", "close_price": 6758.5}]
        elif ticker == "AFLT":
            return [{"date": "2024-12-02", "close_price": 50.61}, {"date": "2024-12-03", "close_price": 49.04}]
        return []

    # Use patch to replace the real function with the mock
    with patch("services.portfolio_analisys.fetch_shares_quotes", side_effect=mock_fetch_shares_quotes):
        # Call the function with mocked data
        start_date = date(2024, 12, 2)
        end_date = date(2024, 12, 3)
        performance = await calculate_portfolio_performance(async_session, portfolio, start_date, end_date)

    # Add assertions to check the result
    assert isinstance(performance, list)
    assert len(performance) == 2
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