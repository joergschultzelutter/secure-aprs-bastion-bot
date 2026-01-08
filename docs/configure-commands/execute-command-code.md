# `--execute-command-code`

## Table of Contents
<!--ts-->
* [Introduction](#introduction)
* [Description](#description)
* [Parameters](#parameters)
* [Example](#example)
  * [Config file before modification](#config-file-before-modification)
  * [Execute command deletion](#execute-command-deletion)
  * [Config file after modification](#config-file-after-modification)
<!--te-->


## Introduction

> [!TIP]
> Use this function to determine whether your combination of callsign and TOTP code is valid and retrieve the [`--command string`](add-command.md#--command-string) for your [`--command code`](add-command.md#--command-code) at the very same time. Once retrieved, the [`--command string`](add-command.md#--command-string) content is then executed. You can simulate the entire execution process with the optional parameter `--dry-run`. 

## Description
This is an extended version of [`--test-totp-code`](test-totp-code.md). In addition to validating the callsign-TOTP code combination, it also attempts to determine the corresponding [`--command string`](add-command.md#--command-string) using the specified [`--command code`](add-command.md#--command-code). If the user has also passed `----aprs-test-arguments`, it will attempt to replace their placeholders in the [`--command string`](add-command.md#--command-string). 

To give the user the opportunity to cancel the execution of the script, a ten-second countdown is started between the determination of the script and its execution, during which the execution of the script can be terminated at any time by pressing a key.

After this period has elapsed, the script starts. If it has been configured as a standalone process (`--detached-launch`), it starts as a background process. In all other cases, the system waits for the script to finish unless an optional `--watchdog-timespan` has been set. You can simulate the entire execution process with the optional parameter `--dry-run`.

## Parameters

| Command                  | Description                                                                                                                                                                                                                                                                                                                                             | [Parameters](/docs/configure.md#parameters) (mandatory) | [Parameters](/docs/configure.md#parameters) (optional) |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|--------------------------------------------------------|
| `--execute-command-code` | Uses a `--callsign` / [`--command-code`](/docs/configure-commands/add-command.md#--command-code) combination,returns the associated [`--command-string`](/docs/configure-commands/add-command.md#--command-string) (whereas present) and executes the associated [`--command-string`](/docs/configure-commands/add-command.md#--command-string) setting | `--callsign`,`--totp-code`, `--command-code`            | `--aprs-test-arguments`, `--dry-run`                   |


## Example

### Invalid user, TOTP Code or some other error

```python
python configure.py --execute-command-code --callsign=df1jsl-1 --command-code=invalidcommand --totp=123456

2026-01-08 20:39:43,270 - configure -INFO - Configuration file 'sabb_command_config.yml' was successfully read
2026-01-08 20:39:43,270 - configure -INFO - Unable to identify matching callsign and/or command_code for given TOTP code in configuration file 'sabb_command_config.yml'; exiting
```

### Run command with additional APRS parameters
```python
python configure.py --execute-command-code --callsign=df1jsl --command-code=helloworld --aprs-test-arguments HelloWorld --totp 264466
2026-01-08 20:50:33,565 - configure -INFO - Configuration file 'sabb_command_config.yml' was successfully read
2026-01-08 20:50:33,565 - configure -INFO - Command 'helloworld' translates to target callsign 'DF1JSL' and command_string 'helloworld.sh @0 @1' with detached_launch='True' and watchdog='disabled'
2026-01-08 20:50:33,565 - configure -INFO - Replacing potential APRS parameters in the command string.
2026-01-08 20:50:33,565 - configure -INFO - Command_string after replacement process: 'helloworld.sh DF1JSL HelloWorld'
2026-01-08 20:50:33,566 - configure -INFO - Executing command '/Users/jsl/greetuser.sh DF1JSL HelloWorld' in 10 seconds
2026-01-08 20:50:33,566 - configure -INFO - Press any key within 10 secs to abort command execution ...
2026-01-08 20:50:43,568 - configure -INFO - Executing code ....
2026-01-08 20:50:43,572 - sabb_utils -INFO - Process started with PID=58029



```
