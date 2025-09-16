#!/opt/local/bin/python
#
# secure-aprs-bastion-bot: Configuration file generator
# Author: Joerg Schultze-Lutter, 2025
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Shorten and abbreviate the original input text which - unfortunately - is
# usually provided by the BBK site in epic proportions. We try to shorten the
# text as much as possible, thus rendering the output text to a format that is
# more compatible with e.g. SMS devices.
#
import sys

import pyotp
import qrcode
import os.path
import argparse
import logging
import yaml
import re
import time
import platform
import subprocess
import threading


if platform.system() == "Windows":
    import msvcrt
else:
    import select
    import termios
    import tty

# Default name of the to-be-generated output configuration file
CONFIG_FILE_NAME = "sabb_command_config.yaml"

# Set up the global logger variable
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(module)s -%(levelname)s- %(message)s"
)
logger = logging.getLogger(__name__)


def ttl_check(ttl_value):
    """
    Helper function for checking TTL

    Parameters
    ==========
    ttl_value: str
        our TTL value we want to check

    Returns
    =======
    success: bool
        True / False, depending on whether or not the entry was valid
    """

    try:
        ttl_value = int(ttl_value)
    except ValueError:
        logger.error("TTL option needs a numeric value")
        sys.exit(0)
    if ttl_value < 30:
        raise argparse.ArgumentTypeError("Minimum TTL value is 30 (seconds)")
    if ttl_value > 300:
        raise argparse.ArgumentTypeError("Maximum TTL value is 300 (seconds)")
    return ttl_value


def totp_check(totp_value):
    """
    Helper function for checking TTL

    Parameters
    ==========
    totp_value: str
        our TOTP code that we want to check

    Returns
    =======
    success: bool
        True / False, depending on whether or not the entry was valid
    """
    if len(totp_value) != 6:
        raise argparse.ArgumentTypeError("Invalid TOTP - needs to have 6 digits")

    if not totp_value.isdigit():
        raise argparse.ArgumentTypeError("Invalid TOTP - needs to be numeric value")
    return totp_value


def get_command_line_params_config():
    """
    Gets the command line parameters from the command line

    Parameters
    ==========

    Returns
    =======
    tons of command line parameters
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--configfile",
        default=CONFIG_FILE_NAME,
        dest="config_file",
        type=str,
        help="Program config file name (default: sabb_command_config.yaml) ",
    )

    parser.add_argument(
        "--add-user",
        dest="add_user",
        action="store_true",
        default=False,
        help="Add a new call sign plus secret to the configuration file",
    )

    parser.add_argument(
        "--delete-user",
        dest="del_user",
        action="store_true",
        default=False,
        help="Remove a user with all data from the configuration file",
    )

    parser.add_argument(
        "--add-command",
        dest="add_command",
        action="store_true",
        default=False,
        help="Add a new command for an existing user to the configuration file",
    )

    parser.add_argument(
        "--delete-command",
        dest="del_command",
        action="store_true",
        default=False,
        help="Remove a command from a user's configuration in the configuration file",
    )

    parser.add_argument(
        "--test-totp-code",
        dest="test_totp_code",
        action="store_true",
        default=False,
        help="Validates the provided TOTP code against the user's secret",
    )

    parser.add_argument(
        "--test-command-code",
        dest="test_command_code",
        action="store_true",
        default=False,
        help="Looks up the call sign / command code combination in the YAML file and returns the command line",
    )

    parser.add_argument(
        "--execute-command-code",
        dest="execute_command_code",
        action="store_true",
        default=False,
        help="Looks up the call sign / command code combination in the YAML file and executes it",
    )

    parser.add_argument(
        "--show-secret",
        dest="show_secret",
        action="store_true",
        default=False,
        help="Shows the user's secret during the -add-user configuration process (default: disabled)",
    )

    parser.add_argument(
        "--callsign",
        dest="callsign",
        type=str,
        default="",
        help="Callsign (must follow call sign format standards)",
    )

    parser.add_argument(
        "--totp-code",
        dest="totp_code",
        type=str,
        default="",
        help="6 digit TOTP code - submitted for configuration testing only",
    )

    parser.add_argument(
        "--command-code",
        dest="command_code",
        type=str,
        default="",
        help="Command code which will be sent to the APRS bot for future execution",
    )

    parser.add_argument(
        "--command-string",
        dest="command_string",
        type=str,
        default="",
        help="Command string that is associated with the user's command code",
    )

    parser.add_argument(
        "--launch-as-subprocess",
        dest="launch_as_subprocess",
        action="store_true",
        default=False,
        help="If specified: launch the command as a subprocess and do not wait for its completion",
    )

    parser.add_argument(
        "--ttl",
        dest="ttl",
        type=ttl_check,
        default=30,
        help="TTL value in seconds (default: 30; range: 30-300)",
    )

    parser.add_argument(
        "--aprs-test-arguments",
        nargs="*",
        dest="aprs_test_arguments",
        type=str,
        help="For testing purposes only; list of 0 to 9 APRS arguments, Used in conjunction with --test-command-code/--execute-command-code",
    )

    args = parser.parse_args()

    __configfile = args.config_file
    __add_user = args.add_user
    __add_command = args.add_command
    __del_user = args.del_user
    __del_command = args.del_command
    # Call sign is always in upper case characters
    __callsign = args.callsign.upper()
    __ttl = args.ttl
    __totp_code = args.totp_code
    # command_code is always in lower case characters
    __command_code = args.command_code.lower()
    __command_string = args.command_string
    __launch_as_subprocess = args.launch_as_subprocess
    __test_totp_code = args.test_totp_code
    __test_command_code = args.test_command_code
    __execute_command_code = args.execute_command_code
    __show_secret = args.show_secret if add_user else False
    __aprs_test_arguments = args.aprs_test_arguments or []

    # Run some basic plausibility checks

    if len(__aprs_test_arguments) > 9:
        logger.error(msg="Too many APRS arguments for testing purposes (0..9)")
        sys.exit(0)

    if len(__callsign) > 0:
        # Check whether we have a call sign with or without SSID
        regex_string = r"\b^([A-Z0-9]{1,3}[0-9][A-Z0-9]{0,3})(-[A-Z0-9]{1,2})?$\b"
        matches = re.search(pattern=regex_string, string=__callsign)
        if not matches:
            logger.error(msg="Call sign must match a valid call sign format")
            sys.exit(0)

    if (
        __add_user
        or __del_user
        or __add_command
        or __del_command
        or __test_totp_code
        or __test_command_code
        or __execute_command_code
    ):
        if len(__callsign) < 1:
            logger.error(msg="Call sign is required")
            sys.exit(0)

    if __test_command_code or __execute_command_code:
        if (
            __add_command
            or __del_command
            or __add_user
            or __del_user
            or __test_totp_code
        ):
            logger.error(msg="Testing not possible with this combination")
            sys.exit(0)
        if len(__callsign) < 1:
            logger.error(msg="Command code is required")
            sys.exit(0)
        if len(__totp_code) < 1:
            logger.error(msg="TOTP code is required")
            sys.exit(0)

    if __add_command or __del_command:
        if len(__command_code) < 1:
            logger.error(msg="Command code is required")
            sys.exit(0)

    if __test_totp_code:
        if __add_user or __del_user or __add_command or __del_command:
            logger.error(
                msg="--test-config and add/del commands cannot be run at the same time"
            )
            sys.exit(0)
        if len(__totp_code) < 1:
            logger.error(msg="TOTP code is required")
            sys.exit(0)
        if __execute_command_code:
            logger.error(
                msg="--test-command-code and --execute-command-code cannot be run at the same time"
            )
            sys.exit(0)

    if __execute_command_code:
        if __add_user or __del_user or __add_command or __del_command:
            logger.error(
                msg="--execute-config and add/del commands cannot be run at the same time"
            )
            sys.exit(0)
        if len(__totp_code) < 1:
            logger.error("TOTP code is required")
            sys.exit(0)
        if __test_command_code:
            logger.error(
                msg="--test-command-code and --execute-command-code cannot be run at the same time"
            )
            sys.exit(0)

    if (
        not __test_totp_code
        and not __test_command_code
        and not __execute_command_code
        and not __add_command
        and not __del_command
        and not __add_user
        and not __del_user
    ):
        logger.error(msg="No command parameters specified; nothing to do")
        sys.exit(0)

    if len(__command_code) > 1:
        if " " in __command_code:
            logger.error(msg="Invalid command code; must not contain spaces")
            sys.exit(0)

    return (
        __configfile,
        __add_user,
        __add_command,
        __del_user,
        __del_command,
        __callsign,
        __ttl,
        __totp_code,
        __command_code,
        __command_string,
        __test_totp_code,
        __show_secret,
        __launch_as_subprocess,
        __test_command_code,
        __execute_command_code,
        __aprs_test_arguments,
    )


def signal_term_handler(signal_number, frame):
    """
    Signal handler for SIGTERM signals. Ensures that the program
    gets terminated in a safe way, thus allowing all databases etc
    to be written to disc.

    Parameters
    ==========
    signal_number:
                    The signal number
    frame:
                    Signal frame

    Returns
    =======
    """

    logger.info(msg="Received SIGTERM; forcing clean program exit")
    sys.exit(0)


def does_file_exist(file_name: str):
    """
    Checks if the given file exists. Returns True/False.

    Parameters
    ==========
    file_name: str
                    our file name
    Returns
    =======
    status: bool
        True /False
    """
    return os.path.isfile(file_name)


def verify_totp_code(secret: str, totp_code: str):
    """
    Verifies a given TOTP code against the given secret.

    Parameters
    ==========
    secret: str
        user's TOTP secret
    totp_code: str
        user's TOTP code

    Returns
    =======
    status: bool
        True / False, depending on whether or not the code matches
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(otp=totp_code)


def add_user_to_yaml_config(configfile: str, callsign: str, secret: str):
    """
    Writes a new user to the config file.

    Parameters
    ==========
    configfile: str
        Name of the external YAML config file
    callsign: str
        User's callsign
    secret: str
        user's TOTP secret

    Returns
    =======
    success: bool
        True / False, depending on whether or not the entry was created/updated
    """

    # Read the file from disk
    __success, data = read_config_file_from_disk(filename=configfile)

    if not __success:
        logger.debug(
            msg=f"Invalid file structure encountered in '{configfile}'; aborting"
        )
        return False

    data_updated = False
    __success = False

    # iterate through the existing list and apply updates
    # in case the user already exists
    for user in data["users"]:
        if user["callsign"] == callsign:
            user["secret"] = secret
            data_updated = True
            break

    # We were upable to update the user as it didn't exist
    # So let's create a new entry instead
    if not data_updated:
        data["users"].append({"callsign": callsign, "secret": secret, "commands": {}})

    # Write the config file back to disk
    __success = write_config_file_to_disk(filename=configfile, data=data)

    return __success


def get_user_secret(configfile: str, callsign: str):
    """
    Gets a user secret from the config file.

    Parameters
    ==========
    configfile: str
        Name of the external YAML config file
    callsign: str
        User's callsign

    Returns
    =======
    success: bool
        True / False, depending on whether or not the data was retrieved
    secret: str
        user's TOTP secret
    """

    secret = None

    __success, data = read_config_file_from_disk(filename=configfile)
    if not __success:
        return __success

    __success = False

    # Get the secret for the user (if present)
    # Our search can only result in a single match; the secret can
    # only be associated with a SSID-less callsign _or_ a callsign with SSID
    for __item in data["users"]:
        if "callsign" in __item and __item["callsign"] == callsign:
            if "secret" in __item:
                secret = __item["secret"]
                __success = True
                break

    return __success, secret


def get_user_command_string(configfile: str, callsign: str, command_code: str):
    """
    Gets the command string for a user/command_line combination from the config file.

    Parameters
    ==========
    configfile: str
        Name of the external YAML config file
    callsign: str
        User's callsign
    command_code: str
        The command code that we intend to retrieve

    Returns
    =======
    success: bool
        True / False, depending on whether or not the data was retrieved
    command_string: str
        command string for the user/command_line combination
    launch_as_subprocess: bool
        launch_as_subprocess flag for the user/command_line combination
    """

    __command_string = ""
    __launch_as_subprocess = False

    __success, data = read_config_file_from_disk(filename=configfile)
    if not __success:
        return __success

    __success = False

    # Get the secret for the user (if present)
    for __item in data["users"]:
        if "callsign" in __item and __item["callsign"] == callsign:
            # we have found our call sign. Now start
            # looking for the command code
            for command in __item["commands"]:
                if command == command_code:
                    try:
                        # We have found our entry. Retrieve all values
                        __command_string = item["commands"][command]["command_string"]
                        __launch_as_subprocess = item["commands"][command][
                            "launch_as_subprocess"
                        ]
                        __success = True
                    except KeyError:
                        pass
                    break
        if __success:
            break
    return (
        __success,
        __command_string,
        __launch_as_subprocess,
    )


def del_user_from_yaml_config(configfile: str, callsign: str):
    """
    Deletes a user (plus sub entries) from the config file.

    Parameters
    ==========
    configfile: str
        Name of the external YAML config file
    callsign: str
        User's callsign

    Returns
    =======
    success: bool
        True / False, depending on whether or not the entry was deleted
    """
    __success, data = read_config_file_from_disk(filename=configfile)
    if not __success:
        return __success

    data["users"] = [user for user in data["users"] if user["callsign"] != callsign]

    # Write the config file back to disk
    __success = write_config_file_to_disk(filename=configfile, data=data)
    return __success


def read_config_file_from_disk(filename: str):
    """
    Reads a YAML config file and returns its contents.

    Parameters
    ==========
    filename: str
        Name of the external YAML config file

    Returns
    =======
    success: bool
        True / False, depending on whether the file was read
    data: dict
        Dictionary containing the contents of the file
    """
    __success = False
    data = {"users": []}

    if not does_file_exist(file_name=filename):
        logger.warning(
            f"Configuration file '{filename}' does not exist, will create a new one"
        )
        # We simply return the pre-defined dictionary
        # so let's consider this a success
        __success = True
    else:
        try:
            with open(file=filename, mode="r") as yaml_file:
                data = yaml.safe_load(yaml_file)
                logger.info(f"Configuration file '{filename}' was successfully read")

                # perform a very basic check of the file structure
                # as the file exists, it has to have a valid data structure
                # otherwise, we will trigger an error
                if "users" not in data:
                    logger.warning(f"Invalid data structure in '{filename}'")
                else:
                    __success = True
        except:
            logger.warning(f"Cannot read config file '{filename}'")
    return __success, data


def write_config_file_to_disk(filename: str, data: dict):
    """
    Writes the configuration to the YAML config file

    Parameters
    ==========
    filename: str
        Name of the external YAML config file
    data: dict
        Dictionary containing the future contents of the file

    Returns
    =======
    success: bool
        True / False, depending on whether the file was written
    """
    __success = False
    assert type(data) is dict

    # Write the config file back to disk
    try:
        with open(file=filename, mode="w") as yaml_file:
            yaml.dump(data, yaml_file, default_flow_style=False, allow_unicode=True)
        __success = True
        logger.info(f"Configuration file '{filename}' was successfully written")
    except Exception as ex:
        logger.debug(f"Exception occurred: {ex.__traceback__}")
        print(f"Cannot write config file '{filename}' to disk")
        __success = False
    return __success


def add_cmd_to_yaml_config(
    configfile: str,
    callsign: str,
    command_code: str,
    command_string: str,
    launch_as_subprocess=False,
):
    """
    Writes a new command for an existing user to the config file.

    Parameters
    ==========
    configfile: str
        Name of the external YAML config file
    callsign: str
        User's callsign
    command_code: str
        The command code for our new command
    command_string: str
        The command string for our new command
    launch_as_subprocess: bool
        Wait or do not wait for the command_string execution

    Returns
    =======
    success: bool
        True / False, depending on whether or not the entry was created/updated
    """

    # Read the file from disk
    __success, data = read_config_file_from_disk(filename=configfile)

    if not __success:
        return __success

    __success = False
    found_data = False

    # Iterate through the list of call sign
    for user in data["users"]:
        if user["callsign"] == callsign:
            # We have found our our user
            # now let's create/update our command entry
            user.setdefault("commands", {})[command_code] = {
                "command_string": command_string,
                "launch_as_subprocess": launch_as_subprocess,
            }
            found_data = True
            break

    # Check if we were able to locate our call sign
    if not found_data:
        logger.warning(
            f"Call sign '{callsign}' doesn't exist in config file '{configfile}', aborting ..."
        )
    else:
        # Write the config file back to disk
        __success = write_config_file_to_disk(filename=configfile, data=data)

    return __success


def del_cmd_from_yaml_config(configfile: str, callsign: str, command_code: str):
    """
    Deletes a command for an existing user from the config file.

    Parameters
    ==========
    configfile: str
        Name of the external YAML config file
    callsign: str
        User's callsign
    command_code: str
        The command code for our new command

    Returns
    =======
    success: bool
        True / False, depending on whether or not the entry was created/updated
    """

    # Read the file from disk
    __success, data = read_config_file_from_disk(filename=configfile)

    if not __success:
        return __success

    found_data = False
    __success = False

    for user in data["users"]:
        if user["callsign"] == callsign:
            user.get("commands", {}).pop(command_code, None)
            found_data = True
            break

    if not found_data:
        logger.warning(
            f"Call sign '{callsign}' doesn't exist in config file '{configfile}', aborting ..."
        )
    else:
        # Write the config file back to disk
        __success = write_config_file_to_disk(filename=configfile, data=data)

    return __success


def identify_target_callsign_and_command_string(
    configfile: str, callsign: str, totp_code: str, command_code: str | None
):
    """
    Retrieves the callsign/totp_code match and identifies the command_string for the given command_code.

    A user entry in the config file can be with or without trailing SSID. Each entry has its very own secret and therefore its very own TOTP code.

    User accounts with_OUT_ trailing SSID can act as a 'wildcard' entry. If a user callsign WITH trailing SSID has access to the user account's secret withOUT SSID (and therefore can generate its associated TOTP code), the user account WITH trailing SSID will be granted access to the entries associated with the callsign withOUT SSID .

    Let's have a look at a scenario where we assume that the TOTP code never expires and that both call signs `DF1JSL` and `DF1JSL-1` are present
    in the external YAML config file. `DF1JSL-15` will NOT have a configuration entry in that file.

    - Callsign 1: `DF1JSL-1`, TOTP : `123456` (based on `DF1JSL-1`'s secret)
    - Callsign 2: `DF1JSL`, TOTP : `471123` (based on `DF1JSL`'s secret)
    - Callsign 3: `DF1JSL-15`. This call sign is __NOT__ present in the YAML configuration file and therefore does not even has a TOTP secret assigned to it.

    | Call sign in APRS message | TOTP in APRS message | Access possible | Config data will be taken from     |
    |---------------------------|----------------------|-----------------|------------------------------------|
    | DF1JSL-1                  | 123456               | yes             | DF1JSL-1                           |
    | DF1JSL-1                  | 471123               | yes             | DF1JSL                             |
    | DF1JSL-1                  | 483574               | no              | didn't find matching secret        |
    | DF1JSL                    | 123456               | no              | SSID-less CS cannot access SSID-CS |
    | DF1JSL                    | 471123               | yes             | DF1JSL                             |
    | DF1JSL                    | 999999               | no              | didn't find matching secret        |
    | DF1JSL-15                 | 555577               | no              | didn't find matching secret        |
    | DF1JSL-15                 | 123456               | no              | didn't find matching secret        |
    | DF1JSL-15                 | 471123               | yes             | DF1JSL                             |

    So instead of adding the very same configuration to each one of your multiple call signs WITH SSID, you _can_ add these to the SSID-less base sign's entry. For accessing these settings from your call sign WITH SSID, you will need to specify the TOTP token for the base call sign withOUT SSID. Note also that the base callsign withOUT SSID will NOT be able to access the configuration entries for those call signs WITH SSID.

    As indicated, `DF1JSL-15` is NOT part of the YAML configuration file. Yet, it still can access `DF1JSL`'s config entries
    because the user knows `DF1JSL`'s secret and was able to generate a valid token (`4771123`) that was based on that secret.

    > [!WARNING]
    > With great power comes great responsibility. If you want to limit access to specific callsigns, do not use the SSID-less callsign option but rather use a single dedicated callsign instead.

    Once the matching call sign has been identified, this function then tries to identify the command_code/command_string combination

    Parameters
    ==========
    configfile: str
        Name of the external YAML configuration file
    callsign: str
        Callsign code of the user
    totp_code: str
        user's TOTP code
    command_code: str
        Command code for which we intend to retrieve the command string
        If missing (None or empty string), only the TOTP validation will be performed

    Returns
    =======
    success: bool
        True if a matching callsign was found, False otherwise
    callsign: str
        Callsign code of the user (or None if no matching callsign was found)
    command_string: str
        Command string for the callsign/command_code combination (or None if no matching callsign was found)
        Always None if no command_code was provided
    launch_as_subprocess: bool
        True if the program is to be launched as a subprocess, False otherwise
        Always False if no command_code was provided
    secret: str
        Secret associated with this callsign
    """

    # Read the file from disk
    __success, data = read_config_file_from_disk(filename=configfile)

    if not __success:
        return False, None, None, None

    __success = False
    __target_callsign = None
    __command_string = None
    __secret = None
    __launch_as_subprocess = False

    # Determine if we are only supposed to check the TOTP code and skip the command_code validation
    perform_full_check = (
        True if type(command_code) is str and len(command_code) > 0 else False
    )

    # build the SSID-less call sign
    callsign_truncated = callsign.split("-")[0]

    # and now iterate through the config file
    for __item in data["users"]:
        if "callsign" in __item and __item["callsign"] in (
            callsign,
            callsign_truncated,
        ):
            # We have found a match, let's retrieve the secret
            if "secret" in __item:
                __secret = __item["secret"]
                # Validate the given TOTP code against that secret
                if verify_totp_code(secret=__item["secret"], totp_code=totp_code):
                    # We found a match for the callsign (note that the input callsign
                    # and our new one may differ for those cases our target callsign
                    # is ssid-less!
                    __target_callsign = __item["callsign"]
                    # We might be required to skip the next step for those cases
                    # where
                    if perform_full_check:
                        # now let's iterate through the target callsign's list of command
                        # codes and try to determine what command string we are supposed
                        # to execute
                        for command in __item["commands"]:
                            if command == command_code:
                                # We found a match!
                                try:
                                    __command_string = __item["commands"][command][
                                        "command_string"
                                    ]
                                    __launch_as_subprocess = __item["commands"][
                                        command
                                    ]["launch_as_subprocess"]
                                    __success = True
                                except KeyError:
                                    __command_string = __launch_as_subprocess = None
                                break
                    # no full check requested; return ok but set command_string and
                    # launch_as_subprocess to None as we don't retrieve this data
                    else:
                        __success = True
                        __command_string = __launch_as_subprocess = None
                    break
    return (
        __success,
        __target_callsign,
        __command_string,
        __launch_as_subprocess,
        __secret,
    )


def add_user(configfile: str, callsign: str, ttl: int, show_secret: bool):
    """
    Adds a user to the config file.

    Parameters
    ==========
    configfile: str
        Name of the external YAML config file
    callsign: str
        User's callsign
    ttl: int
        desired time-to-live time span for the user callsign's secret
    show_secret: bool
        whether or not to show the secret or not (debug purposes only)

    Returns
    =======
    success: bool
        True / False, depending on whether or not the entry was created/updated
    """
    __success = False

    # Do not fail if the config file does not exist
    if not does_file_exist(configfile):
        logger.info(f"Creating new configuration file {configfile}")
    logger.info("Adding new user account")

    logger.info(f"Generating TOTP credentials for user '{callsign}' with TTL '{ttl}'")

    # generate the TOTP secret
    secret = pyotp.random_base32()

    # generate the TOTP object
    totp = pyotp.TOTP(secret, interval=ttl)

    # Provision the URI for the QR code
    uri = totp.provisioning_uri(
        name="https://github.com/joergschultzelutter",
        issuer_name="secure-aprs-bastion-bot",
    )

    # generate the qr code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=2,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)

    # and print the qr code to the command line
    qr.print_ascii(tty=False)  # `tty=False` for better display quality

    # show the secret if the user has asked for it
    if show_secret:
        print(f"User's TOTP secret: {secret}\n")

    # here comes the interactive part
    print("Scan this QR code with your authenticator app. When done,")
    print("enter CONTINUE for code verification")
    print("or enter QUIT for exiting the program.\n")
    content = ""

    # Wait for the user to enter CONTINUE or QUIT
    while content not in ["CONTINUE", "QUIT"]:
        content = input("Enter CONTINUE or QUIT: ")
        if content == "QUIT":
            logger.debug(f"{add_user.__name__}: aborting")
            return __success

    # User has entered CONTINUE. Validate secret against TOTP code from user
    content = ""
    while content not in ["QUIT"] or len(content) != 6 and not content.isdigit():
        content = input("Enter the 6-digit TOTP code or enter QUIT to exit:")
        if content == "QUIT":
            logger.debug(f"{add_user.__name__}: aborting")
            __success = False
            return __success
        else:
            if not verify_totp_code(secret=secret, totp_code=content):
                print("This TOTP code is invalid")
                content = ""
                continue
            else:
                # write to YAML file
                __success = add_user_to_yaml_config(
                    configfile=configfile, callsign=callsign, secret=secret
                )
                print("")
                if __success:
                    logger.info(
                        msg=f"User '{callsign}' was successfully added to config YAML file"
                    )
                    logger.info(
                        msg="Now use --add-command and add some command codes for that user"
                    )
                else:
                    logger.info(
                        msg=f"Unable to write entry for '{callsign}' to config YAML file"
                    )
                break
    return __success


def del_user(configfile: str, callsign: str):
    """
    Deletes a user from the config file.

    Parameters
    ==========
    configfile: str
        Name of the external YAML config file
    callsign: str
        User's callsign

    Returns
    =======
    success: bool
        True / False, depending on whether or not the entry was created/updated
    """
    __success = False
    if not does_file_exist(configfile):
        logger.info(f"Configuration file '{configfile}' does not exist; nothing to do")
    else:
        logger.info("Deleting user account")
        __success = del_user_from_yaml_config(
            configfile=configfile,
            callsign=callsign,
        )
        if success:
            logger.info(f"Have successfully deleted the user account '{callsign}'")
        else:
            logger.info(
                f"Unable to delete the user account '{callsign}' - e.g. user account does not exist"
            )
    return __success


def add_cmd(
    configfile: str,
    callsign: str,
    command_code: str,
    command_string: str,
    launch_as_subprocess: bool,
):
    """
    Adds a command-code/command-string entry for a user to the config file.

    Parameters
    ==========
    configfile: str
        Name of the external YAML config file
    callsign: str
        User's callsign
    command_code: str
        APRS command code
    command_string: str
        the actual code that we are going to execute
    launch_as_subprocess: bool
        Determines whether or not to launch as a subprocess

    Returns
    =======
    success: bool
        True / False, depending on whether or not the entry was created/updated
    """
    __success = False
    if not does_file_exist(configfile):
        logger.info(f"Configuration file '{configfile}' does not exist; nothing to do")
    else:
        logger.info(
            f"Adding new command-code '{command_code}' config for user '{callsign}'"
        )
        __success = add_cmd_to_yaml_config(
            configfile=configfile,
            callsign=callsign,
            command_code=command_code,
            command_string=command_string,
            launch_as_subprocess=launch_as_subprocess,
        )
        if __success:
            logger.info(
                f"Command '{command_code}' for user '{callsign}' added to config file"
            )
    return __success


def del_cmd(configfile: str, callsign: str, command_code: str):
    """
    Deletes a command-code/command-string entry for a user from the config file.

    Parameters
    ==========
    configfile: str
        Name of the external YAML config file
    callsign: str
        User's callsign
    command_code: str
        APRS command code

    Returns
    =======
    success: bool
        True / False, depending on whether or not the entry was created/updated
    """

    __success = False
    if not does_file_exist(configfile):
        logger.info(f"Configuration file '{configfile}' does not exist; nothing to do")
    else:
        logger.info(f"Deleting command '{command_code}' for user '{callsign}'")
        __success = del_cmd_from_yaml_config(
            configfile=configfile,
            callsign=callsign,
            command_code=command_code,
        )
        if __success:
            logger.info(
                f"Command '{command_code}' for user '{callsign}' removed from config file"
            )
        else:
            logger.info(
                "Unable to delete the command name - e.g. command name does not exist or other error occurred"
            )
    return __success


def execute_program(command: str | list, wait_for_completion: bool = True):
    """
    Executes an external program

    Parameters
    ==========
    command: str or list
        Single command or a command with arguments.
    wait_for_completion: bool
        True  = Wait until external program completes its execution (default).
        False = Start external program as background job
                after 20 seconds delay and return immediately.

    Returns
    =======
        int   if wait_for_completion == True: program's return code
        None  if wait_for_completion == False or in case of error
    """
    def _start_process(cmd):
        try:
            if platform.system() == "Windows":
                subprocess.Popen(cmd, shell=True)
            else:
                if isinstance(cmd, str):
                    subprocess.Popen(cmd.split())
                elif isinstance(cmd, list):
                    subprocess.Popen(cmd)
                else:
                    raise ValueError("Command must be of type 'str' or 'list'")
        except Exception as e:
            logger.debug(f"Error while starting process: {e}")

    try:
        if wait_for_completion:
            process = _start_process(command)
            if process is not None:
                return process.wait()
            return None
        else:
            timer = threading.Timer(20.0, _start_process, args=(command,))
            timer.daemon = True
            timer.start()
            return None
    except Exception as e:
        logger.debug(f"General error has occurred: {e}")
        return None


def wait_or_keypress(timeout_seconds: float) -> bool:
    """
    Waits a defined number of seconds until key press is pressed or until timeout is reached.

    Parameters
    ==========
    timeout_seconds: float
        our timeout in seconds

    Returns
    =======
    key_pressed: bool
        True if the keypress was pressed, False otherwise
    """
    key_pressed = threading.Event()

    # Detect our environment
    system = platform.system()
    has_tty = sys.stdin.isatty()
    if not has_tty:
        logger.warning(
            msg="IDE/Piped-mode detected; you need to press any key *AND* confirm this setting with Enter"
        )

    def key_listener():
        if not has_tty:
            try:
                _ = input()  # Enter required for IDE/Piped-mode input
                key_pressed.set()
            except:
                pass
            return

        if system == "Windows":
            import msvcrt

            while not key_pressed.is_set():
                if msvcrt.kbhit():
                    msvcrt.getch()  # buffer read
                    key_pressed.set()
                time.sleep(0.01)
        else:
            import select
            import termios
            import tty

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)  # unfilterd entry
                while not key_pressed.is_set():
                    dr, _, _ = select.select([sys.stdin], [], [], 0.01)
                    if dr:
                        sys.stdin.read(1)  # buffer read
                        key_pressed.set()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    listener_thread = threading.Thread(target=key_listener, daemon=True)
    listener_thread.start()

    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        if key_pressed.is_set():
            return True
        time.sleep(0.01)

    return key_pressed.is_set()


if __name__ == "__main__":
    (
        sabb_configfile,
        sabb_add_user,
        sabb_add_command,
        sabb_del_user,
        sabb_del_command,
        sabb_callsign,
        sabb_ttl,
        sabb_totp_code,
        sabb_command_code,
        sabb_command_string,
        sabb_test_totp_code,
        sabb_show_secret,
        sabb_launch_as_subprocess,
        sabb_test_command_code,
        sabb_execute_command_code,
        sabb_aprs_test_arguments,
    ) = get_command_line_params_config()

    if sabb_add_user:
        add_user(
            configfile=sabb_configfile,
            callsign=sabb_callsign,
            ttl=sabb_ttl,
            show_secret=sabb_show_secret,
        )
        sys.exit(0)

    if sabb_del_user:
        del_user(configfile=sabb_configfile, callsign=sabb_callsign)
        sys.exit(0)

    if sabb_add_command:
        add_cmd(
            configfile=sabb_configfile,
            callsign=sabb_callsign,
            command_code=sabb_command_code,
            command_string=sabb_command_string,
            launch_as_subprocess=sabb_launch_as_subprocess,
        )
        sys.exit(0)

    if sabb_del_command:
        del_cmd(
            configfile=sabb_configfile,
            callsign=sabb_callsign,
            command_code=sabb_command_code,
        )
        sys.exit(0)

    if sabb_test_totp_code:
        if not does_file_exist(sabb_configfile):
            logger.info(f"Given configuration file '{sabb_configfile}' does not exist.")
            logger.info(
                "Please run this program with option --add-user for an initial config file setup."
            )
        else:
            (
                success,
                target_callsign,
                command_string,
                launch_as_subprocess,
                secret,
            ) = identify_target_callsign_and_command_string(
                configfile=sabb_configfile,
                callsign=sabb_callsign,
                totp_code=sabb_totp_code,
                command_code=None,
            )
            if not success:
                logger.info(
                    f"Unable to identify matching call sign and/or totp/secret match in '{sabb_configfile}'; exiting"
                )
            else:
                logger.info(
                    msg=f"Token '{sabb_totp_code}' matches with target call sign '{target_callsign}'"
                )
        sys.exit(0)

    if sabb_test_command_code or sabb_execute_command_code:
        if not does_file_exist(sabb_configfile):
            logger.info(f"Given configuration file '{sabb_configfile}' does not exist.")
            logger.info(
                "Please run this program with option --add-user for an initial config file setup."
            )
        else:
            (
                success,
                target_callsign,
                command_string,
                launch_as_subprocess,
            ) = identify_target_callsign_and_command_string(
                configfile=sabb_configfile,
                callsign=sabb_callsign,
                totp_code=sabb_totp_code,
                command_code=sabb_command_code,
            )
            if not success:
                logger.info(
                    f"Unable to identify matching call sign and/or command_code in configuration file '{sabb_configfile}'; exiting"
                )
            else:
                logger.info(
                    msg=f"Command '{sabb_command_code}' translates to target call sign '{target_callsign}' and command_string '{command_string}'"
                )
                logger.info(
                    msg="Replacing potential APRS parameters in the command string."
                )

                # Replace the callsign. Add the call sign to the top of the list
                sabb_aprs_test_arguments.insert(0, sabb_callsign)

                # and now start iterating through the list and replace our content
                for count, item in enumerate(sabb_aprs_test_arguments, start=0):
                    command_string = command_string.replace(f"${count}", item)
                logger.info(f"final command_string: '{command_string}'")

                if sabb_execute_command_code:
                    pass
        sys.exit(0)
