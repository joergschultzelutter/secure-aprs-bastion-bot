# `--delete-user` - deletes a user from the config file

## Introduction

`--delete-user` deletes a user from the configuration file.

## Description

This command deletes a user (along with **all** of his settings, including [`--command-code`](add-command.md#--command-code) / [`--command-string`](add-command.md#--command-string) entries) from the configuration file.

## Parameters

| Command         | Description                                                                                                      | [Parameters](/docs/configure.md#parameters) (mandatory)| [Parameters](/docs/configure.md#parameters) (optional)|
|-----------------|------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------|-------------------------------------------------------|
| `--delete-user` | Deletes a user from the configuration file                                                                       | `--callsign`                                           | n/a                                                   |

## Example
```
python configure.py --delete-user --callsign=DF1JSL-1
```
