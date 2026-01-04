# `configure.py`

This program is used for the creation of [secure-aprs-bastion-bot](secure-aprs-bastion-bot.md)'s YAML configuration file. It supports a couple of actions such as:

- Create / Update ([`--add-user`](configure-commands/add-user.md)) / Delete ([`--delete-user`](configure-commands/delete-user.md)) a user entry along with its associated TOTP secret
- Create / Update ([`--add-command`](configure-commands/add-command.md)) / Delete ([`--delete-command`](configure-commands/delete-command.md)) a user's command code / command line entries
- Test the TOTP token against the user's TOTP secret ([`--test-totp-code`](configure-commands/test-totp-code.md))
- Retrieve and/or execute a user / command code combination ([`--execute-command-code`](configure-commands/execute-command-code.md))

[secure-aprs-bastion-bot](secure-aprs-bastion-bot.md) will use the resulting configuration file. Note that `configure.py` acts as both configuration tool and gatekeeper / validator; `secure-aprs-bastion-bot` itself assumed that the configuration file structure is valid and hardly performs any validation checks. You can apply manual changes to most sections of the configuration file - but if it breaks, you get to keep both pieces.

## Table of contents

blah

## Parameter Options - Overview

```bash
python configure.py --help
usage: configure.py [-h] 
                    [--configfile CONFIG_FILE] 
                    [--add-user] 
                    [--delete-user] 
                    [--add-command] 
                    [--delete-command] 
                    [--test-totp-code] 
                    [--dry-run] 
                    [--execute-command-code] 
                    [--show-secret] 
                    [--callsign CALLSIGN] 
                    [--totp-code TOTP_CODE] 
                    [--command-code COMMAND_CODE] 
                    [--command-string COMMAND_STRING]
                    [--detached-launch] 
                    [--ttl TTL] 
                    [--watchdog-timespan WATCHDOG_TIMESPAN] 
                    [--aprs-test-arguments [APRS_TEST_ARGUMENTS ...]]

options:
  -h, --help                      show this help message and exit
  --configfile                    CONFIG_FILE
                                  Program config file name (default: sabb_command_config.yml)
  --add-user                      Add a new call sign plus secret to the configuration file
  --delete-user                   Remove a user with all data from the configuration file
  --add-command                   Add a new command for an existing user to the configuration file
  --delete-command                Remove a command from a user's configuration in the configuration file
  --test-totp-code                Validates the provided TOTP code against the user's secret
  --dry-run                       In combination with --execute-command-code, causes the execution of the script to be simulated only
  --execute-command-code          Looks up the call sign / command code combination in the YAML file and executes it
  --show-secret                   Shows the user's secret during the -add-user configuration process (default: disabled)
  --callsign CALLSIGN             Callsign (must follow call sign format standards)
  --totp-code TOTP_CODE           6 digit TOTP code - submitted for configuration testing only
  --command-code COMMAND_CODE     Command code which will be sent to the APRS bot for future execution
  --command-string COMMAND_STRING Command string that is associated with the user's command code
  --detached-launch               If specified: launch the command as a detached subprocess and do not wait for its completion
  --ttl TTL                       TTL value in seconds (default: 30; range: 30-300)
  --watchdog-timespan             WATCHDOG_TIMESPAN
                                  Watchdog timespan in seconds (0.0 = disable). Only applicable to --detached-launch configuration settings
  --aprs-test-arguments           [APRS_TEST_ARGUMENTS ...]
                                  For testing purposes only; list of 0 to 9 APRS arguments, Used in conjunction with --execute-command-code
```

## Parameters

>[!TIP]
> Details on the parameter settings con be found on the [`--add-user`](/docs/configure-commands/add-user.md) and [`--add-command`](/docs/configure-commands/add-command.md) subsections.

| Parameter                                            | Description                                                                                                                                                                                                                                                                                                                                                          | Type          | Default                   |
|------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|---------------------------|
| `--configfile`                                       | External config file. `configure.py` will create this file if it does not exist.                                                                                                                                                                                                                                                                                     | `str`         | `sabb_command_config.yml` |
| `--callsign`                                         | User's call sign, with or without SSID                                                                                                                                                                                                                                                                                                                               | `str`         | `<none>`                  |
| `--totp-code`                                        | Six-digit TOTP code                                                                                                                                                                                                                                                                                                                                                  | `str`         | `<none>`                  |
| [`--command-code`](configure.md#--command-code)      | Command code alias. This is the code that the user will send in his APRS message. Associated with [`--command-string`](/docs/configure-commands/add-command.md#--command-string)                                                                                                                                                                                     | `str`         | `<none>`                  |
| [`--command-string`](configure.md#--command-string)  | Associated with [`--command-code`](/docs/configure-commands/add-command.md#--command-code). This is a representation of the actual command that is going to get executed.                                                                                                                                                                                            | `str`         | `<none>`                  |
| `--detached-launch`                                  | When specified (read:`detached-launch`=`True`), the bot will NOT wait for the [`--command-string`](/docs/configure-commands/add-command.md#--command-string)'s program execution. In addition, the APRS confirmation will be sent to the user _prior_ to the program's execution. Default setting: `False` --> Bot _will_ wait for the end of the program execution. | `bool`        | `False`                   |
| `--ttl`                                              | TOTP TTL value in seconds (`30`..`300`). Default: 30 (seconds)                                                                                                                                                                                                                                                                                                       | `int`         | `30`                      |
| `--dry-run`                                          | When used in combination with `-execute-command-code`, the execution of the associated `--command-script` will only be simulated                                                                                                                                                                                                                                     | `bool`        | `False`                   |
| `--watchdog-timespan`                                | Only applicable for `detached-launch`=`False` configurations. A value of `0.0` (default) will disable the watchdog. Any other positive value will _try_ to abort the previously started process after the given timespan has passed.                                                                                                                                 | `bool`        | `False`                   |
| `--aprs-test-arguments`                              | Used in combination with [`--execute-command-code`](configure.md#--execute-command-code---executes-a---callsign--commannd-code-combination). Simulates the parameter input `$1`..`$9` from an incoming APRS message. 0..9 parameters are supported. Parameter separator = space. Input Parameter `$0` _always_ contains the user's callsign.                         | list of `str` | `[]` (empty list)         |

## Commands

All commands are described in the linked documentation files.

| Command                                                                  | Description                                                                                                                                                                                                                                                                                                                                              | Associated parameter(s)                                                                     |
|--------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| [`--add-user`](configure-commands/add-user.md)                           | Adds (or updates) a user to the configuration file                                                                                                                                                                                                                                                                                                       | `--callsign`,`-ttl`,`--show-secret`                                                         |
| [`--delete-user`](configure-commands/delete-user.md)                     | Deletes a user from the configuration file                                                                                                                                                                                                                                                                                                               | `--callsign`                                                                                |
| [`--add-command`](configure-commands/add-command.md)                     | Adds (or updates) a command code/command string for a user to the configuration file                                                                                                                                                                                                                                                                     | `--callsign`,`--detached-launch`,`--command-code`,`--command-string`, `--watchdog-timespan` |
| [`--delete-command`](configure-commands/delete-command.md)               | Deletes a command code for a user from the configuration file                                                                                                                                                                                                                                                                                            | `--callsign`,`--command-code`                                                               |
| [`--test-totp-code`](configure-commands/test-totp-code.md)               | Tests a given 6-digit TOTP code for validity against the user's TOTP secret                                                                                                                                                                                                                                                                              | `--callsign`,`--totp-code`                                                                  |
| [`--execute-command-code`](configure-commands/execute-command-code.md)   | Uses a `--callsign` / [`--command-code`](/docs/configure-commands/add-command.md#--command-code) combination, returns the associated [`--command-string`](/docs/configure-commands/add-command.md#--command-string) (whereas present) and executes the associated [`--command-string`](/docs/configure-commands/add-command.md#--command-string) setting | `--callsign`,`--totp-code`, `--command-code`, `--aprs-test-arguments`, `--dry-run`          |

## Usage

- First, run [`--add-user`](configure-commands/add-user.md) and create 1...n user accounts in the configuration file. Use [`--test-totp-code`](configure-commands/test-totp-code.md) and check if your user account's secret validates against the TOTP code on your mobile device.
- Then, run [`--add-command`](configure-commands/add-command.md) for each of these user accounts and create 1...n [`--command-code`](/docs/configure-commands/add-command.md#--command-code)/[`--command-string`](/docs/configure-commands/add-command.md#--command-string) entries (you can also use an editor for this step). Use [`--execute-command-code`](configure-commands/execute-command-code.md) for testing.

## Deep-Dive: Understand how user authorization / authentication works

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

### Manual edits to the YAML configuration file

Except for the `--add-user` functionality which generates the user's TOTP secret, you are free to apply manual changes to the external YAML configuration file. The following constraints apply:

- `--callsign` information is always stored uppercase in the configuration file (e.g. `DF1JSL-1` and not `df1jsl-1`)
- `--command-code` information is always stored lowercase in the configuration file (e.g. `sayhello` and not `SayHello`, `SAYHELLO` etc).

When in doubt, always use `configure.py` for abiding to these constraints.
