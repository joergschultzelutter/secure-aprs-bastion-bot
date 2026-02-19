# `--add-command`

## Table of Contents
<!--ts-->
* [Introduction](#introduction)
* [Description](#description)
* [Parameters](#parameters)
  * [`--command-code`](#--command-code)
  * [`--command-string`](#--command-string)
  * [Examples](#examples)
  * [Practical example](#practical-example)
  * [Example 1](#example-1)
  * [Config file after Example 1](#config-file-after-example-1)
  * [Example 2](#example-2)
  * [Config file after Example 2](#config-file-after-example-2)
* [`--detached-launch`](#--detached-launch)
* [`--watchdog-timespan`](#--watchdog-timespan)
<!--te-->

## Introduction

Adds or updates a [`--command code`](add-command.md#--command-code)/[`--command string`](add-command.md#--command-string) for an existing user (`--callsign`) and writes/updates it to the config file. 

## Description

This option creates or updates the [`--command code`](add-command.md#--command-code)/[`--command string`](add-command.md#--command-string) combination.

The user is responsible for creating the [`--command string`](add-command.md#--command-string) content.

## Parameters

| Command         | Description                                                                          | [Parameters](/docs/configure.md#parameters) (mandatory) | [Parameters](/docs/configure.md#parameters) (optional) |
|-----------------|--------------------------------------------------------------------------------------|---------------------------------------------------------|--------------------------------------------------------|
| `--add-command` | Adds (or updates) a command code/command string for a user to the configuration file | `--callsign`, `--command-code`, `--command-string`      | `--detached-launch`, `--watchdog-timespan`             |

### `--command-code`

A [`--command code`](add-command.md#--command-code) is an alias for the [`--command string`](add-command.md#--command-string) entry. [`--command code`](add-command.md#--command-code) entries will be sent be the user via APRS messaging to the bot - which will then execute the associated [`--command string`](add-command.md#--command-string)

> [!NOTE]
> [`--command code`](add-command.md#--command-code) must not contain any space characters as spaces are used for separating the [`--command code`](add-command.md#--command-code) from additional parameters in the message; see [`--command string`](add-command.md#--command-string)

Example:

| APRS `--command-code` ... | ... translates to `--command-string` |
|---------------------------|--------------------------------------|
| `sayhello`                | `source ./hi.sh`                     |

### `--command-string`

The `command-string` supports up to 10 parameters which you can pass along with your APRS message. If detected, `secure-aprs-bastion-bot` will retrieve those parameters from the APRS message and replace the placeholders in the `command-string` value prior to executing it. See [this documentation](/README.md#anatomy-of-an-aprs-message-to-secure-aprs-bastion-bot) for further details.

Supported placeholders:

- `@0` - ALWAYS represents the callsign from which the APRS message originated. Example: `DF1JSL-1`
- `@1`..`@9` are optional free-text parameters which may have been passed along with the incoming APRS message

## Examples

### Practical example

You have designed a [`--command code`](add-command.md#--command-code) keyword `reboot` whose purpose is to reboot a specific server. Instead of hardcoding the server name, you want to pass it along as part of your APRS message. Additionally, you want to send back a message to the APRS callsign once the reboot has completed. To achieve this, you will do the following:

- create a keyword [`--command code`](add-command.md#--command-code) named `reboot`. Its associated [`--command string`](add-command.md#--command-string) script will be responsible for rebooting the server and will accept two parameters:
    - the server name (represented by `@1`)
    - the originating callsign (represented by `@0`)

| `--command-code` | `--command-string`                         |
|------------------|--------------------------------------------|
| `reboot`         | `source ./reboot.sh server=@1 callsign=@0` |

The parameter placeholders defined by the user will later on be replaced by `secure-aprs-bastion-bot` with the values from the APRS message. Note that the order of the parameters is not fixed and can be freely defined by the user. For this example, we assume that the `reboot.sh` script accepts two parameters: parameter 1 is the user's callsign and parameter 2 is the name of the server that we have to reboot. All reboot logic is handled by `reboot.sh` itself. Note that the user is responsible for designing (and locally securing) this script.

Not that we have prepared `secure-aprs-bastion-bot`, let's send the message:

- `DF1JSL-9` transmits an APRS message to the `secure-aprs-bastion-bot`:
    - first six digits = TOTP code (`123456`)
    - followed by the actual keyword (`reboot`)
    - spaces separate additional keywords. We want to reboot a specific machine, e.g. `debmu417`
    - Complete APRS message now looks like this: `123456reboot debmu417`
- Example APRS message: `123456reboot debmu417` results to
    - `@0` translating to value `DF1JSL-9` (remember that this parameter is always present, regardless of whether you have provided addional parameters or not.
    - `@1` translating to value `debmu417`
- `secure-aprs-bastion-bot` will pass along these parameters to the `reboot.sh` script and replace them in the given [`--command string`](add-command.md#--command-string) value, effectively executing `source ./reboot.sh DF1JSL-9 debmu417`. 
- `reboot.sh` is then to restart the `debmu417` server. When completed, it is supposed to send an APRS message back to `DF1JSL-9`, indicating that the reboot has completed.

### Example 1

Create a [`--command code`](add-command.md#--command-code) named `sayhello`. When sent to `core-aprs-client` is then to execute the [`--command string`](add-command.md#--command-string) with the content `echo Hello World`. 

```python
python configure.py --add-command --callsign df1jsl-1 --command-code=sayhello --command-string=echo Hello World 
2026-01-03 19:08:58,618 - configure -INFO - Adding new command-code 'sayhello' config for user 'DF1JSL-1'
2026-01-03 19:08:58,619 - configure -INFO - Configuration file 'sabb_command_config.yml' was successfully read
2026-01-03 19:08:58,620 - configure -INFO - Configuration file 'sabb_command_config.yml' was successfully written
2026-01-03 19:08:58,620 - configure -INFO - Command 'sayhello' for user 'DF1JSL-1' added to config file
```

### Config File after Example 1
```yaml
users:
- callsign: DF1JSL-1
  commands:
    sayhello:
      command_string: echo Hello World
      detached_launch: false
      watchdog_timespan: 0.0
  secret: GJYWOPM5YW22OD4REQDP75APVEGMNX4N
  ttl: 30
```

### Example 2

Add an additional [`--command code`](add-command.md#--command-code) named `greetuser`. When sent to `core-aprs-client` is then to execute the [`--command string`](add-command.md#--command-string) with the content `echo Hello`, followed by the callsign of the user that has sent the message. See the project's [README.MD](/README.md#anatomy-of-an-aprs-message-to-secure-aprs-bastion-bot) on how to use these additional parameters. For this example, we will simply use the `$0` parameter which represents the sender's callsign.

```python
/Users/jsl/git/secure-aprs-bastion-bot/.venv/bin/python /Users/jsl/git/secure-aprs-bastion-bot/src/secure-aprs-bastion-bot/configure.py --add-command --callsign df1jsl-1 --command-code=greetuser --command-string=echo Hello $0 
2026-01-03 19:19:47,962 - configure -INFO - Adding new command-code 'greetuser' config for user 'DF1JSL-1'
2026-01-03 19:19:47,963 - configure -INFO - Configuration file 'sabb_command_config.yml' was successfully read
2026-01-03 19:19:47,964 - configure -INFO - Configuration file 'sabb_command_config.yml' was successfully written
2026-01-03 19:19:47,964 - configure -INFO - Command 'greetuser' for user 'DF1JSL-1' added to config file
```

### Config File after Example 2
```yaml
users:
- callsign: DF1JSL-1
  commands:
    greetuser:
      command_string: echo Hello $0
      detached_launch: false
      watchdog_timespan: 0.0
    sayhello:
      command_string: echo Hello World
      detached_launch: false
      watchdog_timespan: 0.0
  secret: GJYWOPM5YW22OD4REQDP75APVEGMNX4N
  ttl: 30
```

## `--detached-launch`

`--detached-launch` determines if the bot will wait for the program execution or not

- `detached-launch`==`true`: First, `secure-aprs-bastion-bot` will send a confirmation message to the sender. Then, it will launch the execution of the [`--command string`](add-command.md#--command-string) code. This is useful for those cases where e.g. you want to reboot the server which hosts the `secure-aprs-bastion-bot` 
- `detached-launch`==`false` (aka flag is not set) : The `secure-aprs-bastion-bot` will execute the code provided via [`--command string`](add-command.md#--command-string). After its completion, an outgoing APRS message to the sender will be generated. This is the bot's default behavior and is good for situations where a simple task is to be executed.  

## `--watchdog-timespan`

`detached-launch`==`false` supports an optional `--watchdog-timespan` setting. 

A `--watchdog-timespan` value equal to `0.0` __disables__ the watchdog, meaning that `secure-aprs-bastion-bot` will wait until the `--command-string` has finished processing. This is the standard behavior. 

A value __greater__ than `0.0` will first launch the `--command-string`. After the given timespan has passed, `secure-aprs-bastion-bot` will __*try*__ to abort the execution of the `--command-string` sequence. 

Dependent on your individual program configuration, this may or may not work properly. When used with an active `--watchdog-timespan`, I __*strongly*__ recommend testing this scenario with `configure.py` prior to deploying your configuration to production - _especially_ when running `secure-aprs-bastion-bot` on a Windows-based platform.

Once you have run both [`--add-user`](add-user.md) and `--add-command` commands, you can now use [`--execute-command-code`](execute-command-code.md) for testing of your configuration file.
