import requests

def get_stock_price(symbol):
    api_key = "YOUR_ALPHAVANTAGE_API_KEY"
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    time_series = data.get("Time Series (5min)", {})
    latest_time = sorted(time_series.keys())[-1] if time_series else None
    if latest_time:
        latest_data = time_series[latest_time]
        stock_price = {
            "symbol": symbol,
            "price": latest_data["1. open"],
            "date": latest_time
        }
        return stock_price
    else:
        return {"error": "Stock symbol not found or API limit reached"}

if __name__ == "__main__":
    symbol = "AAPL"
    stock = get_stock_price(symbol)
    if "error" not in stock:
        print(f"Stock price for {symbol}:")
        print(f"Price: ${stock['price']}")
        print(f"Date: {stock['date']}")
    else:
        print(stock["error"])
