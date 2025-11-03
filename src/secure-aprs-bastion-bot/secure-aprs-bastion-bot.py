#
# Secure APRS Bastion Bot
# Author: Joerg Schultze-Lutter, 2025
#
# This demo client imports the input parser and output processor
# functions and establishes a live connection to APRS-IS
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
from CoreAprsClient import CoreAprsClient

# Your custom input parser and output generator code
from sabb_input_parser import parse_input_message
from sabb_output_generator import generate_output_message

import argparse
import os
import sys
import logging
from datetime import datetime
import timezone

from sabb_logger import logger
from sabb_shared import totp_message_cache
from sabb_expdict import create_totp_expiringdict


def get_command_line_params():
    """
    Gets and returns the command line arguments

    Parameters
    ==========

    Returns
    =======
    cfg: str
        name of the configuration file
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--configfile",
        default="secure_aprs_bastion_bot.cfg",
        type=argparse.FileType("r"),
        help="APRS framework config file name (default is 'secure_aprs_bastion_bot.cfg')",
    )

    args = parser.parse_args()
    cfg = args.configfile.name

    if not os.path.isfile(cfg):
        print("Config file does not exist; exiting")
        sys.exit(0)

    return cfg


if __name__ == "__main__":

    # Get the configuration file name
    configfile = get_command_line_params()

    # Create the CoreAprsClient object. Supply the
    # following parameters:
    #
    # - configuration file name
    # - log level (from Python's 'logging' package)
    # - function names for both input processor and output generator
    #
    client = CoreAprsClient(
        config_file=configfile,
        log_level=logging.DEBUG,
        input_parser=parse_input_message,
        output_generator=generate_output_message,
    )

    # Create the expiring dictionary object for the TOTP records
    totp_message_cache = create_expiring_dict(
        max_len=client.config_data["secure_aprs_bastion_bot"][
            "sabb_totp_cache_max_len"
        ],
        max_age_seconds=client.config_data["secure_aprs_bastion_bot"][
            "sabb_totp_cache_max_age_seconds"
        ],
    )

    # Activate the APRS client and connect to APRS-IS
    client.activate_client()


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
    key = tuple(callsign, totp_code)
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
    sabb_shared.totp_message_cache[tuple(callsign, totp_code)] = datetime.now(
        timezone.utc
    )
    return sabb_shared.totp_message_cache
