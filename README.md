# secure-aprs-bastion-bot

Manage your IT infrastructure via APRS messaging (to a certain extent).

## Introduction

I recently went on a multi-day hiking trip and discovered that a program on one of my home servers had crashed due to an error. I had my cell phone with me and was able to access the computer via ssh and restart the program, but there are still areas in my country where there is _zero_ cell phone reception (kudos to the German government). 

So what to do in such a case? In most of these cases where I am stuck in the wilderness without no cell phone reception, there would still be an APRS-enabled repeater nearby, and so the idea was born to create an APRS-enabled bastion host that would give me access to my internal IT infrastructure in the event of cell phone network unavailability. `secure-aprs-bastion-bot` aims to support this use case.

## Features

- Control of programs using predefined keywords (`--command-code`) and scripts (`--command-script`). **The user is responsible for creating these individual scripts.**
- In addition to transferring the call sign of the incoming message, optional parameters such as the name of a server can be transferred as part of the APRS message. Up to 9 optional parameters are supported.
- Authorization, authentication, and security:
  - Executable programs are assigned locally per call sign; i.e., programs assigned to the call sign `DF1ABC` cannot be used by `DF1XYZ` (and vice versa).
  - `secure-aprs-bastion-bot` requires one-time passwords (TOTP) which are individual to each authenticated / configured user. The secrets for these tokens are defined when setting up the user configuration and can be configured with a validity of 30 seconds to 5 minutes. In addition to the duplicate check of the actual APRS message, an additional TOTP/callsign duplicate check is performed. This check prevents one-time passwords from being used multiple times during their validity period, effectively preventing hi-jacking and misuse of the token in question as best as possible over an unsecured plain-text APRS connection.
- User account and command setup:
  - The configuration data is set up and tested using a configuration program provided (`configure.py`).
  - The configuration can be done at the call sign plus SSID level _or_ exclusively at the call sign level without SSID (base call sign). In the latter case, all call signs of the user _with_ SSID can use the configuration of the call sign _without_ SSID - provided they transmit the base call sign's TOTP token for authorization and authentication.
  - When configuring the base call sign, it is also not necessary to configure all other call signs with SSID individually. The prerequisite for using this configuration is, of course, the use of the TOTP token of the base call sign. Further details can be found in the [configure.py](https://github.com/joergschultzelutter/secure-aprs-bastion-bot/blob/master/docs/configure.md) program documentation.
- Program execution:
  - The programs to be executed can be started either synchronously or asynchronously.
    - Synchronous execution first executes the desired script. After script termination,  `secure-aprs-bastion-bot` sends an APRS confirmation to the user. This is the default behavior.
    - Asynchronous processing first sends the APRS confirmation to the user and _then_ starts the desired program as a separate process.  `secure-aprs-bastion-bot` will _not_ wait for the program to finish executing. Such processing may be necessary, for example, when restarting a server.
  - After completion of such a program sequence, regardless of its execution type (synchronous or asynchronous), an APRS message can be sent back to the caller as part of the user script and a supporting Python script (`send-aprs-message.py`). Alternatively, other recommended tools such as [Apprise](https://github.com/caronc/apprise) can be used.

# Program-specific documentation

- [secure-aprs-bastion-bot](docs/secure-aprs-bastion-bot.md)
- [configure.py](https://github.com/joergschultzelutter/secure-aprs-bastion-bot/blob/master/docs/configure.md)
- [send-aprs-message.py](https://github.com/joergschultzelutter/secure-aprs-bastion-bot/blob/master/docs/send-aprs-message.md)

## First steps

- Clone this repository
- `pip install -r requirements.txt` (or use the `requirements.txt` file from the respective project's sub directory in case you just want to install a single program)
- Configure the bot`s configuration file:
  - run [configure.py](docs/configure.md) and create at least one user account (`--add-user`)
  - run [configure.py](docs/configure.md) again and create at least one `--command-code` / `--command-string` relationship entry (`--add-command`)
  - Finally, use [configure.py](docs/configure.md) for configuration file testing
- Amend the bot's configuration file. The bot is based on my `core-aprs-client` framework ([repository link](https://github.com/joergschultzelutter/core-aprs-client)). You might want to [disable e.g. beaconing and/or bulletin messages](https://github.com/joergschultzelutter/core-aprs-client/blob/master/docs/configuration.md).
- Start the bot and send APRS commands to it

## Anatomy of an APRS message to `secure-aprs-bastion-bot`

Every message to `secure-aprs-bastion-bot` always starts with a 6-digit TOTP code. This comes either from the sending call sign with SSID or from its generic call sign without SSID, if its configuration is to be used.

The command to be executed (`--command-code`) follows immediately after the TOTP code - read: no separator. The actual content of this command (`--command-string`) is defined as part of the configuration setup. For example, the user transmits the command `reboot` via APRS, and secure-aprs-bastion-bot then executes the command sequence `source ./scripts/server-reboot.sh` locally on the computer of the secure-aprs-bastion-bot after successful authorization and authentication.

Additional parameters are separated by spaces. The first parameter after `--command-code` corresponds to `$1`, the second parameter to `$2`, and so on (`$0` .. `$9`). Before the command stored in the `--command-string` is executed, the placeholders for these parameters are replaced by these optional parameters, which were transmitted as part of the APRS message.

The additional parameter `$0`, on the other hand, _always_ contains the call sign of the user who sent the message to `secure-aprs-bastion-bot` (e.g., `DF1JSL-1`).

Example 1 - `--command-code` without optional parameters

| APRS message             | `TOTP code` | `--command-code` | `$0`        | `$1`  | `$2` | .... | `$9` |
| ------------------------ | ----------- |------------------| ----------- | ----- | ---- | ---- | ---- |
| `123456reboot`           | `123456`    | `reboot`         | `DF1JSL-1`  | n/a   | n/a  |      | n/a  |


Example 1 - `command-code` with optional parameters

| APRS message             | `TOTP code` | `--command-code` | `$0`        | `$1`       | `$2` | .... | `$9` |
| ------------------------ | ----------- |------------------| ----------- | ---------- | ---- | ---- | ---- |
| `123456reboot debmu41 5` | `123456`    | `reboot`         | `DF1JSL-1`  | `debmu41`  | `5`  |      | n/a  |

> [!TIP]
> tl;dr: A user always sends the `--command-code` as an APRS message to the `secure-aprs-bastion-bot`. The bot determines the `--command-code` and any optional parameters from the message, identifies the corresponding `--command-string`, replaces the placeholders for the optional parameters, and then executes the modified `--command-string`.

To define placeholders for the optional parameters in the `--command-string`, the following conventions apply:
- `$0` ALWAYS corresponds to the call sign that sent the initial message to `secure-aprs-bastion-bot`.
- `$1` .. `$9` correspond to the additional parameters that have been extracted from the APRS message. Since these are optional, these parameters are not necessarily filled

Assuming the previous example `reboot debmu41 5` (sent by `DF1JSL-1`), the following optional parameters are available:
- `$0` = `DF1JSL-1`
- `$1` = `debmu41`
- `$2` = `5`
  
These parameters can be stored in the corresponding `command-string` when setting up the `command-code` keyword. Assuming that the `command-code` `reboot` accepts three parameters for its corresponding `command-string`:
- a wait time until reboot
- a server name
- and the call sign of the original message

The setup for `--command-code`and `--command-string` in the program`s configuration file could then look as follows:

| `--command-code` | `--command-string` (as stored in the config file) |
|------------------|---------------------------------------------------|
| `reboot`         | `source ./scripts/server-reboot.sh $2 $1 $0`      |

First, `secure-aprs-bastion-bot` replaces the placeholders in the string with their actual values:

| `--command-code` | `--command-string` (after modification)                |
|------------------|--------------------------------------------------------|
| `reboot`         | `source ./scripts/server-reboot.sh 5 debmu41 DF1JSL-1` |

The command of the edited `--command-string` is then executed by `secure-aprs-bastion-bot`.

> [!CAUTION]
> You should always create a dedicated script for each keyword, which serves a _single predefined purpose_. Creating a free text keyword, in which the _entire_ command line sequence to be executed is transmitted via APRS message, is technically possible, but is not recommended.

## FAQ

- Q: _Why didn't you include this functionality in your other APRS bots, such as [mpad](https://www.github.com/joergschultzelutter/mpad)?_
- A: `secure-aprs-bastion-bot` does not have a magic wand to grant itself extended user rights. So if you intend to use the APRS bot to implement a `restart` command for your server, `secure-aprs-bastion-bot` must also run with the appropriate user rights (i.e., as a privileged user). Additionally, you also might want to refrain from broadcasting APRS bulletins and/or your bot's location data. These are the main reasons why I created a new APRS bot (rather than adding these functions to one of my existing APRS bots).

- Q: _Tell me more about the TOTP codes and their validity._
- A: All TOTP codes can only be used *once*, regardless of their validity period (30 seconds to 5 minutes). This is to prevent TOTP codes with a long validity period from being misused by another party. A TOTP code can therefore only be used to execute a *single* `--command-code`. If several `--command-code`s are to be executed, a separate TOTP code must be provided for each one. The validity period of TOTP codes can be defined between 30 seconds and 5 minutes; this setting is made once when the user account is created (`--add-user`) and can be different for each user. Depending on the transmission time of an APRS message from the radio device via APRS-IS to the `secure-aprs-bastion-bot`, it is recommended to adjust the default setting of 30 seconds individually for each user.

- Q: _Is this program safe to use?_
- A: Yes, to a certain extent. In addition to security via TOTP code, the user's valid call signs must be included in the configuration file with the permitted `--command-code` settings; this means that unknown users or `--command-code` commands that are not configured for this user cannot be executed. Regardless of its validity period, a TOTP code can only be used once for the associated call sign; this prevents multiple use of a TOTP code. Due to the nature of APRS messages, such as unencrypted text messages, there is a theoretical possibility of misuse in the event that an attacker a) obtains a valid and (still) unused TOTP code, b) has knowledge of the `--command-code`s associated with this account configuration, and at the same time c) spoofs the callsign of the original sender.

- Q: _Why is it recommended to create dedicated scripts and only use these? Wouldn't it be easier to transfer the whole command line sequence as free text?_
- A: Sure you can. Create a corresponding `--command-code` and fill its associated `--command-string` _exclusively_ with free text parameters (`$1` .. `$9`). You can also drive your car at 200 km/h towards a rock face without wearing a seat belt, swim in shark-infested waters, or jump out of an airplane without a parachute. All of these options carry a very real risk of ending very badly. Keep in mind that you would be transmitting sensitive data such as user credentials via an unsecured clear-text transmission media (APRS). See also my earlier comments on program security.
