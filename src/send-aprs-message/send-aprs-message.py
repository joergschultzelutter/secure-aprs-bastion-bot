#!/opt/local/bin/python
#
# send-aprs-message.py
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
import logging
import aprslib
import argparse
from unidecode import unidecode
import re
import time
import sys


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(module)s -%(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# change these settings if necessary
aprsis_server_name = "euro.aprs2.net"
aprsis_server_port = 14580

# Default APRS message lengths
# 67 = standard APRS message
# 59 = APRS message with numeric message ID
APRS_MSG_LEN_NOTRAILING = 67
APRS_MSG_LEN_TRAILING = 59

# Our APRS message length
APRS_MSG_LEN = APRS_MSG_LEN_NOTRAILING


def get_command_line_params():
    """
    Gets and returns the command line arguments

    Parameters
    ==========

    Returns
    =======
    configfile: str
        name of the configuration file
    """

    # Yes, quick and dirty this time - and I couldn't care less
    global APRS_MSG_LEN

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--from-callsign",
        dest="aprs_from_callsign",
        type=str,
        default="",
        help="APRS FROM callsign (sender)",
    )

    parser.add_argument(
        "--passcode",
        dest="aprs_passcode",
        type=str,
        default="",
        help="APRS passcode for the FROM callsign (sender)",
    )

    parser.add_argument(
        "--to-callsign",
        dest="aprs_to_callsign",
        type=str,
        default="",
        help="APRS TO callsign (receipient)",
    )

    parser.add_argument(
        "--aprs-message",
        dest="aprs_message",
        type=str,
        default="",
        help="APRS message",
    )

    parser.add_argument(
        "--numeric-message-pagination",
        dest="aprs_message_pagination",
        action="store_true",
        default=False,
        help="Add message enumeration to each outgoing APRS message",
    )

    parser.add_argument(
        "--simulate-send",
        dest="aprs_simulate_send",
        action="store_true",
        default=False,
        help="Simulate sending of data to APRS-IS (output will be made to the console)",
    )

    args = parser.parse_args()

    aprsis_from_callsign = args.aprs_from_callsign.upper()
    aprsis_to_callsign = args.aprs_to_callsign.upper()
    aprsis_passcode = args.aprs_passcode
    aprsis_message = args.aprs_message
    aprsis_message_pagination = args.aprs_message_pagination
    aprsis_simulate_send = args.aprs_simulate_send

    # change our global variable in case of active numeric pagination
    APRS_MSG_LEN = (
        APRS_MSG_LEN_TRAILING if aprsis_message_pagination else APRS_MSG_LEN_NOTRAILING
    )

    if len(aprsis_from_callsign) > 0:
        # Check whether we have a call sign with or without SSID
        regex_string = r"\b^([A-Z0-9]{1,3}[0-9][A-Z0-9]{0,3})(-[A-Z0-9]{1,2})?$\b"
        matches = re.search(pattern=regex_string, string=aprsis_from_callsign)
        if not matches:
            logger.error(msg="Call sign must match a valid call sign format")
            sys.exit(0)
    else:
        logger.error(msg="No FROM call sign provided")
        sys.exit(0)

    if len(aprsis_to_callsign) > 0:
        # Check whether we have a call sign with or without SSID
        regex_string = r"\b^([A-Z0-9]{1,3}[0-9][A-Z0-9]{0,3})(-[A-Z0-9]{1,2})?$\b"
        matches = re.search(pattern=regex_string, string=aprsis_to_callsign)
        if not matches:
            logger.error(msg="Call sign must match a valid call sign format")
            sys.exit(0)
    else:
        logger.error(msg="No FROM call sign provided")
        sys.exit(0)

    if len(aprsis_passcode) != 5:
        logger.error(msg="APRS passcode must be 5 characters long")
        sys.exit(0)
    else:
        if not aprsis_passcode.isdigit():
            logger.error("APRS passcode must be a 5 digit string")
            sys.exit(0)
        else:
            try:
                aprsis_passcode_int = int(aprsis_passcode)
            except ValueError:
                logger.error(msg="APRS passcode must be a 5 digit string")
                sys.exit(0)
            if aprslib.passcode(aprsis_from_callsign) != aprsis_passcode_int:
                logger.error(msg="APRS passcode is incorrect")
                sys.exit(0)

    if len(aprsis_message) < 1:
        logger.error(msg="APRS message is empty")
        sys.exit(0)

    return (
        aprsis_from_callsign,
        aprsis_passcode,
        aprsis_message,
        aprsis_to_callsign,
        aprsis_simulate_send,
    )


def make_pretty_aprs_messages(
    message_to_add: str,
    max_len: int,
    destination_list: list = None,
    separator_char: str = " ",
    add_sep: bool = True,
    force_outgoing_unicode_messages: bool = False,
) -> list:
    """
    Pretty Printer for APRS messages. As APRS messages are likely to be split
    up (due to the 67 chars message len limitation), this function prevents
    'hard cuts'. Any information that is to be injected into message
    destination list is going to be checked wrt its length. If
    len(current content) + len(message_to_add) exceeds the max_len value,
    the content will not be added to the current list string but to a new
    string in the list.

    Example:

    current APRS message = 1111111111222222222233333333333444444444455555555556666666666

    Add String "Hello World !!!!" (16 chars)

    Add the string the 'conventional' way:

    Message changes to
    Line 1 = 1111111111222222222233333333333444444444455555555556666666666Hello W
    Line 2 = orld !!!!

    This function however returns:
    Line 1 = 1111111111222222222233333333333444444444455555555556666666666
    Line 2 = Hello World !!!!

    In case the to-be-added text exceeds 67 characters due to whatever reason,
    this function first tries to split up the content based on space characters
    in the text and insert the resulting elements word by word, thus preventing
    the program from ripping the content apart. However, if the content consists
    of one or multiple strings which _do_ exceed the maximum text len, then there
    is nothing that we can do. In this case, we will split up the text into 1..n
    chunks of text and add it to the list element.

    Known issues: if the separator_char is different from its default setting
    (space), the second element that is inserted into the list may have an
    additional separator char in the text

    Parameters
    ==========
    message_to_add: str
        message string that is to be added to the list in a pretty way
        If string is longer than 67 chars, we will truncate the information
    destination_list: list
        List with string elements which will be enriched with the
        'mesage_to_add' string. Default: empty list aka user wants new list
    max_len: int:
        Max length of the list's string len.
        The length is dependent on whether the user has activated trailing
        message number information in the outgoing message or not.
        When activated, the message length is 59 - otherwise, it is 67.
    separator_char: str
        Separator that is going to be used for dividing the single
        elements that the user is going to add
    add_sep: bool
        True = we will add the separator when more than one item
               is in our string. This is the default
        False = do not add the separator (e.g. if we add the
                very first line of text, then we don't want a
                comma straight after the location
    force_outgoing_unicode_messages: bool
        False = all outgoing UTF-8 content will be down-converted
                to ASCII content
        True = all outgoing UTF-8 content will sent out 'as is'

    Returns
    =======
    destination_list: list
        List array, containing 1..n human readable strings with
        the "message_to_add' input data
    """
    # Dummy handler in case the list is completely empty
    # or a reference to a list item has not been specified at all
    # In this case, create an empty list
    if not destination_list:
        destination_list = []

    # replace non-permitted APRS characters from the
    # message text as APRS-IS might choke on this content
    # Details: see APRS specification chapter 15 taken from
    # https://github.com/wb2osz/aprsspec
    # "Messages, Bulletins and Announcements"
    message_to_add = re.sub("[{}|~]+", "", message_to_add)

    # Convert the message to plain ascii
    # Unidecode does not take care of German special characters
    # Therefore, we need to 'translate' them first
    message_to_add = convert_text_to_plain_ascii(message_string=message_to_add)

    # If new message is longer than max len then split it up with
    # max chunks of max_len bytes and add it to the array.
    # This should never happen but better safe than sorry.
    # Keep in mind that we only transport plain text anyway.
    if len(message_to_add) > max_len:
        split_data = message_to_add.split()
        for split in split_data:
            # if string is short enough then add it by calling ourself
            # with the smaller text chunk
            if len(split) < max_len:
                destination_list = make_pretty_aprs_messages(
                    message_to_add=split,
                    destination_list=destination_list,
                    max_len=max_len,
                    separator_char=separator_char,
                    add_sep=add_sep,
                    force_outgoing_unicode_messages=force_outgoing_unicode_messages,
                )
            else:
                # string exceeds max len; split it up and add it as is
                string_list = split_string_to_string_list(
                    message_string=split, max_len=max_len
                )
                for msg in string_list:
                    destination_list.append(msg)
    else:  # try to insert
        # Get very last element from list
        if len(destination_list) > 0:
            string_from_list = destination_list[-1]

            # element + new string > max len? no: add to existing string, else create new element in list
            if len(string_from_list) + len(message_to_add) + 1 <= max_len:
                delimiter = ""
                if len(string_from_list) > 0 and add_sep:
                    delimiter = separator_char
                string_from_list = string_from_list + delimiter + message_to_add
                destination_list[-1] = string_from_list
            else:
                destination_list.append(message_to_add)
        else:
            destination_list.append(message_to_add)

    return destination_list


def split_string_to_string_list(message_string: str, max_len: int):
    """
    Force-split the string into chunks of max_len size and return a list of
    strings. This function is going to be called if the string that the user
    wants to insert exceeds more than e.g. 67 characters. In this unlikely
    case, we may not be able to add the string in a pretty format - but
    we will split it up for the user and ensure that none of the data is lost

    Parameters
    ==========
    message_string: str
        message string that is to be divided into 1..n strings of 'max_len"
        text length
    max_len: int:
        Default: 67; set to 59 in case of pagination

    Returns
    =======
    split_strings: list
        List array, containing 1..n strings with a max len of 'max_len'
    """
    split_strings = [
        message_string[index : index + max_len]
        for index in range(0, len(message_string), max_len)
    ]
    return split_strings


def convert_text_to_plain_ascii(message_string: str):
    """
    Converts a string to plain ASCII
    Parameters
    ==========
    message_string: str
        Text that needs to be converted
    Returns
    =======
    hex-converted text to the user
    """
    message_string = (
        message_string.replace("Ä", "Ae")
        .replace("Ö", "Oe")
        .replace("Ü", "Ue")
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )
    message_string = unidecode(message_string)
    return message_string


def send_aprs_message_list(
    myaprsis: aprslib.inet.IS | None,
    message_text_array: list,
    destination_call_sign: str,
    source_call_sign: str,
    simulate_send: bool = True,
    packet_delay: float = 10.0,
    packet_delay_last_message: float = 1.0,
    tocall: str = "APMPAD",
):
    """
    Send a pre-prepared message list to to APRS_IS
    All packages have a max len of 67 characters
    If 'simulate_send'= True, we still prepare the message but only send it to our log file
    Parameters
    ==========
    myaprsis: aprslib.inet.IS
        Our aprslib object that we will use for the communication part
    message_text_array: list
        Contains 1..n entries of the content that we want to send to the user
    destination_call_sign: str
        Target user call sign that is going to receive the message (usually, this
        is the user's call sign who has sent us the initial message)
    simulate_send: bool
        If True: Prepare string but only send it to logger
    source_call_sign: str
        Our very own call sign
    packet_delay: float
        Delay after sending out our APRS acknowledgment request
        Used when there are still remaining messages
    packet_delay_last_message: float
        Delay after sending out our APRS acknowledgment request
        Used when there are no remaining messages
    tocall: str
        This bot uses the default TOCALL ("APMPAD")

    Returns
    =======
    """

    # Send the message list
    for index, single_message in enumerate(message_text_array, start=1):
        # Build our output string
        stringtosend = (
            f"{source_call_sign}>{tocall}::{destination_call_sign:9}:{single_message}"
        )
        # Check if we want to send the data for real or just perform an output to console
        if not simulate_send:
            logger.debug(msg=f"Sending APRS message '{stringtosend}'")
            myaprsis.sendall(stringtosend)
        else:
            logger.debug(msg=f"Simulating APRS message '{stringtosend}'")
        # In case of remaining messages, apply the user sleep period
        # otherwise, let's wait just one sec
        if index < len(message_text_array):
            time.sleep(packet_delay)
        else:
            time.sleep(packet_delay_last_message)


def finalize_pretty_aprs_messages(mylistarray: list, max_len: int) -> list:
    """
    Helper method which finalizes the prettified APRS messages
    and triggers the addition of the trailing message numbers (if
    activated by the user).

    Parameters
    ==========
    mylistarray: list
        List of APRS messages
    max_len: int
        maximum length of the message

    Returns
    =======
    listitem: list
        Either formatted list (if more than one list entry was present) or
        the original list item
    """
    if max_len == APRS_MSG_LEN_TRAILING:
        return format_list_with_enumeration(mylistarray=mylistarray)
    else:
        return mylistarray


def format_list_with_enumeration(mylistarray: list) -> list:
    """
    Adds a trailing enumeration to the list if the user has activated this configuration in
    the client's config file

    Parameters
    ==========

    Returns
    =======
    listitem: list
        Either formatted list (if more than one list entry was present) or
        the original list item
    """

    max_total_length = APRS_MSG_LEN_NOTRAILING
    annotation_length = APRS_MSG_LEN_NOTRAILING - APRS_MSG_LEN_TRAILING
    max_content_length = max_total_length - annotation_length

    # check if we have more than 99 entries. We always truncate the list (just to be
    # on the safe side) but whenever more than 99 entries were detected, we also supply
    # the user with a warning message and notify him about the truncation
    if len(mylistarray) > 99:
        logger.warning(
            msg="User has supplied list with more than 99 elements; truncating"
        )
        trimmed_listarray = mylistarray[:98]
        trimmed_listarray.append("[message truncated]")
    else:
        trimmed_listarray = mylistarray
    total = len(trimmed_listarray)

    # now let's add the enumeration to the list - but only if we have
    # more than one list item in our outgoing list
    if len(trimmed_listarray) > 1:
        formatted_list = []
        for i, s in enumerate(trimmed_listarray, start=1):
            annotation = f" ({i:02d}/{total:02d})"
            truncated = s[:max_content_length]
            padded = truncated.ljust(max_content_length)
            final = padded + annotation
            formatted_list.append(final)

        return formatted_list
    else:
        # return the original list to the user
        return trimmed_listarray


if __name__ == "__main__":
    (
        aprs_from_callsign,
        aprs_passcode,
        aprs_message,
        aprs_to_callsign,
        aprs_simulate_send,
    ) = get_command_line_params()

    # prepare the outgoing APRS message list
    output_message = make_pretty_aprs_messages(
        message_to_add=aprs_message, max_len=APRS_MSG_LEN
    )

    # finalize the list whereas needed (e.g. in case the user has
    # requested numeric pagination)
    output_message = finalize_pretty_aprs_messages(
        mylistarray=output_message, max_len=APRS_MSG_LEN
    )

    # simulate server connection; dump our messages to stdout
    # and exit afterwards
    if aprs_simulate_send:
        send_aprs_message_list(
            myaprsis=None,
            message_text_array=output_message,
            destination_call_sign=aprs_to_callsign,
            simulate_send=True,
            source_call_sign=aprs_from_callsign,
        )
    else:
        # Establish the connection to APRS-IS
        AIS = aprslib.IS(aprs_from_callsign, aprs_passcode)
        AIS.set_server(aprsis_server_name, aprsis_server_port)
        AIS.connect(blocking=True)

        # are we connected?
        if AIS._connected:
            logger.info(
                msg=f"Established connection to APRS_IS: server={aprsis_server_name},"
                f"port={aprsis_server_port}, APRS-IS User: {aprs_from_callsign}, APRS-IS passcode: {aprs_passcode}"
            )

            send_aprs_message_list(
                myaprsis=AIS,
                message_text_array=output_message,
                destination_call_sign=aprs_to_callsign,
                simulate_send=False,
                source_call_sign=aprs_from_callsign,
            )

            AIS.close()
        else:
            print("An error has occurred")
