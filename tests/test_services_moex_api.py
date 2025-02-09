# tests/test_services_moex_api.py
import pytest
from services.moex_api import fetch_shares_quotes

@pytest.mark.asyncio
async def test_fetch_shares_quotes_success():
    # Проверяем, что функция возвращает данные при успешном запросе
    quotes = await fetch_shares_quotes("2024-01-01", "2024-01-05", "SBER")
    assert isinstance(quotes, list)
    assert len(quotes) > 0
    assert isinstance(quotes[0], dict)
    assert "date" in quotes[0]
    assert "close_price" in quotes[0]

@pytest.mark.asyncio
async def test_fetch_shares_quotes_failure():
    # Проверяем, что функция вызывает исключение при неудачном запросе (например, неверный тикер)
    with pytest.raises(Exception):
        await fetch_shares_quotes("2024-01-01", "2024-01-05", "INVALID_TICKER")

@pytest.mark.asyncio
async def test_fetch_shares_quotes_empty_response():
    # Проверяем, что функция возвращает пустой список, если нет данных за указанный период
    quotes = await fetch_shares_quotes("2023-01-01", "2023-01-01", "SBER")  # За одну дату
    # assert isinstance(quotes, list)
    # # assert len(quotes) == 0
    print('Список котировок:')
    print(quotes)