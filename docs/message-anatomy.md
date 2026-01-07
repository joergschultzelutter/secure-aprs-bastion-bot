# Anatomy of an APRS message to `secure-aprs-bastion-bot`

Every message to `secure-aprs-bastion-bot` always starts with a 6-digit TOTP code. This comes either from the sending call sign with SSID or from its generic call sign without SSID, if its configuration is to be used.

The command to be executed (`--command-code`) follows immediately after the TOTP code - read: no separator. The actual content of this command (`--command-string`) is defined as part of the configuration setup. For example, the user transmits the command `reboot` via APRS, and secure-aprs-bastion-bot then executes the command sequence `source ./scripts/server-reboot.sh` locally on the computer of the secure-aprs-bastion-bot after successful authorization and authentication.

Additional (optional) user-submittable parameters are separated by spaces. The first parameter after `--command-code` corresponds to `@1`, the second parameter to `@2`, and so on (`@1` .. `@9`). Before the command stored in the `--command-string` is executed, the placeholders for these parameters are replaced by these optional parameters, which were transmitted as part of the APRS message.

The additional parameter `@0`, on the other hand, _always_ contains the call sign of the user who sent the message to `secure-aprs-bastion-bot` (e.g., `DF1JSL-1`); for `configure.py`, this corresponds to the parameter `--callsign`. `@0` is therefore always present, regardless of whether the APRS user has transmitted additional parameters or not. 

Example 1 - `--command-code` without optional parameters

| APRS message             | `TOTP code` | `--command-code` | `@0`       | `@1` | `@2` | `@3` | .... | `@9` |
| ------------------------ | ----------- |------------------|------------|------|------|------| ---- |------|
| `123456reboot`           | `123456`    | `reboot`         | `DF1JSL-1` | n/a  | n/a  | n/a  | n/a  | n/a  |


Example 1 - `command-code` with optional parameters

| APRS message             | `TOTP code` | `--command-code` | `@0`       | `@1`      | `@2` | `@3` | .... | `@9` |
| ------------------------ | ----------- |------------------|------------|-----------|------|------| ---- |------|
| `123456reboot debmu41 5` | `123456`    | `reboot`         | `DF1JSL-1` | `debmu41` | `5`  | n/a  |      | n/a  |

> [!TIP]
> tl;dr: A user always sends the `--command-code` as an APRS message to the `secure-aprs-bastion-bot`. The bot determines the `--command-code` and any optional parameters from the message, identifies the corresponding `--command-string`, replaces potential placeholders for the optional parameters, and then executes the modified `--command-string`.

To define placeholders for the optional parameters in the `--command-string`, the following conventions apply:
- `@0` ALWAYS corresponds to the call sign that sent the initial message to `secure-aprs-bastion-bot`. This parameter is ALWAYS present.
- `@1` .. `@9` correspond to the additional parameters that (may) have been extracted from the APRS message. Since these are optional, these parameters are not necessarily filled

Assuming the previous example `reboot debmu41 5` (sent by `DF1JSL-1`), the following optional parameters are available:
- `@0` = `DF1JSL-1`
- `@1` = `debmu41`
- `@2` = `5`
  
These parameters can be stored in the corresponding `command-string` when setting up the `command-code` keyword. Assuming that the `command-code` `reboot` accepts three parameters for its corresponding `command-string`:
- a wait time until reboot
- a server name
- and the call sign of the original message

The setup for `--command-code`and `--command-string` in the program`s configuration file could then look as follows:

| `--command-code` | `--command-string` (as stored in the config file) |
|------------------|---------------------------------------------------|
| `reboot`         | `source ./scripts/server-reboot.sh @2 @1 @0`      |

First, `secure-aprs-bastion-bot` replaces the placeholders in the string with their actual values:

| `--command-code` | `--command-string` (after modification)                |
|------------------|--------------------------------------------------------|
| `reboot`         | `source ./scripts/server-reboot.sh 5 debmu41 DF1JSL-1` |

The command of the edited `--command-string` is then executed by `secure-aprs-bastion-bot`.

> [!NOTE]
> If the user transmits _more_ optional parameters than there are placeholders in the `--command-string` user script, the additional parameters are ignored by `core-aprs-client`. However, if _fewer_ parameters than required by the `--command-string`user script are transmitted to `core-aprs-client`, this results in a `510 not extended` error - see [this chapter](/docs/return-codes.md)

> [!CAUTION]
> You should always create a dedicated script for each keyword, which serves a _single predefined purpose_. Creating a free text keyword, in which the _entire_ command line sequence to be executed is transmitted via APRS message, is technically possible, but is not recommended.

## Deep-Dive: Understand how user authorization and authentication works

A user entry in the config file can be with or without trailing SSID. Each entry has its very own secret and therefore its very own TOTP code.

User accounts with_OUT_ trailing SSID can act as a 'wildcard' entry. If a user callsign WITH trailing SSID has access to the user account's secret withOUT SSID (and therefore can generate its associated TOTP code), the user account WITH trailing SSID will be granted access to the entries associated with the callsign withOUT SSID .

> [!NOTE]
> Instead of creating the same configuration redundantly for all SSIDs of the callsign, for example, it can be configured only once for the main callsign (_without_ SSID) and used by all associated callsigns _with_ SSID, provided that they then provide the token of the main call sign for authentication and authorization.

Let's have a look at a scenario where we assume that the given TOTP code never expires and that both call signs `DF1JSL` and `DF1JSL-1` are present
in the external YAML configuration file. Additionally, `DF1JSL-15` will NOT have a configuration entry in that configuration file.

- Callsign 1: `DF1JSL-1`, TOTP : `123456` (based on `DF1JSL-1`'s secret)
- Callsign 2: `DF1JSL`, TOTP : `471123` (based on `DF1JSL`'s secret)
- Callsign 3: `DF1JSL-15`. This call sign is __NOT__ present in the YAML configuration file and therefore has not been assigned its own TOTP secret.

| Call sign in APRS message   | TOTP in APRS message | Access permitted   | Configuration data will be taken from                                                                                                                                 |
|-----------------------------|----------------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `DF1JSL-1`                  | `123456`             | :white_check_mark: | `DF1JSL-1`                                                                                                                                                            |
| `DF1JSL-1`                  | `471123`             | :white_check_mark: | `DF1JSL`                                                                                                                                                              |
| `DF1JSL-1`                  | `483574`             | :x:                | TOTP/Secret mismatch                                                                                                                                                  |
| `DF1JSL`                    | `123456`             | :x:                | SSID-less callsign (base callsign) cannot access callsign with SSID                                                                                                   |
| `DF1JSL`                    | `471123`             | :white_check_mark: | `DF1JSL`                                                                                                                                                              |
| `DF1JSL`                    | `999999`             | :x:                | TOTP/Secret mismatch                                                                                                                                                  |
| `DF1JSL-15`                 | `555577`             | :x:                | TOTP/Secret mismatch                                                                                                                                                  |
| `DF1JSL-15`                 | `123456`             | :x:                | TOTP/Secret mismatch. It is not possible to access one call sign with SSID from another call sign with SSID, even if both call signs share the same base call sign.   |
| `DF1JSL-15`                 | `471123`             | :white_check_mark: | `DF1JSL`                                                                                                                                                              |

So instead of adding the very same configuration to each one of your multiple call signs WITH SSID, you _can_ add these to the SSID-less base sign's entry. For accessing these settings from your call sign WITH SSID, you will need to specify the TOTP token for the base call sign withOUT SSID. Note also that the base callsign withOUT SSID will NOT be able to access the configuration entries for those call signs WITH SSID.

As indicated, `DF1JSL-15` is NOT part of the YAML configuration file. Yet, it still can access `DF1JSL`'s config entries
because the user knows `DF1JSL`'s secret and was able to generate a valid token (`4771123`) that was based on that secret.

> [!WARNING]
> With great power comes great responsibility. If you want to be on the safe side, do not use the SSID-less callsign option but rather use a single dedicated callsign instead.
