# `send-aprs-message.py`

This program is a Frankenstein'ed version of multiple APRS “send message” routines from the [core-aprs-client](https://github.com/joergschultzelutter/core-aprs-client). Its sole purpose is to provide the user with a simple way to send _multi_-line APRS messages (read: content longer than 67 characters which is to be split up into multiple APRS messsages). You cann add `send-aprs-message.py` to your custom `--command-code` user scripts and send responses to the user from whose callsign the initial request has originated. 

For notification targets other than APRS (e.g. Telegram messenger), I recommend using the message library [apprise](https://github.com/caronc/apprise) by Chris Caron which also supports regular APRS messages up to 67 bytes in length.

>[!NOTE]
>The format of the message must be limited to content in ASCII 7-bit encoding.

## Usage

```
python send-aprs-message.py --help

sage: send-aprs-message.py  [-h]
                            [--from-callsign APRS_FROM_CALLSIGN]
                            [--passcode APRS_PASSCODE]
                            [--to-callsign APRS_TO_CALLSIGN]
                            [--aprs-message APRS_MESSAGE]
                            [--numeric-message-pagination]
                            [--simulate-send]

options:
  -h, --help                            show this help message and exit
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
  --simulate-send                       Simulate sending of data to APRS-IS (output will be
                                        made to the console)

```

## Description

| Parameter                      | Description                                                                                                                                                                          | Data Type | Default       |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- | ------------- |
| `--from-callsign`              | Our call sign from which we send the message                                                                                                                                         | `str`     | empty string  |
| `--passcode`                   | 5-digit numeric APRS-IS passcode                                                                                                                                                     | `str`     | empty string  |
| `--to-callsign`                | The destination call sign to which we send the message                                                                                                                               | `str`     | empty string  |
| `--aprs-message`               | The APRS message that we want to send to APRS-IS                                                                                                                                     | `str`     | empty string  |
| `--numeric-message-pagination` | __Optional__. When selected, the usable length of an APRS message is reduced to from 67 to 59 characters and message is assigned its own counter in return.                          | `bool`    | `False`       |
| `--simulate-send`              | __Optional__ test option. When activated, outgoing messages are not sent to APRS-IS, but only displayed on the console.                                                              | `bool`    | `False`       |


### Regular APRS messaging (67 usable characters)
```
python send-aprs-message.py --from-callsign=DF1JSL-1 --to-callsign=DF1JSL-2 --passcode=xxxxx --simulate-send --aprs-message=Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum 
2025-08-07 12:07:02,733 - send-aprs-message -DEBUG - Simulating APRS message 'DF1JSL-1>APMPAD::DF1JSL-2 :Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do'
2025-08-07 12:07:12,738 - send-aprs-message -DEBUG - Simulating APRS message 'DF1JSL-1>APMPAD::DF1JSL-2 :eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim'
2025-08-07 12:07:22,741 - send-aprs-message -DEBUG - Simulating APRS message 'DF1JSL-1>APMPAD::DF1JSL-2 :ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut'
2025-08-07 12:07:32,745 - send-aprs-message -DEBUG - Simulating APRS message 'DF1JSL-1>APMPAD::DF1JSL-2 :aliquip ex ea commodo consequat. Duis aute irure dolor in'
2025-08-07 12:07:42,748 - send-aprs-message -DEBUG - Simulating APRS message 'DF1JSL-1>APMPAD::DF1JSL-2 :reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla'
2025-08-07 12:07:52,749 - send-aprs-message -DEBUG - Simulating APRS message 'DF1JSL-1>APMPAD::DF1JSL-2 :pariatur. Excepteur sint occaecat cupidatat non proident, sunt in'
2025-08-07 12:08:02,749 - send-aprs-message -DEBUG - Simulating APRS message 'DF1JSL-1>APMPAD::DF1JSL-2 :culpa qui officia deserunt mollit anim id est laborum'
```

### APRS messaging with active `--numeric-message-pagination` (59 usable characters per message)

```
python send-aprs-message.py --from-callsign=DF1JSL-1 --to-callsign=DF1JSL-2 --passcode=xxxxx --simulate-send --aprs-message=Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum --numeric-message-pagination 
2025-08-07 12:02:49,689 - send-aprs-message -DEBUG - Simulating APRS message 'DF1JSL-1>APMPAD::DF1JSL-2 :Lorem ipsum dolor sit amet, consectetur adipiscing elit,    (01/08)'
2025-08-07 12:02:59,694 - send-aprs-message -DEBUG - Simulating APRS message 'DF1JSL-1>APMPAD::DF1JSL-2 :sed do eiusmod tempor incididunt ut labore et dolore magna  (02/08)'
2025-08-07 12:03:09,695 - send-aprs-message -DEBUG - Simulating APRS message 'DF1JSL-1>APMPAD::DF1JSL-2 :aliqua. Ut enim ad minim veniam, quis nostrud exercitation  (03/08)'
2025-08-07 12:03:19,696 - send-aprs-message -DEBUG - Simulating APRS message 'DF1JSL-1>APMPAD::DF1JSL-2 :ullamco laboris nisi ut aliquip ex ea commodo consequat.    (04/08)'
2025-08-07 12:03:29,699 - send-aprs-message -DEBUG - Simulating APRS message 'DF1JSL-1>APMPAD::DF1JSL-2 :Duis aute irure dolor in reprehenderit in voluptate velit   (05/08)'
2025-08-07 12:03:39,702 - send-aprs-message -DEBUG - Simulating APRS message 'DF1JSL-1>APMPAD::DF1JSL-2 :esse cillum dolore eu fugiat nulla pariatur. Excepteur sint (06/08)'
2025-08-07 12:03:49,706 - send-aprs-message -DEBUG - Simulating APRS message 'DF1JSL-1>APMPAD::DF1JSL-2 :occaecat cupidatat non proident, sunt in culpa qui officia  (07/08)'
2025-08-07 12:03:59,711 - send-aprs-message -DEBUG - Simulating APRS message 'DF1JSL-1>APMPAD::DF1JSL-2 :deserunt mollit anim id est laborum                         (08/08)'
```
