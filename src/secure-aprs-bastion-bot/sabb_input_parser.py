#
# Secure APRS Bastion Bot
# APRS input parser
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

from CoreAprsClient import CoreAprsClientInputParserStatus, CoreAprsClient
import sabb_shared
import re
from sabb_utils import (
    get_modification_time,
    read_config_file_from_disk,
    identify_target_callsign_and_command_string_from_memory,
)
import copy
from sabb_logger import logger


def dismantle_aprs_message(aprs_message: str):
    _success = False
    totp = None
    params = None
    command_code = None

    # Convert our APRS message string to lowercase
    aprs_message = aprs_message.lower()

    # try to determine our target pattern. Our message has to start with
    # a six-digit TOTP code, following 1..10 separate words (separator: space)
    pattern = re.compile(
        r"^"
        r"(?P<totp>\d{6})"  # six digits at start
        r"\s*"  # optional space(s) after digits
        r"(?P<params>[^\s]+(?: [^\s]+){0,9})"  # 1–10 words, separated by single spaces
        r"$"
    )

    # did we find anything?
    matches = pattern.match(aprs_message)
    if matches:
        # get the totp code
        totp = matches.group("code")
        # get the 1..10 words and convert them to a list item
        params = list(matches.group("params").strip().split())
        # remove the very first item from that list; this is our command code
        command_code = params.pop(0)
        _success = True
    return _success, totp, command_code, params


def parse_input_message(
    instance: CoreAprsClient, aprs_message: str, from_callsign: str, **kwargs
):
    """
    This is a stub for your custom APRS input parser.

    Parameters
    ==========
    instance: CoreAprsClient
        Instance of the core-aprs-client object.
    aprs_message: str
        The APRS message that the user has provided us with (1..67
        bytes in length). Parse the content and figure out what
        the user wants you to do.
    from_callsign: str
        Ham radio callsign that sent the message to us.
        Might be required by the input processor e.g. in case you
        have to determine the from_callsign's latitude/longitude.
    **kwargs: dict
        Optional keyword arguments

    Returns
    =======
    return_code: enum
        Appropriate return code value, originating from the
        CoreAprsClientInputParserStatus class
    input_parser_error_message: str
        if return_code is not PARSE_OK, this field can contain an optional
        error message (e.g. context-specific errors related to the
        keyword that was sent to the bot). If this field is empty AND
        return_code is NOT PARSE_OK, then the default error message will be returned.
    input_parser_response_object: dict | object
        Dictionary object where we store the data that is required
        by the 'output_generator' module for generating the APRS message.
        Note that you can also return other objects such as classes. Just ensure that
        both input_parser and output_generator share the very same
        structure for this variable.
    """

    # The following variable is used in conjunction with errors during parsing.
    # Assuming that e.g. your keyword is used for pulling a wx report for a certain
    # city but the user forgot to specify that additional parameter, you can use this
    # variable. By populating it, core-aprs-client will output THIS variable's content
    # to the user whenever 'success == False' applies. If that variable is empty, the
    # bot's default error message will be used instead.
    # You can easily build your own error handling mechanisms in case this function
    # does not work for you
    input_parser_error_message = ""

    # Check if the command config file has been changed and re-import it, if necessary
    config_updated_timestamp = get_modification_time(
        filename=sabb_shared.command_config_filename
    )

    # Re-read the config file from disk, if necessary
    if config_updated_timestamp != sabb_shared.config_initial_timestamp:
        __success, __data = read_config_file_from_disk(
            filename=sabb_shared.command_config_filename
        )
        if __success:
            sabb_shared.config_data = __data.deepcopy()
            sabb_shared.config_initial_timestamp = config_updated_timestamp

    # Dismantle the incoming APRS message
    success, totp_code, command_code, command_params = dismantle_aprs_message(
        aprs_message=aprs_message
    )
    if not success:
        input_parser_error_message = sabb_shared.http_msg_403
        input_parser_response_object = {}
        # set the return code
        return_code = CoreAprsClientInputParserStatus.PARSE_ERROR
        return return_code, input_parser_error_message, input_parser_response_object

    # Check if the TOTP code is already present in our expiringdict object

    # enrich the command_params list with the callsign
    # Replace the callsign. Add the call sign to the top of the list
    command_params.insert(0, from_callsign)

    # Attempt to locate the execution parameters
    success, target_callsign, command_string, detached_launch, secret = (
        identify_target_callsign_and_command_string_from_memory(
            data=sabb_shared.config_data,
            callsign=from_callsign,
            totp_code=totp_code,
            command_code=command_code,
        )
    )

    # Abort the process if we were unable to find the command OR there was a mismatch with
    # the given TOTP code. Do not disclose the origin of the error to the user
    if not success:
        # provide generic APRS response to the user
        input_parser_error_message = sabb_shared.http_msg_403
        input_parser_response_object = {}
        # set the return code
        return_code = CoreAprsClientInputParserStatus.PARSE_ERROR
        return return_code, input_parser_error_message, input_parser_response_object

    # Debug information
    logger.debug(
        msg=f"Command Code: '{command_code}', Command String: '{command_string}', detached_launch: '{detached_launch}'"
    )

    # and now start iterating through the list and replace our content
    for count, item in enumerate(command_params, start=0):
        command_string = command_string.replace(f"${count}", item)
    logger.debug(f"final command_string: '{command_string}'")

    # Check if we have received fewer user-specified parameters than expected
    # if that is the case, our string still contains placeholders
    regex_string = r"\$[0-9]"
    matches = re.search(pattern=regex_string, string=command_string)
    if matches:
        input_parser_error_message = sabb_shared.http_msg_510
        input_parser_response_object = {}
        return_code = CoreAprsClientInputParserStatus.PARSE_ERROR
        return return_code, input_parser_error_message, input_parser_response_object

    # finally, create the input parser response object
    input_parser_response_object = {
        "from_callsign": from_callsign,
        "totp_code": totp_code,
        "command_string": command_string,
        "detached_launch": detached_launch,
    }

    # set the return code
    return_code = CoreAprsClientInputParserStatus.PARSE_OK

    # Add call sign/totp code to our expiringdict object
    # or forward it to the next steps?

    return return_code, input_parser_error_message, input_parser_response_object


if __name__ == "__main__":
    pass
