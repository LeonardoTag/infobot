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
        username="dailyinfobot",  # Twitter account username without @.
        timezone="America/Cuiaba",  # Timezones available at https://stackoverflow.com/q/13866926
        API_KEY="XXX",  # Get yours at https://developer.twitter.com/apps
        API_SECRET_KEY="XXX",  # Get yours at https://developer.twitter.com/apps
        ACCESS_TOKEN="XXX",  # Get yours at https://developer.twitter.com/apps
        ACCESS_TOKEN_SECRET="XXX",  # Get yours at https://developer.twitter.com/apps
        text_message=True,  # Whether you want it to send you a text message if it fails.
        TWILIO_ACCOUNT_SID="XXX",  # Get yours at https://www.twilio.com/sms
        TWILIO_AUTH_TOKEN="XXX",  # Get yours at https://www.twilio.com/sms
        TWILIO_NUMBER="XXX",  # Get yours at https://www.twilio.com/sms
        MOBILE_NUMBER="XXX",  # Your mobile number
    )

```

Feel free to use the information in this module however you like.

No copyright applies.

## This bot is up and running [here](https://twitter.com/dailyinfobot).
