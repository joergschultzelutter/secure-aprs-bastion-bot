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
from sabb_post_processor import post_processing

import argparse
import os
import sys
import logging
import sabb_shared

from sabb_logger import logger
from sabb_expdict import create_totp_expiringdict
from sabb_utils import get_modification_time, read_config_file_from_disk


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

    logger.debug(msg="Starting APRS bastion bot")

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
        post_processor=post_processing,
    )

    # Create the expiring dictionary object for the TOTP records
    sabb_shared.totp_message_cache = create_totp_expiringdict(
        max_len=client.config_data["secure_aprs_bastion_bot"][
            "sabb_totp_cache_max_len"
        ],
        max_age_seconds=client.config_data["secure_aprs_bastion_bot"][
            "sabb_totp_cache_max_age_seconds"
        ],
    )

    # Save the command config filename - we may need to re-read the file
    # in case its content has changed during runtime
    sabb_shared.command_config_filename = client.config_data["secure_aprs_bastion_bot"][
        "sabb_command_config"
    ]

    # Verify if the Command Config file exists
    if not os.path.isfile(sabb_shared.command_config_filename):
        logger.error(
            msg=f"Command Config file '{sabb_shared.command_config_filename}' does not exist; exiting"
        )
        sys.exit(0)

    # Read the config file from disk
    success, sabb_shared.config_data = read_config_file_from_disk(
        filename=sabb_shared.command_config_filename
    )
    if not success:
        logger.error(
            msg=f"Unable to read command config file '{sabb_shared.command_config_filename}'; exiting"
        )
        sys.exit(0)

    # remember the file's initial config file timestamp
    sabb_shared.config_initial_timestamp = get_modification_time(
        filename=sabb_shared.command_config_filename
    )

    # Finally, activate the APRS client and connect to APRS-IS
    client.activate_client()
