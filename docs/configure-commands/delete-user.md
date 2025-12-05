# `--delete-user` - deletes a user from the config file

## Introduction

`--delete-user` deletes a user from the configuration file.

## Description

This command deletes a user (along with **all** of his settings, including [`--command-code`](add-command.md#--command-code) / [`--command-string`](add-command.md#--command-string) entries) from the configuration file.

| Command         | Description                                                                                                      | Associated parameter(s)                                                   |
|-----------------|------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| `--delete-user` | Deletes a user from the configuration file                                                                       | `--callsign`                                                              |

## Example
```
python configure.py --delete-user --callsign=DF1JSL-1
```
