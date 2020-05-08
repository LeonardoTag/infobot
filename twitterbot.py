from __future__ import with_statement

import contextlib
import datetime
import html
import re
import sys
import time

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

try:
    import requests
except ImportError:
    raise Exception("Requests não instalado. (pip3 install requests)")

try:
    import tweepy
except ImportError:
    raise Exception("Tweepy não instalado. (pip3 install tweepy)")

try:
    import pytz
except ImportError:
    raise Exception("Pytz não instalado. (pip3 install pytz)")


def shorten_url(url):
    """
    Takes an url and returns it shortened.
    """
    request_url = "http://tinyurl.com/api-create.php?" + urlencode({"url": url})
    with contextlib.closing(urlopen(request_url)) as response:
        return response.read().decode("utf-8")


def authenticate():
    """
    Returns an authenticated twitter api object.
    """
    API_KEY = "XXX"
    API_SECRET_KEY = "XXX"
    ACCESS_TOKEN = "XXX"
    ACCESS_TOKEN_SECRET = "XXX"

    authentication = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
    authentication.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    return tweepy.API(authentication)


def tweet(message):
    """
    Takes a message and tweets it.
    """
    api = authenticate()

    api.update_status(status=message)


def reply(message, username, status_id):
    """
    Takes a message, an username and a status id and replies it with the message.
    """
    api = authenticate()

    api.update_status(
        status="@" + username + "\n" + message, in_reply_to_status_id=status_id
    )


def get_my_last_tweet_id():
    """
    Returns the Twitter account's last tweet's id.
    """
    api = authenticate()

    for _ in range(3):
        try:
            last_tweet = api.user_timeline(id=api.me().id, count=1)[0]
        except IndexError:
            time.sleep(3)
            continue
        else:
            break
    else:
        raise Exception("O último tweet não foi achado.")

    return last_tweet.id


def get_currencies():
    """
    Returns a string with some currencies' prices in reais.
    """
    CURRENCIES = {
        "1 USD": "https://dolarhoje.com/",
        "1 EUR": "https://dolarhoje.com/euro-hoje/",
        "1 GBP": "https://dolarhoje.com/libra-hoje/",
        "1 BTC": "https://dolarhoje.com/bitcoin-hoje/",
        "1 NANO": "https://dolarhoje.com/nano-hoje/",
        "1 g de ouro": "https://dolarhoje.com/ouro-hoje/",
    }

    PATTERN = re.compile(r"id=\"nacional\" value=\"(\d+,\d\d)\"")

    final_text = ""

    for currency, link in CURRENCIES.items():
        response = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        value = re.search(PATTERN, response.text).group(1)
        final_text += f"{currency}  -  R${value}\n"

    return final_text


def get_stock_indexes():
    """
    Returns a string with some stocks' share prices.
    """
    INDEXES = {
        "IBOVESPA (BRL)": "https://br.investing.com/indices/bovespa",
        "EWZ (USD)": "https://br.investing.com/etfs/ishares-brazil-index",
        "S&P 500 (USD)": "https://br.investing.com/indices/us-spx-500",
        "DIA (USD)": "https://br.investing.com/etfs/diamonds-trust",
        "Brent Oil (USD)": "https://br.investing.com/commodities/brent-oil-opinion/",
    }

    PATTERN = re.compile(
        r"<td id=\"_last_\d+\" class=\"pid-\d+-last\">(\d+(\.\d+)*,\d\d)<\/td>"
    )
    PATTERN_2 = re.compile(
        r"<span class=(.*?)(green|red)Font(.*?)((\+|-)\d+(\.\d+)*,\d\d)(.*?)<\/span>"
    )
    PATTERN_3 = re.compile(
        r"<span class=(.*?)(green|red)Font(.*?)((\+|-)\d+(\.\d+)*,\d\d%)(.*?)<\/span>"
    )

    final_text = ""

    for index, link in INDEXES.items():
        response = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        value = re.search(PATTERN, response.text).group(1)
        change = re.search(PATTERN_2, response.text).group(4)
        change_percentage = re.search(PATTERN_3, response.text).group(4)
        final_text += f"{index}  -  {value} ({change} | {change_percentage})\n"

    return final_text


def get_the_wall_street_journal():
    """
    Returns a list with the website's top 5 news' link and title.
    """
    PATTERN = re.compile(r"<a class=\"\" href=\"(.+?)\">([^<>]+?)<\/a>")

    response = requests.get(
        "https://www.wsj.com/", headers={"User-Agent": "Mozilla/5.0"}
    )
    response.raise_for_status()
    matches = re.findall(PATTERN, response.text)

    text_list = list()

    for i in range(5):
        url = matches[i][0]
        short_url = shorten_url(url)
        text = html.unescape(matches[i][1])
        if len(text) >= 100:
            text = text[:98] + "..."
        text_list.append(f"{text}\n\n{short_url}")

    return text_list


def get_the_economist():
    """
    Returns a list with the website's top 5 news' link and title.
    """
    PATTERN = re.compile(
        r"<a class=\"headline-link\" href=\"(.+?)\"><span.*?>(.+?)<\/span><\/a>"
    )

    response = requests.get(
        "https://economist.com", headers={"User-Agent": "Mozilla/5.0"}
    )
    response.raise_for_status()
    matches = re.findall(PATTERN, response.text)

    text_list = list()

    for i in range(5):
        url = "https://economist.com" + matches[i][0]
        short_url = shorten_url(url)
        text = html.unescape(matches[i][1])
        if len(text) >= 100:
            text = text[:98] + "..."
        text_list.append(f"{text}\n\n{short_url}")

    return text_list


def get_o_antagonista():
    """
    Returns a list with the website's top 5 news' link and title.
    """
    PATTERN = re.compile(
        r"<div class=\"article_link\">.*\n.*<a href=\"(.+?)\" title=\"(.+?)\".*class=\"link_post\">"
    )

    response = requests.get(
        "https://www.oantagonista.com", headers={"User-Agent": "Mozilla/5.0"}
    )
    response.raise_for_status()
    matches = re.findall(PATTERN, response.text)

    text_list = list()

    for i in range(5):
        url = matches[i][0]
        short_url = shorten_url(url)
        text = html.unescape(matches[i][1])
        if len(text) >= 100:
            text = text[:98] + "..."
        text_list.append(f"{text}\n\n{short_url}")

    return text_list


def get_insurgere():
    """
    Returns a list with the website's top 5 news' link and title.
    """
    PATTERN = re.compile(
        r"<h2 class=\"entry-title\"><a href=\"(.+?)\" rel=\"bookmark\">(.+?)<\/a><\/h2>"
    )

    headers = {
        "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A"
    }
    response = requests.get("https://insurgere.com.br", headers=headers)
    response.raise_for_status()
    matches = re.findall(PATTERN, response.text)

    text_list = list()

    for i in range(5):
        url = matches[i][0]
        short_url = shorten_url(url)
        text = html.unescape(matches[i][1])
        if len(text) >= 100:
            text = text[:98] + "..."
        text_list.append(f"{text}\n\n{short_url}")

    return text_list


def get_hacker_news():
    """
    Returns a list with the website's top 5 news' link and title.
    """
    PATTERN = re.compile(r"(<tr class=\'athing\' id=\'\d+\'>.*?\n.*?\n.*?<\/td><\/tr>)")
    LINK_AND_TITLE_PATTERN = re.compile(
        r"<a href=\"(.+?)\" class=\"storylink\">(.+?)<\/a>"
    )
    VOTES_PATTERN = re.compile(r"(\d+) points")

    response = requests.get(
        "https://news.ycombinator.com/news", headers={"User-Agent": "Mozilla/5.0"}
    )
    response.raise_for_status()
    matches = re.findall(PATTERN, response.text)

    matches_list = list()

    for i in matches:
        try:
            link_and_title_matches = re.search(LINK_AND_TITLE_PATTERN, i)
            link = link_and_title_matches.group(1)
            title = link_and_title_matches.group(2)
            votes = re.search(VOTES_PATTERN, i).group(1)
            matches_list.append({"title": title, "link": link, "votes": votes})
        except AttributeError:
            pass

    matches_list = sorted(matches_list, key=lambda x: int(x["votes"]), reverse=True)

    text_list = list()

    for i in range(5):
        url = matches_list[i]["link"]
        if url[:4] != "http":
            url = "https://news.ycombinator.com/" + url
        short_url = shorten_url(url)
        text = html.unescape(matches_list[i]["title"])
        votes = matches_list[i]["votes"]
        text = f"({votes} votos) {text}"
        if len(text) >= 100:
            text = text[:98] + "..."
        text_list.append(f"{text}\n\n{short_url}")

    return text_list


def get_every_news_and_name():
    """
    Returns a list of tuples with websites and news lists.
    """
    the_economist_list = get_the_economist()
    the_wall_street_journal_list = get_the_wall_street_journal()
    o_antagonista_list = get_o_antagonista()
    insurgere_list = get_insurgere()
    hacker_news_list = get_hacker_news()

    websites_list = [
        ("The Economist", the_economist_list),
        ("The Wall Street Journal", the_wall_street_journal_list),
        ("O Antagonista", o_antagonista_list),
        ("Insurgere", insurgere_list),
        ("Hacker News", hacker_news_list),
    ]

    return websites_list


def get_daily_header(timezone="America/Cuiaba"):
    """
    Takes a timezone and returns a header for the daily tweets.
    """
    TIMEZONE = pytz.timezone(timezone)
    now = datetime.datetime.now(TIMEZONE)

    minute = now.minute
    hour = now.hour
    day = now.day
    month = now.month
    year = now.year

    if hour >= 0 and hour <= 11:
        greeting = "Bom dia. "
    elif hour >= 12 and hour <= 17:
        greeting = "Boa tarde. "
    elif hour >= 18 and hour <= 23:
        greeting = "Boa noite. "
    else:
        greeting = ""

    header = f"{greeting}\n\nHoje é dia {day:0>2}/{month:0>2}/{year}.\n\nAgora são {hour}h{minute} (GMT -04:00).\n\nAtualizações:"

    return header


def wait_until(hour, minute, enablezone=False, timezone="America/Cuiaba"):
    """
    Takes an hour mark, a minute mark, and a timezone and waits until the given time in the given timezone.
    """
    if timezone:

        TIMEZONE = pytz.timezone(timezone)
        current_time = datetime.datetime.now(TIMEZONE)
    else:
        current_time = datetime.datetime.now()

    minutes_rest = ((59 + minute) - current_time.minute) * 60
    seconds_rest = 60 - current_time.second
    rest = minutes_rest + seconds_rest

    if current_time.hour < hour:
        time_to_be_slept = (((hour - 1) - current_time.hour) * 60 * 60 + rest) - 60
    elif (current_time.hour == hour) and (current_time.minute < minute):
        time_to_be_slept = (rest - 3600) - 60
    else:
        time_to_be_slept = (((23 + hour) - current_time.hour) * 60 * 60 + rest) - 60

    time_to_be_slept = 0 if time_to_be_slept < 0 else time_to_be_slept

    time.sleep(time_to_be_slept)


def main():
    """
    Runs the program entirely.
    """
    username = input("Twitter Username: ")
    times_a_day = int(input("Threads a day: "))

    schedule = list()

    for i in range(times_a_day):
        hour = input("Hora da " + str(i + 1) + "ª execução: ")
        minute = input("Minuto da " + str(i + 1) + "ª execução: ")
        schedule.append((hour, minute))

    while True:

        for hour, minute in schedule:

            wait_until(hour, minute, enablezone=True)

            # GETTING DATA

            for _ in range(3):
                try:
                    currencies_text = get_currencies()

                    stock_indexes_text = get_stock_indexes()

                    news_list = get_every_news_and_name()

                    daily_header = get_daily_header()

                except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
                    time.sleep(3)
                    continue
                else:
                    break
            else:
                raise Exception("Erro tentando conseguir as informações externas.")

            # TWEETING

            # Daily Header
            tweet(daily_header)
            time.sleep(5)
            daily_header_id = get_my_last_tweet_id()

            # Currencies
            reply(currencies_text, username, daily_header_id)
            time.sleep(3)

            # Stock Indexes
            reply(stock_indexes_text, username, daily_header_id)
            time.sleep(3)

            # News
            reply("Notícias:", username, daily_header_id)
            time.sleep(5)
            news_id = get_my_last_tweet_id()

            for website_name, text_list in news_list:
                reply(website_name, username, news_id)
                time.sleep(5)
                website_name_id = get_my_last_tweet_id()
                for text in text_list:
                    reply(text, username, website_name_id)
                    time.sleep(5)


if __name__ == "__main__":
    main()
