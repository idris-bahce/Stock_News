import requests
import smtplib
from dotenv import load_dotenv
import os

load_dotenv()

account_sid = os.getenv("account_sid")
auth_token = os.getenv("auth_token")
API_KEY_NEWS = os.getenv("API_KEY_NEWS")
API_KEY_STOCK = os.getenv("API_KEY_STOCK")
MY_TEL_NU = os.getenv("MY_TEL_NU")
MY_EMAIL = os.getenv("MY_EMAIL")
MY_PASSWORD = os.getenv("MY_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

STOCK = "AMPS"
COMPANY_NAME = "Altus Power Inc"
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
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday...
def is_5_percent_changed():
    if -4 >= percentage_change or 4 <= percentage_change:
        return True
    else:
        return False


# STEP 2: Use https://newsapi.org
# Get the first 3 news pieces for the COMPANY_NAME.
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

    return f"{STOCK}: {percentage_change}%\nHeadline1: {news1} url:{news1_url}\nHeadline2: {news2} url:" \
           f"{news2_url}\nHeadline3: {news3} url:{news3_url}\n "


# STEP 3: Use https://www.twilio.com
# Send a separate message with the percentage change and each article's title and description to your phone number.
def send_message():
    news = take_news()
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=MY_PASSWORD)
        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=TO_EMAIL,
            msg=f"Subject:NEWS about your stock! \n\nThere have been a change in your stock."
                f" Here is the news:\n{news}: "
        )


if is_5_percent_changed():
    send_message()
