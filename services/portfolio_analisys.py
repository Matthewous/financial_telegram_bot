from datetime import datetime
from typing import List, Dict
import pandas as pd
import matplotlib.pyplot as plt
import io

from requests import session

from database.models import Portfolio_Stocks
from database.orm_queries import delete_graph_from_db, get_graph_from_db, get_portfolio_structure, save_graph_to_db
from services.moex_api import fetch_shares_quotes
from common.bot_config import bot


from typing import List, Dict
import pandas as pd
from sqlalchemy.orm import joinedload
from aiogram.types import BufferedInputFile

# def calculate_portfolio_performance(portfolio, start_date: str, end_date: str, session) -> List[Dict]:
#     portfolio_performance = []

#     # Получаем котировки для каждой акции в портфеле
#     stock_quotes = {}
#     for portfolio_stock in portfolio.stocks:
#         ticker = portfolio_stock.stock.ticker
#         quotes = fetch_shares_quotes(start_date, end_date, ticker)
#         stock_quotes[ticker] = quotes

#     # Определяем начальную стоимость портфеля на Start_date
#     total_initial_value = 0
#     stock_weights = {}

#     # Загружаем все необходимые данные о портфеле и его акциях
#     portfolio_stocks = session.query(Portfolio_Stocks).filter(Portfolio_Stocks.portfolio_id == portfolio.id).all()

#     for portfolio_stock in portfolio_stocks:
#         ticker = portfolio_stock.stock.ticker
#         share = portfolio_stock.share
        
#         # Находим начальную цену акции на start_date
#         initial_price = next((quote['close_price'] for quote in stock_quotes[ticker] if quote['date'] == start_date), None)
#         if initial_price:
#             stock_weights[ticker] = share * initial_price
#             total_initial_value += stock_weights[ticker]

#     # Рассчитываем динамику портфеля
#     for date in pd.date_range(start=start_date, end=end_date):
#         total_value = 0
#         for portfolio_stock in portfolio_stocks:
#             ticker = portfolio_stock.stock.ticker
#             share = portfolio_stock.share
            
#             # Получаем цену акции на текущую дату
#             price_on_date = next((quote['close_price'] for quote in stock_quotes[ticker] if quote['date'] == date.strftime("%Y-%m-%d")), None)
#             if price_on_date:
#                 total_value += share * price_on_date
        
#         # Вычисляем доходность портфеля на текущую дату
#         performance = {
#             "date": date.strftime("%Y-%m-%d"),
#             "portfolio_value": total_value,
#             "return": (total_value - total_initial_value) / total_initial_value * 100
#         }
#         portfolio_performance.append(performance)

#     return portfolio_performance

def preprocess_quotes(stock_quotes):
    """
    Функция для предобработки котировок и приведения всех дат к формату YYYY-MM-DD.
    Также удаляет котировки с некорректными датами.
    """
    for ticker, quotes in stock_quotes.items():
        for quote in quotes:
            try:
                # Преобразуем строку даты в объект datetime в формате YYYY-MM-DD
                quote['date'] = datetime.strptime(quote['date'], "%Y-%m-%d").date()
            except ValueError:
                # Если дата некорректна, выводим предупреждение
                print(f"Warning: Invalid date format for {ticker} on {quote['date']}")
                # Удаляем некорректную котировку
                stock_quotes[ticker].remove(quote)
    return stock_quotes

def get_close_price_on_date(stock_quotes, ticker, date):
    # Получаем котировки для заданного тикера
    quotes = stock_quotes.get(ticker)
    
    if quotes:
        # Ищем котировку на указанную дату
        for quote in quotes:
            if quote['date'] == date:
                return quote['close_price']
    return None

async def calculate_portfolio_performance(session, portfolio, start_date: str, end_date: str) -> List[Dict]:
    portfolio_performance = []
    print(f'ИД портфеля: {portfolio.id}')
    portfolio_structure = await get_portfolio_structure(session, portfolio.id)
    print('---------------------')
    print(portfolio_structure)
    print('---------------------')
    
    # Получаем котировки для каждой акции в портфеле
    stock_quotes = {}
    for portfolio_stock in portfolio_structure:
        ticker = portfolio_stock.stock.ticker
        print(ticker)
        quotes = fetch_shares_quotes(start_date, end_date, ticker)
        stock_quotes[ticker] = quotes

    # Предобрабатываем котировки, приводя все даты к единому формату
    stock_quotes = preprocess_quotes(stock_quotes)
    print('---------------------')
    print(stock_quotes)
    print('---------------------')
    # Определяем начальную стоимость портфеля на Start_date
    total_initial_value = 0
    stock_weights = {}
    stock_initial_prices = {}

    # Проходим по всем записям в связи "Portfolio_Stocks" через фильтрацию по portfolio_id
    for portfolio_stock in portfolio_structure:
        ticker = portfolio_stock.stock.ticker
        share = portfolio_stock.share
        print(f"Processing stock: {ticker}, Shares: {share}")  # Логируем данные по акции
        
        # Находим начальную цену акции на start_date
        initial_price = get_close_price_on_date(stock_quotes, ticker, start_date)
        print('---------------------')
        print(f"Initial {ticker} value on {start_date}: {initial_price}")
        print('---------------------')
        if initial_price:
            stock_initial_prices[ticker] = initial_price
            stock_weights[ticker] = portfolio.initial_summ * float(share)
            print(f"stock_weights {ticker}: {stock_weights[ticker]}")
            total_initial_value += stock_weights[ticker]

    # Логирование начальной стоимости
    print(f"Initial portfolio value on {start_date}: {total_initial_value}")
    print('---------------------')

    last_prices = {ticker: None for ticker in stock_quotes} # Для хранения последней доступной цены
    # Рассчитываем динамику портфеля
    for date in pd.date_range(start=start_date, end=end_date):
        # print(f'Date for plt: {date}')
        date = datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S').date()
        total_value = 0
        for portfolio_stock in portfolio_structure:
            ticker = portfolio_stock.stock.ticker
            
            # Получаем цену акции на текущую дату
            price_on_date = get_close_price_on_date(stock_quotes, ticker, date)
            if price_on_date:
                last_prices[ticker] = price_on_date
                total_value += stock_weights[ticker] * float(price_on_date) / stock_initial_prices[ticker]
            else:
                total_value += stock_weights[ticker] * float(last_prices[ticker]) / stock_initial_prices[ticker]

        # Вычисляем доходность портфеля на текущую дату
        performance = {
            "date": date.strftime("%Y-%m-%d"),
            "portfolio_value": total_value,
            "return": (total_value - total_initial_value) / total_initial_value * 100
        }
        portfolio_performance.append(performance)
        print(performance)

    return portfolio_performance


# def calculate_portfolio_performance(portfolio, start_date: str, end_date: str) -> List[Dict]:
#     portfolio_performance = []
    
#     # Получаем котировки для каждой акции в портфеле
#     stock_quotes = {}
#     for portfolio_stock in portfolio.stocks:
#         ticker = portfolio_stock.stock.ticker
#         quotes = fetch_shares_quotes(start_date, end_date, ticker)
#         stock_quotes[ticker] = quotes

#     # Определяем начальную стоимость портфеля на Start_date
#     total_initial_value = 0
#     stock_weights = {}

#     for portfolio_stock in portfolio.stocks:
#         ticker = portfolio_stock.stock.ticker
#         share = portfolio_stock.share
#         initial_price = next((quote['close_price'] for quote in stock_quotes[ticker] if quote['date'] == start_date), None)
#         if initial_price:
#             stock_weights[ticker] = share * initial_price
#             total_initial_value += stock_weights[ticker]

#     # Рассчитываем динамику портфеля
#     for date in pd.date_range(start=start_date, end=end_date):
#         total_value = 0
#         for portfolio_stock in portfolio.stocks:
#             ticker = portfolio_stock.stock.ticker
#             share = portfolio_stock.share
#             # Получаем цену акции на текущую дату
#             price_on_date = next((quote['close_price'] for quote in stock_quotes[ticker] if quote['date'] == date.strftime("%Y-%m-%d")), None)
#             if price_on_date:
#                 total_value += share * price_on_date
        
#         performance = {
#             "date": date.strftime("%Y-%m-%d"),
#             "portfolio_value": total_value,
#             "return": (total_value - total_initial_value) / total_initial_value * 100
#         }
#         portfolio_performance.append(performance)

#     return portfolio_performance

async def plot_portfolio_performance(message, portfolio_performance):
    dates = [perf['date'] for perf in portfolio_performance]
    values = [perf['portfolio_value'] for perf in portfolio_performance]

    plt.figure(figsize=(10, 6))
    plt.plot(dates, values, label="Динамика портфеля")
    plt.xlabel('Дата')
    plt.ylabel('Стоимость портфеля')
    plt.title('Динамика стоимости портфеля')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    # plt.show()

    # Сохраняем график в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    # from common.bot_config import bot
    # await bot.send_photo(message.chat.id, BufferedInputFile(buf, filename="portfolio_performance.png"))
    graph_id = await save_graph_to_db(session, buf)

    # Загружаем график из базы данных
    graph_file = await get_graph_from_db(session, graph_id)

    if graph_file:
        # Отправляем изображение
        await bot.send_photo(chat_id=message.chat.id, photo=open(graph_file, 'rb'))

        # Удаляем график из базы данных после отправки
        await delete_graph_from_db(session, graph_id)
    else:
        print('Файл не найден!')

    return buf

