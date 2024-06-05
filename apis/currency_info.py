import requests

def get_exchange_rate(base_currency, target_currency):
    api_key = "YOUR_EXCHANGE_RATE_API_KEY"
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
    response = requests.get(url)
    data = response.json()
    exchange_rate = data["conversion_rates"].get(target_currency)
    if exchange_rate:
        return {"base_currency": base_currency, "target_currency": target_currency, "rate": exchange_rate}
    else:
        return {"error": "Currency not found"}

if __name__ == "__main__":
    base_currency = "USD"
    target_currency = "EUR"
    exchange_rate = get_exchange_rate(base_currency, target_currency)
    if "error" not in exchange_rate:
        print(f"Exchange rate from {base_currency} to {target_currency}: {exchange_rate['rate']}")
    else:
        print(exchange_rate["error"])
