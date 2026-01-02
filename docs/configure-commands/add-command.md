# `--add-command`

## Introduction

Adds or updates a [`--command code`](add-command.md#--command-code)/[`--command string`](add-command.md#--command-string) for an existing user (`--callsign`) and writes/updates it to the config file. 

## Description

This option creates or updates the [`--command code`](add-command.md#--command-code)/[`--command string`](add-command.md#--command-string) combination.

The user is responsible for creating the [`--command string`](add-command.md#--command-string) content.

## Parameters

| Command         | Description                                                                          | [Parameters](/docs/configure.md#parameters) (mandatory) | [Parameters](/docs/configure.md#parameters) (optional) |
|-----------------|--------------------------------------------------------------------------------------|---------------------------------------------------------|--------------------------------------------------------|
| `--add-command` | Adds (or updates) a command code/command string for a user to the configuration file | `--callsign`, `--command-code`, `--command-string`      | `--detached-launch`                                    |

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

- `$0` - always represents the call sign from which the APRS message originated. Example: `DF1JSL-1`
- `$1`..`$9` are optional free-text parameters which may have been passed along with the incoming APRS message

### Practical example:

You have designed a [`--command code`](add-command.md#--command-code) keyword `reboot` whose purpose is to reboot a specific server. Instead of hardcoding the server name, you want to pass it along as part of your APRS message. Additionally, you want to send back a message to the APRS callsign once the reboot has completed. To achieve this, you will do the following:

- create a keyword [`--command code`](add-command.md#--command-code) named `reboot`. Its associated [`--command string`](add-command.md#--command-string) script will be responsible for rebooting the server and will accept two parameters:
    - the server name (represented by `$1`)
    - the originating callsign (represented by `$0`)

| `--command-code` | `--command-string`                         |
|------------------|--------------------------------------------|
| `reboot`         | `source ./reboot.sh server=$1 callsign=$0` |

The parameter placeholders defined by the user will later on be replaced by `secure-aprs-bastion-bot` with the values from the APRS message. Note that the order of the parameters is not fixed and can be freely defined by the user. For this example, we assume that the `reboot.sh` script accepts two parameters: parameter 1 is the user's call sign and parameter 2 is the name of the server that we have to reboot. All reboot logic is handled by `reboot.sh` itself. Note that the user is responsible for designing (and locally securing) this script.

Not that we have prepared `secure-aprs-bastion-bot`, let's send the message:

- `DF1JSL-9` transmits an APRS message to the `secure-aprs-bastion-bot`:
    - first six digits = TOTP code (`123456`)
    - followed by the actual keyword (`reboot`)
    - spaces separate additional keywords. We want to reboot a specific machine, e.g. `debmu417`
    - Complete APRS message now looks like this: `123456reboot debmu417`
- Example APRS message: `123456reboot debmu417` results to
    - `$0` translating to value `DF1JSL-9` (remember that this parameter is always present, regardless of whether you have provided addional parameters or not.
    - `$1` translating to value `debmu417`
- `secure-aprs-bastion-bot` will pass along these parameters to the `reboot.sh` script and replace them in the given [`--command string`](add-command.md#--command-string) value, effectively executing `source ./reboot.sh DF1JSL-9 debmu417`. 
- `reboot.sh` is then to restart the `debmu417` server. When completed, it is supposed to send an APRS message back to `DF1JSL-9`, indicating that the reboot has completed.

## Example

Create a [`--command code`](add-command.md#--command-code) named `sayhello`. When sent to `core-aprs-client` is then to execute the [`--command string`](add-command.md#--command-string) with the content `source ./hi.sh`. 

```
python configure.py --add-user --callsign=DF1JSL-1 --command-code=sayhello --command-string="source ./hi.sh"
```

## Config File
```
users:
- callsign: DF1JSL-1
  commands:
    sayhello:
      command_string: source ./hi.sh
      detached_launch: false
  secret: HFV5Z3DBATOSZW24N5QZPHGGSCNRZ7EV
  ttl: 30
```

> [!NOTE]
> `--detached-launch` determines if the bot will wait for the program execution or not

- `detached-launch`==`false` (aka flag is not set) : The `secure-aprs-bastion-bot` will execute the code provided via [`--command string`](add-command.md#--command-string). After its completion, an outgoing APRS message to the sender will be generated. This is the bot's default behavior and is good for situations where a simple task is to be executed.
- `detached-launch`==`true`: First, `secure-aprs-bastion-bot` will send a confirmation message to the sender. Then, it will launch the execution of the [`--command string`](add-command.md#--command-string) code. This is useful for those cases where e.g. you want to reboot the server which hosts the `secure-aprs-bastion-bot` 

Once you have run both [`--add-user`](add-user.md) and `--add-command` commands, you can now use [`--execute-command-code`](execute-command-code.md) for testing of your configuration file.
