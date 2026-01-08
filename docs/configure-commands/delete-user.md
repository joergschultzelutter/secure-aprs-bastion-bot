# `--delete-user` - deletes a user from the config file

## Table of Contents
<!--ts-->
* [Introduction](#introduction)
* [Description](#description)
* [Parameters](#parameters)
* [Example](#example)
  * [Config file before modification](#config-file-before-modification)
  * [Execute user deletion](#execute-user-deletion)
  * [Config file after modification](#config-file-after-modification)
<!--te-->


## Introduction

`--delete-user` deletes a user from the configuration file.

## Description

This command deletes a user (along with **all** of his settings, including [`--command-code`](add-command.md#--command-code) / [`--command-string`](add-command.md#--command-string) entries) from the configuration file.

## Parameters

| Command         | Description                                | [Parameters](/docs/configure.md#parameters) (mandatory) | [Parameters](/docs/configure.md#parameters) (optional) |
|-----------------|--------------------------------------------|---------------------------------------------------------|--------------------------------------------------------|
| `--delete-user` | Deletes a user from the configuration file | `--callsign`                                            | n/a                                                    |

## Example

### Config file before modification

```yaml
users:
- callsign: DF1JSL-1
  commands:
    sayhello:
      command_string: echo Hello World
      detached_launch: false
      watchdog_timespan: 0.0
  secret: GJYWOPM5YW22OD4REQDP75APVEGMNX4N
  ttl: 30
```

### Execute user deletion
``` python
python configure.py --delete-user --callsign=DF1JSL-1
2026-01-04 14:08:00,273 - configure -INFO - Deleting user account
2026-01-04 14:08:00,274 - configure -INFO - Configuration file 'sabb_command_config.yml' was successfully read
2026-01-04 14:08:00,274 - configure -INFO - Configuration file 'sabb_command_config.yml' was successfully written
2026-01-04 14:08:00,274 - configure -INFO - Have successfully deleted the user account 'DF1JSL-1'
```

### Config file after modification

```yaml
users: []
```