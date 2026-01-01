#!/opt/local/bin/python
#
# secure-aprs-bastion-bot: utility functions
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
from sabb_logger import logger
import sabb_shared
import yaml
from datetime import datetime, timezone

import os
import shlex
import signal
import subprocess
import time
from typing import Optional, List
import pyotp
import psutil


def get_modification_time(filename: str):
    timestamp = None
    if os.path.isfile(filename):
        timestamp = os.path.getmtime(filename)
    return timestamp


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
        logger.error(f"Configuration file '{filename}' does not exist")
        # We simply return the pre-defined dictionary
        # so let's consider this a success
        __success = False
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


def get_totp_expiringdict_key(callsign: str, totp_code: str):
    """
    Checks for an entry in our TOTP expiring dictionary cache.
    If we find that entry in our list before that entry has expired,
    we consider the request as a duplicate and will not process it again

    Parameters
    ==========
    callsign: str
        User's callsign, e.g. DF1JSL-1
    totp_code: str
        six-digit numeric TOTP code

    Returns
    =======
    key: 'Tuple'
        Key tuple consisting of 'callsign' and 'totp_code' or
        value 'None' if we were unable to locate the entry
    """
    key = (callsign, totp_code)
    key = tuple(key)
    key = key if key in sabb_shared.totp_message_cache else None
    return key


def set_totp_expiringdict_key(callsign: str, totp_code: str):
    """
    Adds an entry to our TOTP expiring dictionary cache.

    Parameters
    ==========
    callsign: str
        User's callsign, e.g. DF1JSL-1
    totp_code: str
        six-digit numeric TOTP code

    Returns
    =======
    totp_message_cache: Expiringdict
        The updated version of our ExpiringDict object
    """

    key = (callsign, totp_code)
    key = tuple(key)
    sabb_shared.totp_message_cache[key] = datetime.now(timezone.utc)


def execute_program(
    command: str, detached_launch: bool = False, watchdog_timespan: float = 0.0
) -> Optional[int]:
    """
    Runs an external program / Script

    Parameters:
    ===========
    command: str
        The command to be executed. Additional parameters are separated by spaces.
    detached_launch: bool
        sets the launch mode
        'False' = Starts the program and waits until it has finished running.
        'True' = Starts the program as a detached process
    watchdog_timespan: float
        Optional watchdog parameter in seconds. Is only taken into consideration for
        'detached_launch=False' cases.
        0.0 = Disable watchdog and wait until the program has finished running.
        Any other positive value: (try to) terminate the program after x seconds

    Returns
    =======
    - Optional[int]:
        process PID or 'None' in case of an error
    """

    def out(msg: str) -> None:
        try:
            logger.debug(msg)
        except Exception:
            pass

    # Check our input
    try:
        if not isinstance(command, str) or not command.strip():
            out("execute_program: ERROR: invalid command (empty or non-string).")
            return None
        if not isinstance(detached_launch, bool):
            out("execute_program: ERROR: invalid detached_launch (must be bool).")
            return None
        try:
            watchdog = float(watchdog_timespan)
        except Exception:
            out(
                "execute_program: ERROR: invalid watchdog_timespan (must be float-compatible)."
            )
            return None
        if watchdog < 0.0:
            out("execute_program: ERROR: invalid watchdog_timespan (must be >= 0.0).")
            return None
    except Exception as e:
        out(f"execute_program: ERROR: unexpected validation failure: {e}")
        return None

    # parse our command
    try:
        argv = shlex.split(command, posix=(os.name != "nt"))
        if not argv:
            out("execute_program: ERROR: command parsing produced empty argv.")
            return None
    except Exception as e:
        out(f"execute_program: ERROR: failed to parse command: {e}")
        return None

    out(f"execute_program: INFO: starting command: {command}")

    def terminate_process_tree(pid: int) -> None:
        """
        Best-effort Termination:
        1) SIGTERM/terminate() process tree (children + root)
        2) wait_procs
        3) kill() on remaining items
        """
        try:
            root = psutil.Process(pid)
        except Exception as e:
            out(f"execute_program: ERROR: psutil cannot attach to PID={pid}: {e}")
            return

        try:
            children: List[psutil.Process] = root.children(recursive=True)
        except Exception as e:
            out(f"execute_program: ERROR: cannot enumerate children of PID={pid}: {e}")
            children = []

        procs = children + [root]

        # Graceful terminate
        for p in procs:
            try:
                if os.name == "nt":
                    p.terminate()
                else:
                    p.send_signal(signal.SIGTERM)
            except Exception as e:
                out(
                    f"execute_program: ERROR: terminate failed for PID={getattr(p, 'pid', '?')}: {e}"
                )

        try:
            _, alive = psutil.wait_procs(procs, timeout=3.0)
        except Exception as e:
            out(f"execute_program: ERROR: wait_procs error: {e}")
            alive = procs

        # Hard kill remaining
        if alive:
            for p in alive:
                try:
                    p.kill()
                except Exception as e:
                    out(
                        f"execute_program: ERROR: kill failed for PID={getattr(p, 'pid', '?')}: {e}"
                    )
            try:
                psutil.wait_procs(alive, timeout=3.0)
            except Exception as e:
                out(f"execute_program: ERROR: wait after kill error: {e}")

    # launch process
    try:
        if detached_launch:
            # Detached: new process group and detached I/O
            try:
                if os.name == "nt":
                    creationflags = (
                        subprocess.CREATE_NEW_PROCESS_GROUP
                        | subprocess.DETACHED_PROCESS
                    )
                    proc = subprocess.Popen(
                        argv,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        close_fds=True,
                        creationflags=creationflags,
                    )
                else:
                    proc = subprocess.Popen(
                        argv,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        close_fds=True,
                        start_new_session=True,
                    )
                pid = proc.pid
                out(f"execute_program: INFO: detached process started with PID={pid}")
                return pid
            except FileNotFoundError:
                out(f"execute_program: ERROR: command not found: {command}")
                return None
            except PermissionError:
                out(f"execute_program: ERROR: permission denied: {command}")
                return None
            except Exception as e:
                out(
                    f"execute_program: ERROR: failed to start detached command '{command}': {e}"
                )
                return None

        # Non-detached: with output capture and optional watchdog
        try:
            proc = subprocess.Popen(
                argv,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
        except FileNotFoundError:
            out(f"execute_program: ERROR: command not found: {command}")
            return None
        except PermissionError:
            out(f"execute_program: ERROR: permission denied: {command}")
            return None
        except Exception as e:
            out(f"execute_program: ERROR: failed to start command '{command}': {e}")
            return None

        pid = proc.pid
        out(f"execute_program: INFO: process started with PID={pid}")

        # Watchdog
        try:
            if watchdog == 0.0:
                try:
                    stdout_data, stderr_data = proc.communicate()
                except Exception as e:
                    out(f"execute_program: ERROR: communicate failed (PID={pid}): {e}")
                    stdout_data, stderr_data = "", ""

                try:
                    rc = proc.returncode
                except Exception:
                    rc = None

                if stdout_data:
                    out(
                        f"execute_program: INFO: stdout (PID={pid}):\n{stdout_data.rstrip()}"
                    )
                if stderr_data:
                    out(
                        f"execute_program: WARN: stderr (PID={pid}):\n{stderr_data.rstrip()}"
                    )
                out(f"execute_program: INFO: process finished (PID={pid}, rc={rc})")
                return pid

            deadline = time.time() + watchdog
            while True:
                try:
                    if proc.poll() is not None:
                        break
                except Exception as e:
                    out(f"execute_program: ERROR: poll failed (PID={pid}): {e}")
                    break

                if time.time() >= deadline:
                    out(
                        f"execute_program: WARN: watchdog timeout reached (PID={pid}, {watchdog:.3f}s). Terminating."
                    )
                    terminate_process_tree(pid)
                    break

                time.sleep(0.1)

            # get remaining output (best-effort approach)
            stdout_data, stderr_data = "", ""
            try:
                stdout_data, stderr_data = proc.communicate(timeout=1.0)
            except Exception:
                pass

            try:
                rc = proc.returncode
            except Exception:
                rc = None

            """
            if stdout_data:
                out(
                    f"execute_program: INFO: stdout (PID={pid}):\n{stdout_data.rstrip()}"
                )
            if stderr_data:
                out(
                    f"execute_program: WARN: stderr (PID={pid}):\n{stderr_data.rstrip()}"
                )
            """
            out(f"execute_program: INFO: process ended (PID={pid}, rc={rc})")
            return pid

        except Exception as e:
            out(
                f"execute_program: ERROR: runtime error while waiting/terminating (PID={pid}): {e}"
            )
            return pid

    except Exception as e:
        out(f"execute_program: ERROR: unexpected failure: {e}")
        return None


def identify_target_callsign_and_command_string(
    data: dict, callsign: str, totp_code: str, command_code: str | None
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
    data: dict
        Content from the external YAML file
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
    detached_launch: bool
        True if the program is to be launched as a detached subprocess, False otherwise
        Always False if no command_code was provided
    secret: str
        Secret associated with this callsign
    watchdog_timespan: float
        Watchdog timespan in seconds (0.0 = disable). Only applicable to 'detached_launch'='False' settings
    """

    __success = False
    __target_callsign = None
    __command_string = None
    __secret = None
    __detached_launch = False
    __watchdog_timespan = 0.0

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
                _ttl = __item["ttl"]
                # Validate the given TOTP code against that secret
                if verify_totp_code(
                    totp_secret=__item["secret"], totp_code=totp_code, ttl_interval=_ttl
                ):
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
                                    __detached_launch = __item["commands"][command][
                                        "detached_launch"
                                    ]
                                    __watchdog_timespan = __item["commands"][command][
                                        "watchdog_timespan"
                                    ]
                                    __success = True
                                except KeyError:
                                    __command_string = __detached_launch = None
                                break
                    # no full check requested; return ok but set command_string and
                    # detached_launch to None as we don't retrieve this data
                    else:
                        __success = True
                        __command_string = __detached_launch = None
                    break
    return (
        __success,
        __target_callsign,
        __command_string,
        __detached_launch,
        __secret,
        __watchdog_timespan,
    )


def verify_totp_code(totp_secret: str, totp_code: str, ttl_interval: int):
    """
    Verifies a given TOTP code against the given secret.

    Parameters
    ==========
    totp_secret: str
        user's TOTP secret
    totp_code: str
        user's TOTP code
    ttl_interval: int
        TOTP's TTL interval

    Returns
    =======
    status: bool
        True / False, depending on whether the code matches
    """
    totp = pyotp.TOTP(totp_secret, interval=ttl_interval)
    return totp.verify(otp=totp_code)


if __name__ == "__main__":
    pass
