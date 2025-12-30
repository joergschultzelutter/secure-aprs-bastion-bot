#
# Core APRS Client
# APRS output generator stub
# Author: Joerg Schultze-Lutter, 2025
#
# This is a stub for the module which generates the outgoing APRS message
# (based on what the user wants you to do)
#
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

# These keywords are STUBS which also assume that the data parameters (originating
# from the input_processor) are forwarded as a 'dict' object. You need to modify
# this code according to your very own use case.
#

from CoreAprsClient import CoreAprsClient
from sabb_utils import set_totp_expiringdict_key
import sabb_shared


def generate_output_message(
    instance: CoreAprsClient, input_parser_response_object: dict | object, **kwargs
):
    """
    This is a stub for your custom APRS output generator

    Parameters
    ==========
    instance: CoreAprsClient
        Instance of the core-aprs-client object.
    input_parser_response_object: dict | object
        dictionary object, containing data from input_parser.py
        Literally speaking, you will use the content from this
        dictionary in order to generate an APRS output message.
        You can (and should!) customize this dict object but ensure that
        both input_parser and output_processor use the same structure
        Note that you can also return other objects such as classes. Just ensure that
        both input_parser and output_generator share the very same
        structure for this variable.
    **kwargs: dict
        Optional keyword arguments

    Returns
    =======
    success: bool
        True if everything is fine, False otherwise.
        Unlike for the input processor, there are no edge cases that we need to take
        care of (e.g. ignoring incoming messages). Therefore, a simple true/false
        return code will suffice.
    output_message: str
        The output message that we want to return to the user.
    postprocessor_input_object: object | None
        'None' if no post-processor is supposed to be triggered
        Otherwise, use this parameter for transporting data structures
        to your custom post-processor code. Note that in order to get
        triggered, a) the post-processor code function needs to be supplied
        to the instantiated class object AND b) postprocessor_input_object
        must not be 'None'
    """

    # If the user has requested a detached launch, simply return http202 response
    # message and pass the input parser response object along to the framework
    if input_parser_response_object["detached_launch"]:
        success = True
        output_message = sabb_shared.http_msg_202
        return success, output_message, input_parser_response_object

    # Everything else from here is NOT a detached launch, meaning that we have to
    # execute the user's command string and ultimately, add callsign/token to our
    # expiring dict, thus preventing the framework from re-using it again.
    instance.log_info(
        msg=f"Executing command: '{input_parser_response_object["command_string"]}'"
    )
    success = True
    output_message = sabb_shared.http_msg_200

    # Finally, add the target callsign and the TOTP token to our expiring cache
    set_totp_expiringdict_key(
        callsign=input_parser_response_object["target_callsign"],
        totp_code=input_parser_response_object["totp_code"],
    )

    # and return the status to the framework
    return success, output_message, None


if __name__ == "__main__":
    pass
