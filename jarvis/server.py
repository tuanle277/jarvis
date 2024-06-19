from flask import Flask, request, jsonify
from modules.voice_recognition import recognize_speech
from modules.talk import speak
from modules.chatbot import get_response

from apis.weather_info import get_weather
from apis.news_info import get_news
from apis.stock_info import get_stock_price
from apis.currency_info import get_exchange_rate

app = Flask(__name__)

@app.route('/jarvis', methods=['POST'])
def jarvis():
    command = recognize_speech()
    if command:
        response_text = get_response(command)
        
        # Example commands processing
        if "weather" in command:
            city = command.split("in")[-1].strip()
            weather = get_weather(city)
            if "error" not in weather:
                response_text = f"Weather in {city}: {weather['description']} at {weather['temperature']}°C, Humidity: {weather['humidity']}%, Wind Speed: {weather['wind_speed']} m/s"
            else:
                response_text = weather["error"]

        elif "news" in command:
            news = get_news()
            response_text = "Here are the top 5 news headlines: "
            for i, article in enumerate(news[:5], start=1):
                response_text += f"{i}. {article['title']} "

        elif "stock price" in command:
            symbol = command.split("price of")[-1].strip().upper()
            stock = get_stock_price(symbol)
            if "error" not in stock:
                response_text = f"Stock price for {symbol}: ${stock['price']} on {stock['date']}"
            else:
                response_text = stock["error"]

        elif "exchange rate" in command:
            parts = command.split("to")
            base_currency = parts[0].split("from")[-1].strip().upper()
            target_currency = parts[-1].strip().upper()
            exchange_rate = get_exchange_rate(base_currency, target_currency)
            if "error" not in exchange_rate:
                response_text = f"Exchange rate from {base_currency} to {target_currency}: {exchange_rate['rate']}"
            else:
                response_text = exchange_rate["error"]
        
        speak(response_text)
        return jsonify({"response": response_text})
    else:
        return jsonify({"response": "I didn't catch that. Please try again."})

if __name__ == "__main__":
    app.run(debug=True)
