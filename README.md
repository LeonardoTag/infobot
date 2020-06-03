# InfoBot

## Created by Leonardo F. Tag.

A Twitter bot programmed for my personal use, hence the Portuguese
and R$ signs.

It tweets information about currencies prices, stock indexes, and
recent news whenever programmed.

To adjust it to your use, change the information in the last if
statement to your data.

```python
if __name__ == "__main__":
    main(
        username="username",  # Twitter account username without @.
        timezone="timezone",  # Timezones available at https://stackoverflow.com/q/13866926
        API_KEY="XXX",  # Get yours at https://developer.twitter.com/apps
        API_SECRET_KEY="XXX",  # Get yours at https://developer.twitter.com/apps
        ACCESS_TOKEN="XXX",  # Get yours at https://developer.twitter.com/apps
        ACCESS_TOKEN_SECRET="XXX",  # Get yours at https://developer.twitter.com/apps
    )
```

Feel free to use the information in this module however you like.

No copyright applies.

## This bot is up and running [here](https://twitter.com/dailyinfobot).