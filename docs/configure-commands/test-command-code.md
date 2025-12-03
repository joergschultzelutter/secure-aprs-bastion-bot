# `--test-command-code`

## Introduction

> [!TIP]
> Use this function to determine whether your combination of call sign and TOTP code is valid and retrieve the `--command-string` for your `--command-code` at the very same time.

## Description

> [!NOTE]
> This is an extended version of `--test-totp-code`. In addition to validating the call sign-TOTP code combination, it also attempts to determine the corresponding `--command-string` using the specified `--command-code`. If the user has also passed `----aprs-test-arguments`, it will attempt to replace their placeholders in the `--command-string`. 
> When using `--test-command-code`, only the final `--command-string` is output on the command line; `--execute-command-code`, on the other hand, also executes the determined `--command-string`.

## Example
`--execute-totp-code --callsign=df1jsl-1 --command-code=helloworld --totp=502506 --aprs-test-arguments argument_1 argument_2 argument_3`  
