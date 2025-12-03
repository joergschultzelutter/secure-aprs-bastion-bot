# `--add-user`

#### Introduction

Adds or updates a user (`--callsign`) to the external YAML `--configfile`. Unlike the other commands, `--add-user` is an _interactive_ process. First, it will generate a TOTP QR code which you will scan with your mobile phone's password manager. Then, the program will ask you to verify that TOTP code by specifying the current 6-digit code.

Except for `--add-user`, all other modifications to the configuration file can be done manually (e.g. by editing the configuration file directly).

#### Description

`python configure.py --add-user --callsign=DF1JSL-1`

Creates _or updates_ a configuration for a callsign with a TOTP TTL of 30 seconds. During the configuration process, the user's secret will not get displayed. If you try to create an entry which already exists in the `--configfile`, its secret setting will be updated.

- run `python configure.py --add-user --callsign=DF1JSL-1`
- use a mobile phone for scanning the QR barcode and saving it to your password manager
- If you want to abort the process, enter `QUIT`. Otherwise, enter `CONTINUE`.
- Use your phone's password manager to retrieve the current TOTP token for the secret which was just generated. Enter the secret. If the code validates, `configure.py` will write/update the configuration file with the new user data. If you don't want to do this, enter `QUIT` instead.
- If the user was already present in that config file, its secret will get updated.

> [!TIP]
> The default value for the token's validity is `30` seconds. Use the `--ttl` setting to change this setting to a value between 30..300.

#### Example
```
python configure.py --add-user --callsign=DF1JSL-1 
2025-07-27 18:52:43,446 configure -INFO- Creating new configuration file sabb_command_config.yaml
2025-07-27 18:52:43,446 configure -INFO- Adding new user account
2025-07-27 18:52:43,446 configure -INFO- Generating TOTP credentials for user 'DF1JSL-1' with TTL '30'
                                                     
                                                     
    █▀▀▀▀▀█  █▀ █▄▀█▀▄ ▀▄ ██▄▄█▀█ ▀▄▄▀ ▄▀ █▀▀▀▀▀█    
    █ ███ █ ▄█▀█▄█▄█ █▄▀ █▀█    ▀ ▄    █▄ █ ███ █    
    █ ▀▀▀ █ ▀▄   ▄█  ▄▄▀█▀▀▀█▄█▀█▀███ ▀▀▀ █ ▀▀▀ █    
    ▀▀▀▀▀▀▀ ▀▄█▄▀ █ █ ▀▄█ ▀ █▄▀ █▄▀ █▄▀ ▀ ▀▀▀▀▀▀▀    
    ██   █▀▀    ▄▀██ ▄ ▀█████▄▄  ███ ▄▄█▄▄▄ █▀▄      
     ▀  █▀▀▀█ ▀█ ▀▀███▄▀█▄▀  ▀███▄    █▀▄ ▀  █▄▀     
     █  ██▀█▄██▀▀▄██ ▀▀▄ ▀ ▀▀ ▀█  ▀ ▀ █▄   █▀▀▄██    
    ▄▄ ▀▀█▀▀█▀▄▄ ▄▄ █ █▄█▀ ▄▀█▄█▀▄▀   ▄█▀▄ █ ███     
     ▄█ ██▀▄▄▀▄▄ ▄ ▀ ▄ ▄█ ██ ▄ ▀ ███ █▀▄▄█▀▄▄█▄██    
    ▀ ▄█▄█▀ ▄██ █ ▀▀▀▄  ▄▄▀██▄▄▄█▀ ▄▄▀ ▄█▄▄ ▄▄█ ▀    
     █▄██▀▀▀█▀ ▄ █ ██▀▀▀█▀▀▀█ ▀██▀ █▄▄ ▀█▀▀▀█▄▄█     
     ▄  █ ▀ ██  ▀▀█ ▀█▀ █ ▀ █▀▀██▀█ ██  █ ▀ ███ ▄    
    ▄ ▀▄██▀█▀█  █  ▀▀█▀█▀██▀▀█▀▄█▄███ ▀██▀▀▀▀ ▄██    
    ▀▄▀█  ▀▀█ ▄▀█ ▀▀▀  ▄▄▀█ ▄▀▀▄▀▄▄▄▄▀██▀ ▀▄ █▄█     
    ▀ █▄██▀ ▄█▄█▄▀▄▄▀▀▀▄▀█▄▀█▀▄▀▀ ▀█▀██▄▄▀ ▀▀█▄██    
     ▀▀█▄█▀▄▀▀████▀▄ ▀▀▄█ ▀     ██ ██▄▄██▄█▄▄██▄▀    
    ▀▀███▄▀▄ █▀▄▀▄▄ ▀▄█▄     ▀█  ▄▄▀ ▄▄ ▄█▀ █ ▄▀     
     ▄▄▄█ ▀█▄▄ ▄ █ ▄▀█  ██▀▄█ ▀█▄  ▄▄█▀█ ▄ █ ▄▄█▄    
    ▀  ▀▀ ▀ ██ ▄▄ ██  ▀██▀▀▀█▀▄██▀▄▀▄▀▀██▀▀▀█▀  █    
    █▀▀▀▀▀█ █████▀▀▀█▀▀ █ ▀ ███▀ ▄██  ▄██ ▀ █ █▀▄    
    █ ███ █  █ ▀█▀▀ ▀▄ █▀▀▀█▀▀ ▄  █▀ ▄ ▀▀▀▀▀██▄█     
    █ ▀▀▀ █ ▄▀█ █   ▀▄██▄ ▄█▀  ▄ █ █▀  ▀▄▀▀▀█▄█ ▀    
    ▀▀▀▀▀▀▀ ▀▀▀▀ ▀  ▀▀▀▀ ▀   ▀ ▀▀▀  ▀▀    ▀▀▀▀ ▀     
                                                     
                                                     
Scan this QR code with your authenticator app. When done,
enter CONTINUE for code verification
or enter QUIT for exiting the program.

Enter CONTINUE or QUIT: CONTINUE
Enter the 6-digit TOTP code or enter QUIT to exit:494186

2025-07-27 18:53:46,982 configure -WARNING- Configuration file 'sabb_command_config.yaml' does not exist, will create a new one
2025-07-27 18:53:46,984 configure -INFO- Configuration file 'sabb_command_config.yaml' was successfully written
User 'DF1JSL-1' was successfully added to config YAML file
Amend config file as per program documentation, then use the --test-totp-token option for a config test

Process finished with exit code 0
```
### Config file 
This example shows the config file after adding the user. As you can see, there are no commands associated with this user. We'll do this in the next step.

```
users:
- callsign: DF1JSL-1
  commands: {}
  secret: HFV5Z3DBATOSZW24N5QZPHGGSCNRZ7EV
```
