# secure-aprs-bastion-bot

Manage your IT infrastructure via APRS messaging (to a certain extent).

## Introduction

I recently went on a multi-day hiking trip and discovered that a program on one of my home servers had crashed due to an error. I had my cell phone with me and was able to access the computer via ssh and restart the program, but there are still areas in my country where there is _zero_ cell phone reception (kudos to the German government). 

So what to do in such a case? In most of these cases where I am stuck in the wilderness without no cell phone reception, there would still be an APRS-enabled repeater nearby, and so the idea was born to create an APRS-enabled bastion host that would give me access to my internal IT infrastructure in the event of cell phone network unavailability. `secure-aprs-bastion-bot` aims to support this use case.

## Features

- Control of programs using predefined keywords (`--command-code`) and scripts (`--command-string`) associated with these keywords. The user sends a `--command-code` message to `secure-aprs-bastion-bot`, which then executes the local script `--command-string` that is associated to the `--command-code`. **The user is responsible for creating these individual scripts.**
- In addition to the call sign of the incoming message, up to 9 optional parameters can be passed to the `--command-string` as part of the APRS message for control purposes.
- Authorization, authentication, and security:
  - Executable programs are assigned locally per call sign; i.e., `--command-code`s assigned to the call sign `DF1ABC` cannot be accessed by `DF1XYZ` (and vice versa).
  - `secure-aprs-bastion-bot` requires one-time passwords (TOTP) which are individual to each authenticated / configured call sign. The secrets for these tokens are defined when setting up the call sign configuration and can be configured with a validity of 30 seconds to 5 minutes. In addition to the duplicate check of the actual APRS message, an additional TOTP/call sign duplicate check is performed. This check prevents one-time passwords from being used multiple times during their validity period, effectively preventing hi-jacking and misuse of the token in question as best as possible over an unsecured plain-text APRS connection.
- Call sign and command setup:
  - The configuration data is set up and tested using a configuration program provided (`configure.py`).
  - User accounts are configured on a call sign level.
  - The user account configuration can be done at the call sign plus SSID level _or_ exclusively at the call sign level without SSID (base call sign). In the latter case, all call signs of the user _with_ SSID can use the configuration of the call sign _without_ SSID - provided they transmit the base call sign's TOTP token for authorization and authentication.
  - When configuring the base call sign, it is also not necessary to configure all other call signs with SSID individually. The prerequisite for using this configuration is, of course, the use of the TOTP token of the base call sign. Further details can be found in the [configure.py](https://github.com/joergschultzelutter/secure-aprs-bastion-bot/blob/master/docs/configure.md) program documentation.
- Program execution:
  - The programs to be executed can be started either synchronously or as a detached process.
    - Synchronous execution first executes the desired script. After script termination,  `secure-aprs-bastion-bot` sends an APRS confirmation to the user. This is the default behavior.
    - Asynchronous processing first sends the APRS confirmation to the user and starts the desired program as a separate process.  `secure-aprs-bastion-bot` will _not_ wait for the program to finish executing. Such processing may be necessary, for example, when restarting a server.
  - After completion of such a program sequence, regardless of its execution type (synchronous or asynchronous), an APRS message can be sent back to the caller as part of the user script and a supporting Python script (`send-aprs-message.py`). Alternatively, other recommended tools such as [Apprise](https://github.com/caronc/apprise) can be used.

# Program-specific documentation

- [secure-aprs-bastion-bot.py](docs/secure-aprs-bastion-bot.md)
- [configure.py](https://github.com/joergschultzelutter/secure-aprs-bastion-bot/blob/master/docs/configure.md)
- [send-aprs-message.py](https://github.com/joergschultzelutter/secure-aprs-bastion-bot/blob/master/docs/send-aprs-message.md)

## First steps in a nutshell

- Clone this repository
- `pip install -r requirements.txt` (or use the `requirements.txt` file from the respective project's sub directories in case you just want to install a single program)
- Configure the bot`s configuration file:
  - run [configure.py](docs/configure.md) and create at least one user account (`--add-user`), based on a call sign with or without SSID.
  - run [configure.py](docs/configure.md) again and add at least one `--command-code` / `--command-string` relationship entry (`--add-command`) to that user account.
  - Finally, use [configure.py](docs/configure.md) for local configuration file testing
  - The configuration file generated by `configure.py` is then copied to the installation directory of `secure-aprs-bastion-bot` and processed by the bot.
- Amend the bot's configuration file. The bot is based on my `core-aprs-client` framework ([repository link](https://github.com/joergschultzelutter/core-aprs-client)). You might want to [disable e.g. beaconing and/or bulletin messages](https://github.com/joergschultzelutter/core-aprs-client/blob/master/docs/configuration.md).
- Start the bot and send APRS commands (`--command-code`) to it.

## Anatomy of an APRS message to `secure-aprs-bastion-bot`

Every message to `secure-aprs-bastion-bot` always starts with a 6-digit TOTP code. This comes either from the sending call sign with SSID or from its generic call sign without SSID, if its configuration is to be used.

The command to be executed (`--command-code`) follows immediately after the TOTP code - read: no separator. The actual content of this command (`--command-string`) is defined as part of the configuration setup. For example, the user transmits the command `reboot` via APRS, and secure-aprs-bastion-bot then executes the command sequence `source ./scripts/server-reboot.sh` locally on the computer of the secure-aprs-bastion-bot after successful authorization and authentication.

Additional (optional) user-submissable parameters are separated by spaces. The first parameter after `--command-code` corresponds to `$1`, the second parameter to `$2`, and so on (`$1` .. `$9`). Before the command stored in the `--command-string` is executed, the placeholders for these parameters are replaced by these optional parameters, which were transmitted as part of the APRS message.

The additional parameter `$0`, on the other hand, _always_ contains the call sign of the user who sent the message to `secure-aprs-bastion-bot` (e.g., `DF1JSL-1`). `$0` is therefore always present, regardless of whether the APRS user has transmitted additional parameters or not.

Example 1 - `--command-code` without optional parameters

| APRS message             | `TOTP code` | `--command-code` | `$0`        | `$1`  | `$2` | `$3` | .... | `$9` |
| ------------------------ | ----------- |------------------| ----------- | ------| ---- | ---- | ---- | ---- |
| `123456reboot`           | `123456`    | `reboot`         | `DF1JSL-1`  | n/a   | n/a  | n/a  | n/a  | n/a  |


Example 1 - `command-code` with optional parameters

| APRS message             | `TOTP code` | `--command-code` | `$0`        | `$1`       | `$2` | `$3` | .... | `$9` |
| ------------------------ | ----------- |------------------| ----------- | ---------- | ---- | ---- | ---- | ---- |
| `123456reboot debmu41 5` | `123456`    | `reboot`         | `DF1JSL-1`  | `debmu41`  | `5`  | n/a  |      | n/a  |

> [!TIP]
> tl;dr: A user always sends the `--command-code` as an APRS message to the `secure-aprs-bastion-bot`. The bot determines the `--command-code` and any optional parameters from the message, identifies the corresponding `--command-string`, replaces potential placeholders for the optional parameters, and then executes the modified `--command-string`.

To define placeholders for the optional parameters in the `--command-string`, the following conventions apply:
- `$0` ALWAYS corresponds to the call sign that sent the initial message to `secure-aprs-bastion-bot`. This parameter is ALWAYS present.
- `$1` .. `$9` correspond to the additional parameters that (may) have been extracted from the APRS message. Since these are optional, these parameters are not necessarily filled

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

> [!NOTE]
> If the user transmits _more_ optional parameters than there are placeholders in the `--command-string` user script, the additional parameters are ignored by `core-aprs-client`. However, if _fewer_ parameters than required by the `--command-string`user script are transmitted to `core-aprs-client`, this results in a `510 not extended` error - see [this chapter](/README.md#return-codes)

> [!CAUTION]
> You should always create a dedicated script for each keyword, which serves a _single predefined purpose_. Creating a free text keyword, in which the _entire_ command line sequence to be executed is transmitted via APRS message, is technically possible, but is not recommended.

## Return Codes
`secure-aprs-bastion-bot` was deliberately designed so that no output from the called programs is sent back to the requester. If necessary, such a return transmission can be implemented individually via the `--command-code` script using the supplied `send-aprs-message.py` script or other options such as [Apprise](https://www.github.com/caronc/apprise). The following return values are possible:

| Return value       | Description                                                                                                                                                                                                                                                                                                                                                                                                     |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `200 ok`           | The user's call sign and `--command-code` were found in the configuration file. The TOTP code was valid. The `--command-string` was executed. The `--command-string` script was waited for until it finished executing.                                                                                                                                                                                         |
| `202 accepted`     | The user's call sign and `--command-code` were found in the configuration file. The TOTP code was valid. The `--command-string` was started as a separate process. No wait was performed for the `--command-string` script to finish.                                                                                                                                                                           |
| `403 forbidden`    | The call sign and/or the `--command-code` is not stored in the configuration file and/or the transmitted TOTP code is invalid. This is the program's default return code                                                                                                                                                                                                                                        |
| `510 not extended` | The identified `--command-string` still contains placeholders after `core-aprs-client` [replaced the placeholders with the user's additional parameters](/README.md#anatomy-of-an-aprs-message-to-secure-aprs-bastion-bot). Usually, this means that you created a user script with placeholders - but the APRS user did submit an insufficient/lower number of additional parameters to `core-aprs-client`. | 

> [!TIP]
> If you receive a `510 not extended` error, check the number of user-submissable parameter placeholders in your  `--command-string` (`$1`..`$9`) against the number of parameters in your APRS message; he latter must be at least equal to the number of user-transmittable parameter placeholders in your user script. If you transmit more user parameters in your APRS message than are available in your `--command-string`, no error will be triggered; these additional parameters will simply be ignored.

## FAQ

- Q: _Why didn't you include this functionality in your other APRS bots, such as [mpad](https://www.github.com/joergschultzelutter/mpad)?_
- A: `secure-aprs-bastion-bot` does not have a magic wand to grant itself extended user rights. So if you intend to use the APRS bot to implement a `restart` command for your server, `secure-aprs-bastion-bot` must also run with the appropriate user rights (i.e., as a privileged user). Additionally, you also might want to refrain from broadcasting APRS bulletins and/or your bot's location data. These are the main reasons why I created a new APRS bot (rather than adding these functions to one of my existing APRS bots).

- Q: _Tell me more about the TOTP codes and how they are used by `secure-aprs-bastion-bot`._
- A: All TOTP codes can only be used *once*, regardless of their validity period (30 seconds to 5 minutes). This is to prevent TOTP codes with a long validity period from being misused by another party. A valid TOTP code can therefore only be used to execute a *single* `--command-code`. If several `--command-code`s are to be executed, separate valid TOTP codes must be provided for each command. The validity period of TOTP codes can be defined between 30 seconds and 5 minutes; this setting is made once when the user account is created (`--add-user`) and can be different for each user. Depending on the transmission time of an APRS message from the radio device via APRS-IS to the `secure-aprs-bastion-bot`, it is recommended to adjust this setting individually for each user.

- Q: _Is this program safe to use?_
- A: Yes, to a certain extent (see the previous explanations on account configuration and preventing multiple use of valid TOTP codes). Due to the nature of unencrypted APRS messages, there is a theoretical possibility of misuse if an attacker a) obtains a valid __and__ unused TOTP code, b) has knowledge of the `--command-code`s associated with this configuration/call sign, and at the same time c) mimicks the call sign of the original sender (base call sign or call sign with SSID). However, such an attacker would only be able to transmit ONE single `--command-code` to `secure-aprs-bastion-bot`; no additional `--command-code`s would be possible for this TOTP code. I deliberately chose not to include the APRS [tocall device ID](https://github.com/aprsorg/aprs-deviceid) of the original transmitter call sign as an additional identification criterion, as this could also be easily exchanged in the event of spoofing due to the nature of unencrypted APRS messages. Ultimately, certain compromises (due to the nature of APRS messaging) had to be made.

- Q: _Can I use this program even if I am not a licensed radio amateur?_
- A: Since `secure-aprs-bastion-bot` transmits messages to the APRS network, it cannot be used without an amateur radio license.
  
- Q: _Why is it recommended to create dedicated scripts (serving a single predefined purpose) and only use these? Wouldn't it be easier to transfer the whole command line sequence as free text?_
- A: Sure you can. Create a corresponding `--command-code` and fill its associated `--command-string` _exclusively_ with free text parameters (`$1` .. `$9`). You can also drive your car at 200 km/h towards a rock face without wearing a seat belt, swim in shark-infested waters, or jump out of an airplane without a parachute. All of these options carry a real risk of ending very badly. Keep in mind that you would be transmitting sensitive data such as user credentials via an unsecured clear-text transmission media (APRS). See also my earlier comments on program security.

## Technical details

`secure-aprs-bastion-bot` uses my [`core-aprs-client`](https://www.github.com/joergschultzelutter/core-aprs-client) framework.

## The fine print

- If you intend to host an instance of this program, you must be a licensed radio amateur. BYOP: Bring your own (APRS-IS) passcode. If you don't know what this is, then this program is not for you.
- APRS is a registered trademark of APRS Software and Bob Bruninga, WB4APR.
