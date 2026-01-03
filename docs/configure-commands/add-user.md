# `--add-user`

## Introduction

Adds or updates a user (`--callsign`) to the external YAML `--configfile`. Unlike the other commands, `--add-user` is an _interactive_ process. First, it will generate a TOTP QR code which you will scan with your mobile phone's password manager. Then, the program will ask you to verify that TOTP code by specifying the current 6-digit code.

Except for `--add-user`, all other modifications to the configuration file can be done manually (e.g. by editing the configuration file directly).

## Description

`python configure.py --add-user --callsign=DF1JSL-1`

Creates _or updates_ a configuration for a callsign with a TOTP TTL of 30 seconds. During the configuration process, the user's secret will not get displayed. If you try to create an entry which already exists in the `--configfile`, its secret setting will be updated.

- run `python configure.py --add-user --callsign=DF1JSL-1`
- use a mobile phone for scanning the QR barcode and saving it to your password manager
- If you want to abort the process, enter `QUIT`. Otherwise, enter `CONTINUE`.
- Use your phone's password manager to retrieve the current TOTP token for the secret which was just generated. Enter the secret. If the code validates, `configure.py` will write/update the configuration file with the new user data. If you don't want to do this, enter `QUIT` instead.
- If the user was already present in that config file, its secret will get updated.

> [!TIP]
> The default value for the token's validity is `30` seconds. Use the `--ttl` setting to change this setting to a value between 30..300.

## Parameters

| Command      | Description                                        | [Parameters](/docs/configure.md#parameters) (mandatory) | [Parameters](/docs/configure.md#parameters) (optional) |
|--------------|----------------------------------------------------|---------------------------------------------------------|--------------------------------------------------------|
| `--add-user` | Adds (or updates) a user to the configuration file | `--callsign`                                            | `-ttl`,`--show-secret`                                 |

## Example
```python
python configure.py --add-user --callsign=DF1JSL-1 
/Users/jsl/git/secure-aprs-bastion-bot/.venv/bin/python /Users/jsl/git/secure-aprs-bastion-bot/src/secure-aprs-bastion-bot/configure.py --add-user --callsign df1jsl-1 
2026-01-03 19:03:38,046 - configure -INFO - Creating new configuration file sabb_command_config.yml
2026-01-03 19:03:38,046 - configure -INFO - Adding new user account
2026-01-03 19:03:38,046 - configure -INFO - Generating TOTP credentials for user 'DF1JSL-1' with TTL '30'
                                                     
                                                     
    █▀▀▀▀▀█ ▀▄ ▄▀ ██▀▄ ▀▄ ██▄ ▀▀█▄▀▄█▀ ▄▀ █▀▀▀▀▀█    
    █ ███ █  ▄█▄▀▄▄█▀█▄▀▀█ █ ▀   ██ ▄  █▄ █ ███ █    
    █ ▀▀▀ █  ▀▀ ▀▄▄ ▄█ ▀█▀▀▀█▄▄▀▀▄▄ █▄▀▀▀ █ ▀▀▀ █    
    ▀▀▀▀▀▀▀ █▄▀ █▄▀ █ ▀ █ ▀ █ █ █ █▄▀▄▀ █ ▀▀▀▀▀▀▀    
    ██ ▀▀ ▀   ▀▄▄ ██▀▄▀ ██████▄ ▀█▄  ▄██▄▄█ ▄ ▄ ▀    
    ▄▄▀█▄ ▀▄█▀ █ ▀ █▀ ▄▀▄▄██ ▀▄█▀  ▄▀ ▀▄▄   ▄ ▄▀▀    
    ▄▄█▀█ ▀  █▄▄  ▀█ ▀▀██▀ ▀▀▄██  █ ▄ ▀▀ ▀ █▀▀▄▀▀    
    ▄█▄ ▀ ▀██▀▀█▄█▄ ▄▀███▀▀▄▀▄▄█ ▄█ ▀ █▀██▀█▀██▄     
     ██ ██▀▄█▀█▀▀▄▀▀▄▀ ▄▄ ▀  ▄▀▀▄▀██▀██▀▄█ ▄  ▄█▄    
    ▀▄▀▀█ ▀███▀▀▄▄█▀▀▄ ▄▄▄▀██  ▄█▀ ▄ ▀ ▄█▄▄ ▄▄█▄█    
     ▀ ██▀▀▀█▄  █▄ █▄▀▀ █▀▀▀█▀▀█▄▀▄ █▄█▄█▀▀▀█▄▄▄     
    ▄▀ ██ ▀ █▄█  ▀▄ █ ▀ █ ▀ █▀ █▀█▀ ██▄ █ ▀ █ █ █    
      ████▀██ ▄ █▄▄▀▀█ ▀███▀▀▀█▄█▄█▀▀ ▀ █▀▀▀▀ ▄▀▀    
    ▀▄ ██▀▀ █▀ ▀█▀▀▀   █▄▀▄ ▄ ▀▄ ▄▄▀▄█▄▄▀ █▄▀█▄▄     
    █ ▀█▄ ▀     ▄▀█▄█▄▀▄ █ ▄█▀█▀█▀▄▄▀██▀▄▀▀▀█ ▄█▄    
    ███▄ █▀█ ▄███▀█▄ ▄▀ ▀ ▀  ▄▄ █▄▀ ▀▄▄█  ▀▄▄██ █    
    █ █ ▀█▀▄▀█▀▄▀█▄  ▄██  ▀   █ ▀█▄  ▄█▀ █  ▄ ▄      
     ▄▄▄█ ▀▄█▀ ▀ █▀▄█   ▄██▀█  █ █  ▀▀▀▀ █▀█▄▀▄██    
    ▀  ▀▀ ▀▀█▀▀▄▄▄▀█  ▀▀█▀▀▀██ ██▀▄▄█▀▄██▀▀▀█▀ ▄▀    
    █▀▀▀▀▀█  ▀▀██ ▀▀▄▀▀▀█ ▀ █▄█▀▀▄▀▄▀ ███ ▀ █ █ ▄    
    █ ███ █ █ █▄█▀  █▀ █▀▀█▀▀▀▀▄▄█▄▀▀▄▄▄█▀▀▀▀ ▄█▀    
    █ ▀▀▀ █ ▄▀▀ █▄▄ ▀▄█▀  ▄█▀▄▄▄ █ ██  ▄███▀█▄█▄█    
    ▀▀▀▀▀▀▀ ▀▀▀▀     ▀▀  ▀▀    ▀ ▀   ▀▀ ▀▀▀▀ ▀       
                                                     
                                                     
Scan this QR code with your authenticator app. When done,
enter CONTINUE for code verification
or enter QUIT for exiting the program.

Enter CONTINUE or QUIT: CONTINUE
Enter the 6-digit TOTP code or enter QUIT to exit:093351

2026-01-03 19:04:41,373 - configure -WARNING - Configuration file 'sabb_command_config.yml' does not exist, will create a new one
2026-01-03 19:04:41,374 - configure -INFO - Configuration file 'sabb_command_config.yml' was successfully written
2026-01-03 19:04:41,374 - configure -INFO - User 'DF1JSL-1' was successfully added to config YAML file
2026-01-03 19:04:41,375 - configure -INFO - Now use --add-command and add some command codes for that user
```

## Config file 
This example shows the config file after adding the user. As you can see, there are no commands associated with this user. We'll do this in the [next step](add-command.md).

```yaml
users:
- callsign: DF1JSL-1
  commands: {}
  secret: GJYWOPM5YW22OD4REQDP75APVEGMNX4N
  ttl: 30
```
