# `send-aprs-message.py`

This program is a Frankenstein version of multiple APRS “send message” routines from the [core-aprs-client](https://github.com/joergschultzelutter/core-aprs-client). Its sole purpose is to provide the user with a simple way to send multi-line APRS messages (read: content longer tan 67 characters) — which may be necessary after restarting your server, for example. For notification targets other than APRS multi-messages _or_ APRS messages not longer than 67 characters, I recommend using the message library [apprise](https://github.com/caronc/apprise) by Chris Caron.

## Usage

```
python send-aprs-message.py --help

sage: send-aprs-message.py [-h] [--from-callsign APRS_FROM_CALLSIGN]
                            [--passcode APRS_PASSCODE]
                            [--to-callsign APRS_TO_CALLSIGN]
                            [--aprs-message APRS_MESSAGE]
                            [--numeric-message-pagination] [--simulate-send]

options:
  -h, --help            show this help message and exit
  --from-callsign APRS_FROM_CALLSIGN
                        APRS FROM callsign (sender)
  --passcode APRS_PASSCODE
                        APRS passcode for the FROM callsign (sender)
  --to-callsign APRS_TO_CALLSIGN
                        APRS TO callsign (receipient)
  --aprs-message APRS_MESSAGE
                        APRS message
  --numeric-message-pagination
                        Add message enumeration to each outgoing APRS message
  --simulate-send       Simulate sending of data to APRS-IS (output will be
                        made to the console)

```
