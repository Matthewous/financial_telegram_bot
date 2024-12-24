import requests
from typing import List, Dict

def fetch_shares_quotes(start_date: str, end_date: str, ticker: str) -> List[Dict]:
    BASE_URL = f"https://iss.moex.com/iss/history/engines/stock/markets/shares/securities/{ticker}.json"
    
    params = {
        "from": start_date,
        "till": end_date,
        "marketprice_board": 1
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        raise Exception(f"Не удалось получить данные для {ticker} с {start_date} по {end_date}")

    data = response.json()

    # Преобразуем данные в удобный формат
    quotes = []
    for row in data['history']['data']:
        date = row[1]  # TRADEDATE
        close_price = float(row[9])  # CLOSE
        quotes.append({"date": date, "close_price": close_price})

    return quotes