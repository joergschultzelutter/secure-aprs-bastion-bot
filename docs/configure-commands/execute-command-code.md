# `--execute-command-code`

## Introduction

> [!TIP]
> Use this function to determine whether your combination of call sign and TOTP code is valid and retrieve the [`--command string`](add-command.md#--command-string) for your [`--command code`](add-command.md#--command-code) at the very same time. Once retrieved, the [`--command string`](add-command.md#--command-string) content is then executed. 

## Description
This command uses the same code basis as [`--test-command-code`](test-command-code.md). Instead of printing the [`--command string`](add-command.md#--command-string) information to the console, this option actually executes the retrieved [`--command string`](add-command.md#--command-string) information. 

To give the user the opportunity to cancel the execution of the script, a ten-second countdown is started between the determination of the script and its execution, during which the execution of the script can be terminated at any time by pressing a key. 

After this period has elapsed, the script starts. If it has been configured as a standalone process (--launch-as-subprocess), it starts as a background process. In all other cases, the system waits for the script to finish.

## Parameters

| Command                  | Description                                                                                                                                                                                           | [Parameters](/docs/configure.md#parameters) (mandatory) | [Parameters](/docs/configure.md#parameters) (optional) |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|--------------------------------------------------------|
| `--execute-command-code` | Same as [`--test-command-code`](configure-commands/test-command-code.md), but actually executes the associated [`--command-string`](/docs/configure-commands/add-command.md#--command-string) setting | `--callsign`,`--totp-code`, `--command-code`            | `--aprs-test-arguments`                                |


## Example

`python configure.py --execute-command-code --callsign=df1jsl-1 --command-code=helloworld --totp=502506`  

`python configure.py --test-command-code --callsign=df1jsl-1 --command-code=helloworld --totp=502506 --aprs-test-arguments argument_1 argument_2 argument_3`  
