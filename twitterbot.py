# Created by Leonardo F. Tag.
#
# A Twitter bot programmed for my personal use, hence the Portuguese
# and R$ signs.
#
# It tweets information about currencies prices, stock indexes, and
# recent news whenever programmed.
#
# To adjust it to your use, change the information in the last if
# statement to your data.
#
# Feel free to use the information in this module however you like.
#
# No copyright applies.

# IMPORTING MODULES FROM THE STANDARD LIBRARY

import contextlib
import datetime
import html
import re
import sys
import time
from urllib.parse import urlencode
from urllib.request import urlopen

# CHECKING IF THE REQUIRED THIRD-PARTY MODULES ARE INSTALLED AND IMPORTING THEM

try:
    import requests
except ImportError:
    raise Exception("Requests not installed. (pip3 install requests)")

try:
    import tweepy
except ImportError:
    raise Exception("Tweepy not installed. (pip3 install tweepy)")

try:
    import pytz
except ImportError:
    raise Exception("Pytz not installed. (pip3 install pytz)")


# UTILITIES


def shorten_url(url):
    """
    Takes an url and returns it shortened.

    :param url: Desired web address.

    :return: Desired web address shortened. (http://tinyurl.com/XXXXXXXX)
    """
    request_url = "http://tinyurl.com/api-create.php?" + urlencode({"url": url})
    with contextlib.closing(urlopen(request_url)) as response:
        return response.read().decode("utf-8")


def wait_until(hour, minute, timezone, delay=0, advance=0, enablezone=False):
    """
    Takes an hour mark, a minute mark, and a timezone, and waits until the given time in the given timezone.

    :param hour: Desired hour mark.
    :param minute: Desired minute mark.
    :param timezone: Desired timezone. (Timezones available at https://stackoverflow.com/q/13866926.)
    :param delay: Optional delay. (0 as default.)
    :param advance: Optional advance. (0 as default.)
    :param enablezone: True: Enables the timezone feature. False: Disables the timezone feature. (False as default.)

    :return: None
    """
    if timezone:
        TIMEZONE = pytz.timezone(timezone)
        current_time = datetime.datetime.now(TIMEZONE)
    else:
        current_time = datetime.datetime.now()

    # Calculate the remaining time in seconds to complete an hour.
    minutes_rest = ((59 + minute) - current_time.minute) * 60
    seconds_rest = 60 - current_time.second
    rest = minutes_rest + seconds_rest

    if current_time.hour < hour:
        time_to_be_slept = ((hour - 1) - current_time.hour) * 60 * 60 + rest
    elif (current_time.hour == hour) and (current_time.minute < minute):
        time_to_be_slept = rest - 3600
    else:
        time_to_be_slept = ((23 + hour) - current_time.hour) * 60 * 60 + rest

    time_to_be_slept = time_to_be_slept + delay - advance

    time_to_be_slept = (
        0 if time_to_be_slept < 0 else time_to_be_slept
    )  # Used to keep time nonnegative and to become 0 if negative.

    time.sleep(time_to_be_slept)


# TWITTER


def authenticate(API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET):
    """
    Takes Twitter's Api Key, Api Secret Key, Access Token, and Access Token Secret, returns an authenticated Twitter Api Object.

    :param API_KEY: Twitter's Api key.
    :param API_SECRET_KEY: Twitter's Api secret key.
    :param ACCESS_TOKEN: Twitter's Api access token.
    :param ACCESS_TOKEN_SECRET: Twitter's Api access token secret.

    :return: An authenticated Tweepy Api Object.
    """
    authentication = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
    authentication.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    return tweepy.API(authentication)


def tweet(api, message):
    """
    Takes an authenticated Tweepy Api Object, a message and tweets it.

    :param api: An authenticated Tweepy Api Object.
    :param message: Desired message to tweet.

    return: None
    """
    api.update_status(status=message)


def reply(api, message, username, status_id):
    """
    Takes an authenticated Tweepy Api Object, a message, an username and a status id and replies it with the message.

    :param api: An authenticated Tweepy Api Object.
    :param message: Desired message to reply.
    :param username: Twitter account username without @.
    :param status_id: The id of the tweet to be replied.

    :return: None
    """
    api.update_status(
        status="@" + username + "\n" + message,
        in_reply_to_status_id=status_id,  # The @username must be used for the message to be recognized as a reply.
    )


def get_my_last_tweet_id(api):
    """
    Takes an authenticated Tweepy Api Object and returns the Twitter account's last tweet's id.

    :param api: An authenticated Tweepy Api Object.

    :return: Int with Twitter account's last tweet's id.
    """
    for _ in range(3):
        try:
            last_tweet = api.user_timeline(id=api.me().id, count=1)[0]
        except IndexError:
            time.sleep(3)
            continue
        else:
            break
    else:
        raise Exception("The last tweet was not found.")

    return last_tweet.id


# DAILY HEADER


def get_daily_header(timezone):
    """
    Takes a timezone and returns a header for the daily tweets.

    :param timezone: Desired timezone. (Timezones available at https://stackoverflow.com/q/13866926.)

    :return: A formated string for the first tweet.
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
    #               Good morning
    elif hour >= 12 and hour <= 17:
        greeting = "Boa tarde. "
    #               Good afternoon
    elif hour >= 18 and hour <= 23:
        greeting = "Boa noite. "
    #               Good evening
    else:
        greeting = ""

    header = f"{greeting}\n\nHoje é dia {day:0>2}/{month:0>2}/{year}.\n\nAgora são {hour:0>2}h{minute:0>2} (GMT -04:00).\n\nAtualizações:"
    #                        Today is the day                            It is (Timewise)               My local timezone   Updates
    return header


# CURRENCIES


def get_currencies():
    """
    Returns a string with some currencies' prices in reais.

    :return: Formated string for the currencies reply.
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


# STOCK INDEXES


def get_stock_indexes():
    """
    Returns a string with some stocks' share prices.

    :return: Formated string for the stock Indexes reply.
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


# NEWS


def get_the_economist():
    """
    Returns a list with The Economist's first 5 news' links and titles.

    :return: List of strings with the first 5 news' links and titles found.
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
        if len(text) >= 100:  # Used to keep tweets under 144 characters.
            text = text[:98] + "..."
        text_list.append(f"{text}\n\n{short_url}")

    return text_list


def get_the_wall_street_journal():
    """
    Returns a list with The Wall Street Journal's first 5 news' links and titles.

    :return: List of strings with the first 5 news' links and titles found.
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
        if len(text) >= 100:  # Used to keep tweets under 144 characters.
            text = text[:98] + "..."
        text_list.append(f"{text}\n\n{short_url}")

    return text_list


def get_o_antagonista():
    """
    Returns a list with O Antagonista's first 5 news' links and titles.

    :return: List of strings with the first 5 news' links and titles found.
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
        if len(text) >= 100:  # Used to keep tweets under 144 characters.
            text = text[:98] + "..."
        text_list.append(f"{text}\n\n{short_url}")

    return text_list


def get_insurgere():
    """
    Returns a list with Insurgere's first 5 news' links and titles.

    :return: List of strings with the first 5 news' links and titles found.
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
        if len(text) >= 100:  # Used to keep tweets under 144 characters.
            text = text[:98] + "..."
        text_list.append(f"{text}\n\n{short_url}")

    return text_list


def get_hacker_news():
    """
    Returns a list with The Hacker News's 5 most voted news' links and titles.

    :return: List of strings with the most voted 5 news' links and titles found.
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
        if len(text) >= 100:  # Used to keep tweets under 144 characters.
            text = text[:98] + "..."
        text_list.append(f"{text}\n\n{short_url}")

    return text_list


def get_every_news_and_name():
    """
    Returns a list of tuples with websites and news lists.

    :return: List of tuples with the first element being a string with the website name and the second a list with the news.
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


# SCHEDULE


def request_schedule_input():
    """
    Requests the user the wished schedule of tweets and returns a list with it.

    :return: A sorted list of tuples with the first element being the hour and the second the minute, according to the schedule input by the user.
    """
    times_a_day = int(input("Threads a day: "))
    assert times_a_day > 0, "Times a day must be greater than 0."

    print()

    schedule = list()

    for index in range(1, times_a_day + 1):

        if times_a_day > 1:
            if str(index)[-1] == "1":
                ordinal_sign = "st e"
            elif str(index)[-1] == "2":
                ordinal_sign = "nd e"
            elif str(index)[-1] == "3":
                ordinal_sign = "rd e"
            else:
                ordinal_sign = "th e"
        else:
            index, ordinal_sign = "", "E"

        hour = int(input(f"{index}{ordinal_sign}xecution hour mark: "))
        assert 0 <= hour < 24, "Hour invalid."

        minute = int(input(f"{index}{ordinal_sign}xecution minute mark: "))
        assert 0 <= minute < 60, "Minute invalid."

        schedule.append((hour, minute))

        print()

    return sorted(list(set(schedule)))


# SKIPS


def get_skips_needed(schedule, timezone):
    """
    Takes the tweet schedule and the timezone and returns how many time marks should be skipped.

    :param schedule: List generated with the request_schedule_input function.
    :param timezone: Desired timezone. (Timezones available at https://stackoverflow.com/q/13866926.)

    :return: An int with the needed amount of time marks to be skipped in order to execute the next one in time order.
    """
    TIMEZONE = pytz.timezone(timezone)
    current_time = datetime.datetime.now(TIMEZONE)
    current_hour_and_minute = (current_time.hour, current_time.minute)

    if current_hour_and_minute in schedule:
        current_index = schedule.index(current_hour_and_minute) + 1
        comparison_list = list()
    else:
        comparison_list = schedule.copy()
        comparison_list.append(current_hour_and_minute)
        comparison_list.sort()
        current_index = comparison_list.index(current_hour_and_minute)

    if (current_index == 0) or (current_index == len(comparison_list)):
        return 0
    else:
        return current_index


# MAIN FUNCTION


def main(
    username, timezone, API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
):
    """
    Runs the program.

    :param username: Twitter account username without @.
    :param timezone: Desired timezone. (Timezones available at https://stackoverflow.com/q/13866926.)
    :param API_KEY: Twitter's Api key.
    :param API_SECRET_KEY: Twitter's Api secret key.
    :param ACCESS_TOKEN: Twitter's Api access token.
    :param ACCESS_TOKEN_SECRET: Twitter's Api access token secret.
    """

    schedule = request_schedule_input()

    skips = get_skips_needed(schedule=schedule, timezone=timezone)

    first_time_looping = True

    while True:
        schedule_iterator = iter(schedule)

        for hour, minute in schedule_iterator:
            if first_time_looping:
                first_time_looping = False
                if skips == 0:
                    pass
                else:
                    for _ in range(skips - 1):
                        next(schedule_iterator)
                    continue

            wait_until(
                hour=hour, minute=minute, timezone=timezone, advance=60, enablezone=True
            )

            # GETTING DATA

            for _ in range(3):
                try:
                    currencies_text = get_currencies()
                    stock_indexes_text = get_stock_indexes()
                    news_list = get_every_news_and_name()
                    daily_header = get_daily_header(timezone=timezone)
                except (
                    requests.exceptions.HTTPError,
                    requests.exceptions.ConnectionError,
                ):
                    time.sleep(3)
                    continue
                else:
                    break
            else:
                raise Exception("Erro tentando conseguir as informações externas.")

            # TWEETING

            api = authenticate(
                API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
            )

            # Daily Header
            tweet(api, daily_header)
            time.sleep(5)
            daily_header_id = get_my_last_tweet_id(api)

            # Currencies
            reply(api, currencies_text, username, daily_header_id)
            time.sleep(3)

            # Stock Indexes
            reply(api, stock_indexes_text, username, daily_header_id)
            time.sleep(3)

            # News
            reply(api, "Notícias:", username, daily_header_id)
            #           News
            time.sleep(5)
            news_id = get_my_last_tweet_id(api)

            for website_name, text_list in news_list:
                reply(api, website_name, username, news_id)
                time.sleep(5)
                website_name_id = get_my_last_tweet_id(api)
                for text in text_list:
                    reply(api, text, username, website_name_id)
                    time.sleep(5)


if __name__ == "__main__":
    main(
        username="username",  # Twitter account username without @.
        timezone="timezone",  # Timezones available at https://stackoverflow.com/q/13866926
        API_KEY="XXX",  # Get yours at https://developer.twitter.com/apps
        API_SECRET_KEY="XXX",  # Get yours at https://developer.twitter.com/apps
        ACCESS_TOKEN="XXX",  # Get yours at https://developer.twitter.com/apps
        ACCESS_TOKEN_SECRET="XXX",  # Get yours at https://developer.twitter.com/apps
    )
