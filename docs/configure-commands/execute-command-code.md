# `--execute-command-code`

## Introduction

> [!TIP]
> Use this function to determine whether your combination of call sign and TOTP code is valid and retrieve the `--command-string` for your `--command-code` at the very same time. Once retrieved, the `--command-string` content is then executed. 

## Description
This command uses the same code basis as [`--test-command-code`](test-command-code.md). Instead of printing the `command-string` information to the console, this option actually executes the retrieved `command-string` information. 

To give the user the opportunity to cancel the execution of the script, a ten-second countdown is started between the determination of the script and its execution, during which the execution of the script can be terminated at any time by pressing a key. 

After this period has elapsed, the script starts. If it has been configured as a standalone process (--launch-as-subprocess), it starts as a background process. In all other cases, the system waits for the script to finish.

## Example
`--execute-command-code --callsign=df1jsl-1 --command-code=helloworld --totp=502506`  
