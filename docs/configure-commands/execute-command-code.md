# `--execute-command-code`

## Introduction

> [!TIP]
> Use this function to determine whether your combination of call sign and TOTP code is valid and retrieve the [`--command string`](add-command.md#--command-string) for your [`--command code`](add-command.md#--command-code) at the very same time. Once retrieved, the [`--command string`](add-command.md#--command-string) content is then executed. You can simulate the entire execution process with the optional parameter `--dry-run`. 

## Description
This is an extended version of [`--test-totp-code`](test-totp-code.md). In addition to validating the call sign-TOTP code combination, it also attempts to determine the corresponding [`--command string`](add-command.md#--command-string) using the specified [`--command code`](add-command.md#--command-code). If the user has also passed `----aprs-test-arguments`, it will attempt to replace their placeholders in the [`--command string`](add-command.md#--command-string). 

To give the user the opportunity to cancel the execution of the script, a ten-second countdown is started between the determination of the script and its execution, during which the execution of the script can be terminated at any time by pressing a key. 

After this period has elapsed, the script starts. If it has been configured as a standalone process (`--launch-as-subprocess`), it starts as a background process. In all other cases, the system waits for the script to finish unless an optional `--watchdog-timespan` has been set. You can simulate the entire execution process with the optional parameter `--dry-run`.

## Parameters

| Command                  | Description                                                                                                                                                                                                                                                                                                                                             | [Parameters](/docs/configure.md#parameters) (mandatory) | [Parameters](/docs/configure.md#parameters) (optional)     |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|------------------------------------------------------------|
| `--execute-command-code` | Uses a `--callsign` / [`--command-code`](/docs/configure-commands/add-command.md#--command-code) combination,returns the associated [`--command-string`](/docs/configure-commands/add-command.md#--command-string) (whereas present) and executes the associated [`--command-string`](/docs/configure-commands/add-command.md#--command-string) setting | `--callsign`,`--totp-code`, `--command-code`            | `--aprs-test-arguments`, `--watchdog-timespan`,`--dry-run` |


## Example

`python configure.py --execute-command-code --callsign=df1jsl-1 --command-code=helloworld --totp=502506`  

`python configure.py --execute-command-code --callsign=df1jsl-1 --command-code=helloworld --totp=502506 --aprs-test-arguments argument_1 argument_2 argument_3`  
