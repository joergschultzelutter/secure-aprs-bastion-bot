# `send-aprs-message.py`

This program is a Frankenstein version of the APRS “send message” routines from the [core-aprs-client](https://github.com/joergschultzelutter/core-aprs-client). Its sole purpose is to provide the user with a simple way to send multi-line APRS messages (read: content longer tan 67 characters) — which may be necessary after restarting your server, for example. For notification targets other than APRS multi-messages _or_ APRS messages not longer than 67 characters, I recommend using the message library [apprise](https://github.com/caronc/apprise) by Chris Caron.
