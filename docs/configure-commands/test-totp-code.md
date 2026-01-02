# `--test-totp-code`

## Introduction

Tests a user's TOTP code against the user's secret and returns a simple "valid" / "invalid" message to the user.

> [!NOTE]
> Use this function to determine whether your combination of call sign and TOTP code is valid.

## Description

`configure.py` will try to read the user entry from the configuration file. If found, it will try to validate the given TOTP code against the user's secret. A simple "code is valid" or "code is invalid" message will get printed to the command line.

## Parameters

| Command            | Description                                                                 | [Parameters](/docs/configure.md#parameters) (mandatory) | [Parameters](/docs/configure.md#parameters) (optional) |
|--------------------|-----------------------------------------------------------------------------|---------------------------------------------------------|--------------------------------------------------------|
| `--test-totp-code` | Tests a given 6-digit TOTP code for validity against the user's TOTP secret | `--callsign`,`--totp-code`                              | n/a                                                    |


## Examples

- Configuration entries for `DF1JSL-1` and `DF1JSL` exist in the external YAML configuration file
- Configuration entries for `DF1JSL-15` do _NOT_ exist in the external YAML configuration file

Failed attempt
```
python configure.py --test-totp-code --callsign=df1jsl-1 --totp=502506 
2025-08-03 16:56:05,828 configure -INFO- Configuration file 'sabb_command_config.yaml' was successfully read
2025-08-03 16:56:05,828 configure -INFO- Unable to identify matching call sign and/or command_code in configuration file 'sabb_command_config.yaml'; exiting
```  

Successful attempt, not using the wildcard callsign's TOTP token (read: the TOTP token which belongs to `DF1JSL-1`)
```
python configure.py --test-totp-code --callsign=df1jsl-1 --totp=779856 
2025-08-03 17:13:45,797 configure -INFO- Configuration file 'sabb_command_config.yaml' was successfully read
2025-08-03 17:13:45,798 configure -INFO- Token '779856' matches with target call sign 'DF1JSL-1'
```

Successful attempt, using the wildcard TOTP token (read: the TOTP token which belongs to `DF1JSL`). Note that instead of retrieving the target callsign `DF1JSL-1`, this retrieval attempt did return the SSID-less callsign `DF1JSL`
```
python configure.py --test-totp-code --callsign=df1jsl-1 --totp=761814 
2025-08-03 17:16:39,736 configure -INFO- Configuration file 'sabb_command_config.yaml' was successfully read
2025-08-03 17:16:39,737 configure -INFO- Token '761814' matches with target call sign 'DF1JSL'
```

Successful attempt, using the wildcard TOTP token (read: the TOTP token which belongs to `DF1JSL`) for `DF1JSL-15` which has no entry in the configuration file. As we use the SSID-less TOTP token from `DF1JSL`, we are able to retrieve the configuration data.
```
python configure.py --test-totp-code --callsign=df1jsl-1 --totp=761814 
2025-08-03 17:16:39,736 configure -INFO- Configuration file 'sabb_command_config.yaml' was successfully read
2025-08-03 17:16:39,737 configure -INFO- Token '761814' matches with target call sign 'DF1JSL'
```
