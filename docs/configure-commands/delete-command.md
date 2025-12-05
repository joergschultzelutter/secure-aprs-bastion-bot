# `--delete-command` - deletes a command code/command string from the config file

## Introduction

Deletes a single [`--command-code`](add-command.md#--command-code) / [`--command-string`](add-command.md#--command-string) combination from the config file (whereas present). 

## Description
Deletes a single [`--command-code`](add-command.md#--command-code) / [`--command-string`](add-command.md#--command-string) combination from the config file (whereas present). 

## Parameters
| Command            | Description                                                                                                      | [Associated parameters](/docs/configure.md#parameters)                                                   |
|--------------------|------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| `--delete-command` | Deletes a command code for a user from the configuration file                                                    | `--callsign`,`--command-code`                                             |

## Example
```
python configure.py --delete-command --callsign=DF1JSL-1 --command-code=sayhello
```
