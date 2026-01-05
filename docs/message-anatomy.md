# Anatomy of an APRS message to `secure-aprs-bastion-bot`

Every message to `secure-aprs-bastion-bot` always starts with a 6-digit TOTP code. This comes either from the sending call sign with SSID or from its generic call sign without SSID, if its configuration is to be used.

The command to be executed (`--command-code`) follows immediately after the TOTP code - read: no separator. The actual content of this command (`--command-string`) is defined as part of the configuration setup. For example, the user transmits the command `reboot` via APRS, and secure-aprs-bastion-bot then executes the command sequence `source ./scripts/server-reboot.sh` locally on the computer of the secure-aprs-bastion-bot after successful authorization and authentication.

Additional (optional) user-submittable parameters are separated by spaces. The first parameter after `--command-code` corresponds to `$1`, the second parameter to `$2`, and so on (`$1` .. `$9`). Before the command stored in the `--command-string` is executed, the placeholders for these parameters are replaced by these optional parameters, which were transmitted as part of the APRS message.

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

