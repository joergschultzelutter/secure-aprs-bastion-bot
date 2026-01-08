# `--test-totp-code`

## Table of Contents
<!--ts-->
* [Introduction](#introduction)
* [Description](#description)
* [Parameters](#parameters)
* [Examples](#examples)
<!--te-->

## Introduction

Tests a user's TOTP code against the user's secret and returns a simple "valid" / "invalid" message to the user. 

This function is the “little brother” of [`--execute-command-code`](execute-command-code.md) and can be used as soon as the user has been created using [`--add-user`](add-user.md). Creating [`--command-scripts`](add-command.md) is not necessary for this option, so that the user can already perform initial tests after creating the user.

## Description

`configure.py` will try to read the user entry from the configuration file. If found, it will try to validate the given TOTP code against the user's secret. A simple "code is valid" or "code is invalid" message will get printed to the command line.

## Parameters

| Command            | Description                                                                 | [Parameters](/docs/configure.md#parameters) (mandatory) | [Parameters](/docs/configure.md#parameters) (optional) |
|--------------------|-----------------------------------------------------------------------------|---------------------------------------------------------|--------------------------------------------------------|
| `--test-totp-code` | Tests a given 6-digit TOTP code for validity against the user's TOTP secret | `--callsign`,`--totp-code`                              | n/a                                                    |


## Examples

Assumptions:
- Configured user settings for both `DF1JSL-1` and `DF1JSL` exist in the external YAML configuration file
- A configured user setting for `DF1JSL-15` does _*NOT*_ exist in the external YAML configuration file
- For this example, I assume that the TOTP token values are fixed and do not expire:
  - `DF1JSL-1` has a fixed TOTP token value of 111111
  - `DF1JSL` has a fixed TOTP token value of 000000

Failed attempt, using callsign `DF1JSL-1` and TOTP token value `666666`
```python
python configure.py --test-totp-code --callsign=df1jsl-1 --totp=666666 
2025-08-03 16:56:05,828 configure -INFO- Configuration file 'sabb_command_config.yaml' was successfully read
2025-08-03 16:56:05,828 configure -INFO- Unable to identify matching callsign and/or command_code in configuration file 'sabb_command_config.yaml'; exiting
```  

Successful attempt, using callsign `DF1JSL-1` and TOTP token value `111111`. As the token belongs to `DF1JSL-1`, input and output callsign are identical. Read: we do not perform a wildcard identification. 
```python
python configure.py --test-totp-code --callsign=df1jsl-1 --totp=111111 
2025-08-03 17:13:45,797 configure -INFO- Configuration file 'sabb_command_config.yaml' was successfully read
2025-08-03 17:13:45,798 configure -INFO- Token '111111' matches with target callsign 'DF1JSL-1'
```

Successful attempt, using callsign `DF1JSL-1` and TOTP token value `000000`. As the token belongs to `DF1JSL`, input and output callsign differ and the SSID-less callsign `DF1JSL` is returned.
```python
python configure.py --test-totp-code --callsign=df1jsl-1 --totp=000000 
2025-08-03 17:16:39,736 configure -INFO- Configuration file 'sabb_command_config.yaml' was successfully read
2025-08-03 17:16:39,737 configure -INFO- Token '000000' matches with target callsign 'DF1JSL'
```

Successful attempt, using callsign `DF1JSL-15` and TOTP token value `000000`. As the token belongs to `DF1JSL`, input and output callsign differ and the SSID-less callsign `DF1JSL` is returned. Note that this works even though DF1JSL-15 has no entries in the program's configuration file.
```python
python configure.py --test-totp-code --callsign=df1jsl-15 --totp=000000 
2025-08-03 17:16:39,736 configure -INFO- Configuration file 'sabb_command_config.yaml' was successfully read
2025-08-03 17:16:39,737 configure -INFO- Token '761814' matches with target callsign 'DF1JSL'
```
