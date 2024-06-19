import requests

def get_news():
    api_key = "YOUR_NEWS_API_KEY"
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    response = requests.get(url)
    data = response.json()
    articles = data.get("articles", [])
    news_list = [{"title": article["title"], "description": article["description"]} for article in articles]
    return news_list

if __name__ == "__main__":
    news = get_news()
    for i, article in enumerate(news[:5], start=1):
        print(f"News {i}: {article['title']}")
        print(f"Description: {article['description']}")
        print()
