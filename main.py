import requests
from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

account_sid = os.getenv("account_sid")
auth_token = os.getenv("auth_token")
API_KEY_NEWS = os.getenv("API_KEY_NEWS")
API_KEY_STOCK = os.getenv("API_KEY_STOCK")
MY_TEL_NU = os.getenv("MY_TEL_NU")

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
url_stock = "https://www.alphavantage.co/query"
parameters_stock = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK,
    "apikey": API_KEY_STOCK
}


url_news = "https://newsapi.org/v2/everything"
parameters_news = {
    "q": COMPANY_NAME,
    "apiKey": API_KEY_NEWS,
    "language": "en",
    "sortBy": "publishedAt",
    "searchIn": "title,content"
}

response_stock = requests.get(url_stock, params=parameters_stock)
response_stock.raise_for_status()
data = response_stock.json()["Time Series (Daily)"]
two_day_data = []  # 0. value will be yesterday and 1. value will be the day before that
i = 0  # With this integer we will take two of the dictionaries and leave the loop.
for key in data:
    two_day_data.append(data[key])
    i += 1
    if i == 2:
        break

close_of_yesterday = float(two_day_data[0]["4. close"])
close_of_day_before_yesterday = float(two_day_data[1]["4. close"])
percentage_change = ((close_of_yesterday - close_of_day_before_yesterday) / close_of_day_before_yesterday) * 100


# STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
def is_5_percent_changed():
    if -5 >= percentage_change or 5 <= percentage_change:
        return False
    else:
        return True


# STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
def take_news():
    response_news = requests.get(url_news, params=parameters_news)
    response_news.raise_for_status()
    data_news = response_news.json()["articles"]
    three_data_for_news = []  # 0. value will be yesterday and 1. value will be the day before that
    k = 0  # With this integer we will take two of the dictionaries and leave the loop.
    for dic in data_news:
        three_data_for_news.append(dic)
        k += 1
        if k == 3:
            break
    news1 = three_data_for_news[0]["title"]
    news1_url = three_data_for_news[0]["url"]
    news2 = three_data_for_news[1]["title"]
    news2_url = three_data_for_news[1]["url"]
    news3 = three_data_for_news[2]["title"]
    news3_url = three_data_for_news[2]["url"]

    return f"TSLA: {round(percentage_change)}%\nHeadline1: {news1} url:{news1_url}\nHeadline2: {news2} url:{news2_url}" \
           f"\nHeadline3: {news3} url:{news3_url}\n "


# STEP 3: Use https://www.twilio.com
# Send a separate message with the percentage change and each article's title and description to your phone number.
def send_message():
    client = Client(account_sid, auth_token)
    message = client.messages \
        .create(
            body=take_news(),
            from_='+16073605918',
            to=MY_TEL_NU
        )
    print(message.status)


if is_5_percent_changed():
    send_message()
