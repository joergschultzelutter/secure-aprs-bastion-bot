# `--test-command-code`

## Introduction

> [!TIP]
> Use this function to determine whether your combination of call sign and TOTP code is valid and retrieve the [`--command string`](add-command.md#--command-string) for your [`--command code`](add-command.md#--command-code) at the very same time.

## Description

> [!NOTE]
> This is an extended version of [`--test-totp-code`](test-totp-code.md). In addition to validating the call sign-TOTP code combination, it also attempts to determine the corresponding [`--command string`](add-command.md#--command-string) using the specified [`--command code`](add-command.md#--command-code). If the user has also passed `----aprs-test-arguments`, it will attempt to replace their placeholders in the [`--command string`](add-command.md#--command-string). 
> When using `--test-command-code`, only the final [`--command string`](add-command.md#--command-string) is output on the command line; `--execute-command-code`, on the other hand, also executes the determined [`--command string`](add-command.md#--command-string).

## Parameters

| Command               | Description                                                                                                                                                                                                                              | [Parameters](/docs/configure.md#parameters) (mandatory) | [Parameters](/docs/configure.md#parameters) (optional) |
|-----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|--------------------------------------------------------|
| `--test-command-code` | Uses a `--callsign` / [`--command-code`](/docs/configure-commands/add-command.md#--command-code) combination and returns the associated [`--command-string`](/docs/configure-commands/add-command.md#--command-string) (whereas present) | `--callsign`,`--totp-code`, `--command-code`            | `--aprs-test-arguments`                                |

## Examples

### Successful retrieval with parameter replacement

```python
# test-command-code with optional APRS parameters
python configure.py --test-command-code --callsign=df1jsl-1 --command-code=helloworld --totp-code=502506 --aprs-test-arguments hallo Welt  
2025-12-20 22:31:26,743 configure -INFO- Configuration file 'sabb_command_config.yaml' was successfully read
2025-12-20 22:31:26,743 configure -INFO- Command 'hello' translates to target call sign 'DF1JSL-1' and command_string 'Hello W0rld $0 $1' with detached_launch='True'
2025-12-20 22:31:26,743 configure -INFO- Replacing potential APRS parameters in the command string.
2025-12-20 22:31:26,743 configure -INFO- Command_string after replacement process: 'Hello W0rld DF1JSL-1 hallo'
```

### Less additional parameters than required

See [return code](/README.md#return-codes) information for further details. The following example illustrates a case where the user has set up a `--command-string` with additional parameters but did not provide enough parameters via his APRS message.

```python
/Users/jsl/git/secure-aprs-bastion-bot/.venv/bin/python /Users/jsl/git/secure-aprs-bastion-bot/src/configure/configure.py --test-command-code --callsign df1jsl-1 --command-code hello --totp-code 429723 
2025-12-20 22:44:48,333 configure -INFO- Configuration file 'sabb_command_config.yaml' was successfully read
2025-12-20 22:44:48,333 configure -INFO- Command 'hello' translates to target call sign 'DF1JSL-1' and command_string 'Hello W0rld $0 $1' with detached_launch='True'
2025-12-20 22:44:48,333 configure -INFO- Replacing potential APRS parameters in the command string.
2025-12-20 22:44:48,333 configure -INFO- Command_string after replacement process: 'Hello W0rld DF1JSL-1 $1'
2025-12-20 22:44:48,333 configure -ERROR- 510 not extended
2025-12-20 22:44:48,333 configure -ERROR- Your final command string still contains placeholders; did you specify all parameters?
2025-12-20 22:44:48,333 configure -ERROR- Final command string: 'Hello W0rld DF1JSL-1 $1'
```

### Unsuccessful retrieval (not found, invalid TOTP code, ...)

```python
/Users/jsl/git/secure-aprs-bastion-bot/.venv/bin/python /Users/jsl/git/secure-aprs-bastion-bot/src/configure/configure.py --test-command-code --callsign df1jsl-1 --command-code hello --totp-code 429723 
2025-12-20 22:48:31,194 configure -INFO- Configuration file 'sabb_command_config.yaml' was successfully read
2025-12-20 22:48:31,195 configure -INFO- Unable to identify matching call sign and/or command_code for given TOTP code in configuration file 'sabb_command_config.yaml'; exiting
```