# `send-aprs-message.py`

This program is a Frankenstein'ed version of the [core-aprs-client](https://github.com/joergschultzelutter/core-aprs-client)'s APRS "send message" routines. Its sole purpose is to provide the user with an easy means of sending multiple APRS messages - which is something that you may want to do after e.g. your server has been rebooted. For notification targets other than APRS multi-messages, I recommend using Chris Caron's [apprise](https://github.com/caronc/apprise) messaging library.
