# `--delete-command` - deletes a command code/command string from the config file

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

Deletes a single [`--command-code`](add-command.md#--command-code) / [`--command-string`](add-command.md#--command-string) combination from the config file (whereas present). 

## Description
Deletes a single [`--command-code`](add-command.md#--command-code) / [`--command-string`](add-command.md#--command-string) combination from the config file (whereas present). 

## Parameters
| Command            | Description                                                   | [Parameters](/docs/configure.md#parameters) (mandatory) | [Parameters](/docs/configure.md#parameters) (optional) |
|--------------------|---------------------------------------------------------------|---------------------------------------------------------|--------------------------------------------------------|
| `--delete-command` | Deletes a command code for a user from the configuration file | `--callsign`,`--command-code`                           | n/a                                                    |

## Example

### Config file before modification

```yaml
users:
- callsign: DF1JSL-1
  commands:
    greetuser:
      command_string: echo Hello $0
      detached_launch: false
      watchdog_timespan: 0.0
    sayhello:
      command_string: echo Hello World
      detached_launch: false
      watchdog_timespan: 0.0
  secret: GJYWOPM5YW22OD4REQDP75APVEGMNX4N
  ttl: 30
```

### Execute command deletion
```python
python configure.py --delete-command --callsign=DF1JSL-1 --command-code=sayhello
2026-01-04 14:05:53,078 - configure -INFO - Deleting command 'greetuser' for user 'DF1JSL-1'
2026-01-04 14:05:53,080 - configure -INFO - Configuration file 'sabb_command_config.yml' was successfully read
2026-01-04 14:05:53,081 - configure -INFO - Configuration file 'sabb_command_config.yml' was successfully written
2026-01-04 14:05:53,081 - configure -INFO - Command 'greetuser' for user 'DF1JSL-1' removed from config file```
```

### Config file after modification

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