# `configure.py`

This program is used for the creation of the bot's user/command YAML configuration file. It supports a couple of actions such as:

- Create / Update / Delete a user entry along with its associated TOTP token
- Create / Update / Delete a user's command code / command line entries
- Test the TOTP token against the user's TOTP secret
- Retrieve and/or execute a user / command code combination

The APRS bot will use the resulting configuration file. Note that `configure.py` acts as both configuration tool and gatekeeper / validator; `secure-aprs-bastion-bot` itself assumed that the configuration file structure is valid and hardly performs any validation checks. You can apply manual changes to the configuration file - but if it breaks, you get to keep both pieces.  

## Overview

```
usage: configure.py     [-h] 
                        [--configfile SAC_CONFIG_FILE] 
                        [--add-user] [--delete-user] 
                        [--add-command] 
                        [--delete-command] 
                        [--test-totp-code] 
                        [--test-command-code] 
                        [--execute-command-code] 
                        [--show-secret] 
                        [--callsign SAC_CALLSIGN] 
                        [--totp-code SAC_TOTP_CODE] 
                        [--command-code SAC_COMMAND_CODE]
                        [--command-string SAC_COMMAND_STRING] 
                        [--launch-as-subprocess] 
                        [--ttl SAC_TTL]

options:
  -h, --help            show this help message and exit
  --configfile          SAC_CONFIG_FILE
                        Program config file name
  --add-user            Add a new call sign plus secret to the configuration file
  --delete-user         Remove a user with all data from the configuration file
  --add-command         Add a new command for an existing user to the configuration file
  --delete-command      Remove a command from a user's configuration in the configuration file
  --test-totp-code      Validates the provided TOTP code against the user's secret
  --test-command-code   Looks up the call sign / command code combination in the YAML file and returns the command line
  --execute-command-code
                        Looks up the call sign / command code combination in the YAML file and executes it
  --show-secret         Shows the user's secret during the -add-user configuration process (default: disabled)
  --callsign            SAC_CALLSIGN
                        Callsign (must follow call sign format standards)
  --totp-code           SAC_TOTP_CODE
                        6 digit TOTP code - submitted for configuration testing only
  --command-code        SAC_COMMAND_CODE
                        Command code which will be sent to the APRS bot for future execution
  --command-string      SAC_COMMAND_STRING
                        Command string that is associated with the user's command code
  --launch-as-subprocess
                        If specified: launch the command as a subprocess and do not wait for its completion
  --ttl SAC_TTL         TTL value in seconds (default: 30; range: 30-300)
```

## Parameters

| Parameter                | Description                                                                                                                                                                           | Type   | Default           |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|-------------------|
| `--configfile`           | External config file. `configure.py` will create this file if it does not exist.                                                                                                      | `str`  | `sac_config.yml`  |
| `--callsign`             | User's call sign, with or without SSID                                                                                                                                                | `str`  | `<none>`          |
| `--totp-code`            | Six-digit TOTP code                                                                                                                                                                   | `str`  | `<none>`          |
| `--command-code`         | Command code alias. This is the code that the user will send in his APRS message. Associated with `--command-string`                                                                  | `str`  | `<none>`          |
| `--command-string`       | Associated with `--command-code`. This is a representation of the actual command that is going to get executed.                                                                       | `str`  | `<none>`          |
| `--launch-as-subprocess` | When specified, the bot will NOT wait for the `--command-string`'s program execution. In addition, the APRS confirmation will be sent to the user _prior_ to the program's execution. | `bool` | `False`           |
| `--ttl`                  | TOTP TTL value in seconds (30..300)                                                                                                                                                   | `int`  | `30`              |
| `--aprs-test-arguments`  | Used in combination with either `--test-totp-code` or `--execute-totp-code`. Simulates parameter input `$1`..`$9` from an incoming APRS message. 0..9 parameters are supported        | `str`  | `[]` (empty list) |

## Commands

| Command                  | Description                                                                                                      | Associated parameter(s)                                                   |
|--------------------------|------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| `--add-user`             | Adds (or updates) a user to the configuration file                                                               | `--callsign`,`-ttl`,`--show-secret`                                       |
| `--delete-user`          | Deletes a user from the configuration file                                                                       | `--callsign`                                                              |
| `--add-command`          | Adds (or updates) a command code/command string for a user to the configuration file                             | `--callsign`,`--launch-as-subprocess`,`--command-code`,`--command-string` |
| `--delete-command`       | Deletes a command code for a user from the configuration file                                                    | `--callsign`,`--command-code`                                             |
| `--test-totp-code`       | Tests a given 6-digit TOTP code for validity against the user's TOTP secret                                      | `--callsign`,`--totp-code`                                                |
| `--test-command-code`    | Uses a `--callsign`/`--command-code` combination and returns the associated `--command-string` (whereas present) | `--callsign`,`--totp-code`, `--command-code`                              |
| `--execute-command-code` | Same as `--test-command-code`, but actually executes the associated `--command-string` setting                   | `--callsign`,`--totp-code`, `--command-code`                              |

## Usage

First, run `--add-user` and create 1...n user accounts in the configuration file. Then, run `--add-command` for each of these user accounts and create 1...n `--command-code`/`--command-string` entries (you can also use an editor for this step)

## Deep-Dive: Understand how user authorization / authentication works

A user entry in the config file can be with or without trailing SSID. Each entry has its very own secret and therefore its very own TOTP code.

User accounts with_OUT_ trailing SSID can act as a 'wildcard' entry. If a user callsign WITH trailing SSID has access to the user account's secret withOUT SSID (and therefore can generate its associated TOTP code), the user account WITH trailing SSID will be granted access to the entries associated with the callsign withOUT SSID .

Let's have a look at a scenario where we assume that the TOTP code never expires and that both call signs `DF1JSL` and `DF1JSL-1` are present
in the external YAML config file. `DF1JSL-15` will NOT have a configuration entry in that file.

- Callsign 1: `DF1JSL-1`, TOTP : `123456` (based on `DF1JSL-1`'s secret)
- Callsign 2: `DF1JSL`, TOTP : `471123` (based on `DF1JSL`'s secret)
- Callsign 3: `DF1JSL-15`. This call sign is __NOT__ present in the YAML configuration file and therefore has no TOTP secret assigned to it.

| Call sign in APRS message | TOTP in APRS message | Access possible | Config data will be taken from                      |
|---------------------------|----------------------|-----------------|-----------------------------------------------------|
| DF1JSL-1                  | 123456               | yes             | DF1JSL-1                                            |
| DF1JSL-1                  | 471123               | yes             | DF1JSL                                              |
| DF1JSL-1                  | 483574               | no              | didn't find matching secret                         |
| DF1JSL                    | 123456               | no              | SSID-less callsign cannot access callsign with SSID |
| DF1JSL                    | 471123               | yes             | DF1JSL                                              |
| DF1JSL                    | 999999               | no              | didn't find matching secret                         |
| DF1JSL-15                 | 555577               | no              | didn't find matching secret                         |
| DF1JSL-15                 | 123456               | no              | didn't find matching secret                         |
| DF1JSL-15                 | 471123               | yes             | DF1JSL                                              |

So instead of adding the very same configuration to each one of your multiple call signs WITH SSID, you _can_ add these to the SSID-less base sign's entry. For accessing these settings from your call sign WITH SSID, you will need to specify the TOTP token for the base call sign withOUT SSID. Note also that the base callsign withOUT SSID will NOT be able to access the configuration entries for those call signs WITH SSID.

As indicated, `DF1JSL-15` is NOT part of the YAML configuration file. Yet, it still can access `DF1JSL`'s config entries
because the user knows `DF1JSL`'s secret and was able to generate a valid token (`4771123`) that was based on that secret.

> [!WARNING]
> With great power comes great responsibility. If you want to be on the safe side, do not use the SSID-less callsign option but rather use a single dedicated callsign instead.

## Manual edits to the YAML configuration file

Except for the `--add-user` functionality, you are free to apply manual changes to the external YAML configuration file. The following constraints apply:

- `--callsign` information is always stored uppercase in the configuration file (e.g. `DF1JSL-1` and not `df1jsl-1`)
- `--command-code` information is always stored lowercase in the configuration file (e.g. `sayhello` and not `SayHello`, `SAYHELLO` etc).

When in doubt, use `configure.py` for abiding to these constraints.

## `--add-user` - add a user to the config file

### Introduction

Adds or updates a user (`--callsign`) to the external YAML `--configfile`. Unlike the other commands, `--add-user` is an _interactive_ process. First, it will generate a TOTP QR code which you will scan with your mobile phone's password manager. Then, the program will ask you to verify that TOTP code by specifying the current 6-digit code.

Except for `--add-user`, all other modifications to the configuration file can be done manually (e.g. by editing the configuration file directly).

> [!NOTE]
> This command will not fail if the config file does not exist. All other commands expect that the program configuration file is present.

### Description

`python configure.py --add-user --callsign=DF1JSL-1`

Creates _or updates_ a configuration for a callsign with a TOTP TTL of 30 seconds. During the configuration process, the user's secret will not get displayed. If you try to create an entry which already exists in the `--configfile`, its secret setting will be updated.

- run `python configure.py --add-user --callsign=DF1JSL-1`
- use a mobile phone for scanning the QR barcode and saving it to your password manager
- If you want to abort the process, enter `QUIT`. Otherwise, enter `CONTINUE`.
- Use your phone's password manager to retrieve the current TOTP token for the secret which was just generated. Enter the secret. If the code validates, `configure.py` will write/update the configuration file with the new user data. If you don't want to do this, enter `QUIT` instead.
- If the user was already present in that config file, its secret will get updated.

> [!TIP]
> The default value for the token's validity is `30` seconds. Use the `--ttl` setting to change this setting to a value between 30..300.

### Example
```
python configure.py --add-user --callsign=DF1JSL-1 
2025-07-27 18:52:43,446 configure -INFO- Creating new configuration file sac_config.yml
2025-07-27 18:52:43,446 configure -INFO- Adding new user account
2025-07-27 18:52:43,446 configure -INFO- Generating TOTP credentials for user 'DF1JSL-1' with TTL '30'
                                                     
                                                     
    █▀▀▀▀▀█  █▀ █▄▀█▀▄ ▀▄ ██▄▄█▀█ ▀▄▄▀ ▄▀ █▀▀▀▀▀█    
    █ ███ █ ▄█▀█▄█▄█ █▄▀ █▀█    ▀ ▄    █▄ █ ███ █    
    █ ▀▀▀ █ ▀▄   ▄█  ▄▄▀█▀▀▀█▄█▀█▀███ ▀▀▀ █ ▀▀▀ █    
    ▀▀▀▀▀▀▀ ▀▄█▄▀ █ █ ▀▄█ ▀ █▄▀ █▄▀ █▄▀ ▀ ▀▀▀▀▀▀▀    
    ██   █▀▀    ▄▀██ ▄ ▀█████▄▄  ███ ▄▄█▄▄▄ █▀▄      
     ▀  █▀▀▀█ ▀█ ▀▀███▄▀█▄▀  ▀███▄    █▀▄ ▀  █▄▀     
     █  ██▀█▄██▀▀▄██ ▀▀▄ ▀ ▀▀ ▀█  ▀ ▀ █▄   █▀▀▄██    
    ▄▄ ▀▀█▀▀█▀▄▄ ▄▄ █ █▄█▀ ▄▀█▄█▀▄▀   ▄█▀▄ █ ███     
     ▄█ ██▀▄▄▀▄▄ ▄ ▀ ▄ ▄█ ██ ▄ ▀ ███ █▀▄▄█▀▄▄█▄██    
    ▀ ▄█▄█▀ ▄██ █ ▀▀▀▄  ▄▄▀██▄▄▄█▀ ▄▄▀ ▄█▄▄ ▄▄█ ▀    
     █▄██▀▀▀█▀ ▄ █ ██▀▀▀█▀▀▀█ ▀██▀ █▄▄ ▀█▀▀▀█▄▄█     
     ▄  █ ▀ ██  ▀▀█ ▀█▀ █ ▀ █▀▀██▀█ ██  █ ▀ ███ ▄    
    ▄ ▀▄██▀█▀█  █  ▀▀█▀█▀██▀▀█▀▄█▄███ ▀██▀▀▀▀ ▄██    
    ▀▄▀█  ▀▀█ ▄▀█ ▀▀▀  ▄▄▀█ ▄▀▀▄▀▄▄▄▄▀██▀ ▀▄ █▄█     
    ▀ █▄██▀ ▄█▄█▄▀▄▄▀▀▀▄▀█▄▀█▀▄▀▀ ▀█▀██▄▄▀ ▀▀█▄██    
     ▀▀█▄█▀▄▀▀████▀▄ ▀▀▄█ ▀     ██ ██▄▄██▄█▄▄██▄▀    
    ▀▀███▄▀▄ █▀▄▀▄▄ ▀▄█▄     ▀█  ▄▄▀ ▄▄ ▄█▀ █ ▄▀     
     ▄▄▄█ ▀█▄▄ ▄ █ ▄▀█  ██▀▄█ ▀█▄  ▄▄█▀█ ▄ █ ▄▄█▄    
    ▀  ▀▀ ▀ ██ ▄▄ ██  ▀██▀▀▀█▀▄██▀▄▀▄▀▀██▀▀▀█▀  █    
    █▀▀▀▀▀█ █████▀▀▀█▀▀ █ ▀ ███▀ ▄██  ▄██ ▀ █ █▀▄    
    █ ███ █  █ ▀█▀▀ ▀▄ █▀▀▀█▀▀ ▄  █▀ ▄ ▀▀▀▀▀██▄█     
    █ ▀▀▀ █ ▄▀█ █   ▀▄██▄ ▄█▀  ▄ █ █▀  ▀▄▀▀▀█▄█ ▀    
    ▀▀▀▀▀▀▀ ▀▀▀▀ ▀  ▀▀▀▀ ▀   ▀ ▀▀▀  ▀▀    ▀▀▀▀ ▀     
                                                     
                                                     
Scan this QR code with your authenticator app. When done,
enter CONTINUE for code verification
or enter QUIT for exiting the program.

Enter CONTINUE or QUIT: CONTINUE
Enter the 6-digit TOTP code or enter QUIT to exit:494186

2025-07-27 18:53:46,982 configure -WARNING- Configuration file 'sac_config.yml' does not exist, will create a new one
2025-07-27 18:53:46,984 configure -INFO- Configuration file 'sac_config.yml' was successfully written
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

## `--add-command` - adds a command code/command string to the config file

### Introduction

Adds or updates a `--command code`/`--command string` for an existing user (`--callsign`) and writes/updates it to the config file. 

### Description

This option creates or updates the `--command-code` / `--command-string` combination.


#### `--command-code`

A `--command-code` is an alias for the `--command-string` entry. `--command-code` entries will be sent be the user via APRS messaging to the bot - which will then execute the associated `--command-string`

> [!NOTE]
> `--command-code` must not contain any space characters as spaces are used for separating the `--command-code` from additional parameters in the message; see ``--command-string`

Example:

| APRS `--command-code` ... | ... translates to `--command-string` |
|---------------------------|--------------------------------------|
| `sayhello`                | `source ./hi.sh`                     |

#### `--command-string`

The `command-string` supports up to 10 parameters which you can pass along with your APRS message. If detected, `secure-aprs-bastion-bot` will retrieve those parameters from the APRS message and replace the placeholders in the `command-string` value prior to executing it.

Supported placeholders:

- `$0` - always represents the call sign from which the APRS message originated. Example: `DF1JSL-1`
- `$1`..`$9` are free-text parameters which are passed along with the incoming APRS message

Practical example:

You have designed a `command-code` keyword `reboot` whose purpose is to reboot a specific server. Instead of hardcoding the server name, you want to pass it along as part of your APRS message. Additionally, you want to send back a message to the APRS callsign once the reboot has completed. To achieve this, you will do the following:

- create a keyword `command-code` named `reboot`. Its associated `command-string` will be responsible for rebooting the server and will accept two parameters:
    - the server name (represented by `$1`)
    - the originating callsign (represented by `$0`)

| `--command-code` | `--command-string`         |
|------------------|----------------------------|
| `reboot`         | `source ./reboot.sh $0 $1` |

The parameter placeholders defined by the user will later on be replaced by `secure-aprs-bastion-bot` with the values from the APRS message. Note that the order of the parameters is not fixed and can be freely defined by the user. For this example, we assume that the `reboot.sh` script accepts two parameters: parameter 1 is the user's call sign and parameter 2 is the name of the server that we have to reboot. All reboot logic is handled by `reboot.sh` itself.

Not that we have prepared `secure-aprs-bastion-bot`, let's send the message:

- `DF1JSL-9` transmits an APRS message to the `secure-aprs-bastion-bot`:
    - first six digits = TOTP code (`123456`)
    - followed by the actual keyword (`reboot`)
    - spaces separate additional keywords. We want to reboot a specific machine, e.g. `debmu417`
- Example APRS message: `123456reboot debmu417` results to
    - `$0` translating to value `DF1JSL-9`
    - `$1` translating to value `debmu417`
- `secure-aprs-bastion-bot` will pass along these parameters to the `reboot.sh` script and replace them in the given `--command-string` value, effectively executing `source ./reboot.sh DF1JSL-9 debmu417`. 
- `reboot.sh` is then to restart the `debmu417` server. When completed, it is supposed to send an APRS message back to `DF1JSL-9`, indicating that the reboot has completed.

### Example
```
python configure.py --add-user --callsign=DF1JSL-1 --command-code=sayhello --command-string="source ./hi.sh"
```

### Config File
```
users:
- callsign: DF1JSL-1
  commands:
    sayhello:
      command_string: source ./hi.sh
      launch_as_subprocess: false
  secret: HFV5Z3DBATOSZW24N5QZPHGGSCNRZ7EV
```

> [!NOTE]
> `--launch-as-subprocess` determines if the bot will wait for the program execution or not

- `launch-as-subprocess`==`false`: The `secure-aprs-bastion-bot` will execute the code provided via `--command-string`. After its completion, an outgoing APRS message to the sender will be generated. This is the bot's default behavior and is good for situations where a simple task is to be executed.
- `launch-as-subprocess`==`true`: First, `secure-aprs-bastion-bot` will send a confirmation message to the sender. Then, it will launch the execution of the `--command-string` code. This is useful for those cases where e.g. you want to reboot the server which hosts the `secure-aprs-bastion-bot` 

## `--delete-command` - deletes a command code/command string from the config file

### Introduction

Deletes a `--command-code` / `--command-string` combination from the config file (whereas present)

### Description

### Example
```
python configure.py --delete-command --callsign=DF1JSL-1 --command-code=sayhello
```

## `--delete-user` - deletes a user from the config file

### Introduction

`--delete-user` deletes a user from the configuration file.

### Description

This command deletes a user (along with all of his settings, including `--command-code`/`--commannd-string` entries) from the configuration file.

### Example
```
python configure.py --delete-user --callsign=DF1JSL-1
```

## `--test-totp-code` - tests a user's TOTP code against the user's secret

### Introduction

Tests a user's TOTP code against the user's secret and returns a simple "valid" / "invalid" message to the user.

### Description

`configure.py` will try to read the user entry from the configuration file. If found, it will try to validate the given TOTP code against the user's secret. A simple "code is valid" or "code is invalid" message will get printed to the command line.

### Examples

- Configuration entries for `DF1JSL-1` and `DF1JSL` exist in the external YAML configuration file
- Configuration entries for `DF1JSL-15` do _NOT_ exist in the external YAML configuration file

Failed attempt
```
python configure.py --test-command-code --callsign=df1jsl-1 --totp=502506 
2025-08-03 16:56:05,828 configure -INFO- Configuration file 'sac_config.yml' was successfully read
2025-08-03 16:56:05,828 configure -INFO- Unable to identify matching call sign and/or command_code in configuration file 'sac_config.yml'; exiting
```  

Successful attempt, not using the wildcard callsign's TOTP token (read: the TOTP token which belongs to `DF1JSL-1`)
```
python configure.py --test-totp-code --callsign=df1jsl-1 --totp=779856 
2025-08-03 17:13:45,797 configure -INFO- Configuration file 'sac_config.yml' was successfully read
2025-08-03 17:13:45,798 configure -INFO- Token '779856' matches with target call sign 'DF1JSL-1'
```

Successful attempt, using the wildcard TOTP token (read: the TOTP token which belongs to `DF1JSL`). Note that instead of retrieving the target callsign `DF1JSL-1`, this retrieval attempt did return the SSID-less callsign `DF1JSL`
```
python configure.py --test-totp-code --callsign=df1jsl-1 --totp=761814 
2025-08-03 17:16:39,736 configure -INFO- Configuration file 'sac_config.yml' was successfully read
2025-08-03 17:16:39,737 configure -INFO- Token '761814' matches with target call sign 'DF1JSL'
```

Successful attempt, using the wildcard TOTP token (read: the TOTP token which belongs to `DF1JSL`) for `DF1JSL-15` which has no entry in the configuration file. As we use the SSID-less TOTP token from `DF1JSL`, we are able to retrieve the configuration data.
```
python configure.py --test-totp-code --callsign=df1jsl-1 --totp=761814 
2025-08-03 17:16:39,736 configure -INFO- Configuration file 'sac_config.yml' was successfully read
2025-08-03 17:16:39,737 configure -INFO- Token '761814' matches with target call sign 'DF1JSL'
```

## `--test-command-code` - tests a `--callsign`/`--command-code` combination

### Introduction

### Description

### Example
`--execute-totp-code --callsign=df1jsl-1 --command-code=helloworld --totp=502506`  

## `--execute-command-code` - executes a `--callsign`/`--commannd-code` combination

### Introduction

This command uses the same code basis as `--test-command-code`. Instead of printing the `command-string` information to the console, this option actually executes the retrieved `command-string` information.

### Description
This command uses the same code basis as `--test-command-code`. Instead of printing the `command-string` information to the console, this option actually executes the retrieved `command-string` information.

### Example
`--execute-totp-code --callsign=df1jsl-1 --command-code=helloworld --totp=502506`  
