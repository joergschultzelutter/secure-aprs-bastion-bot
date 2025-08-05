#!/opt/local/bin/python
import logging
import aprslib
import argparse
from unidecode import unidecode
import re
import time

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(module)s -%(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

aprsis_filter = ""
aprsis_server_name = "euro.aprs2.net"
aprsis_server_port = 14580

# Default value: 67. May change in case of activated pagination
APRS_MSG_LEN = 67

def get_command_line_params():
    """
    Gets and returns the command line arguments

    Parameters
    ==========

    Returns
    =======
    configfile: 'str'
        name of the configuration file
    """

    # Yes, quick and dirty this time - and I couldn't care less
    global APRS_MSG_LEN
    
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--from-callsign",
        dest="aprs_from_callsign",
        type=str,
        help="APRS FROM callsign (sender)",
    )

    parser.add_argument(
        "--passcode",
        dest="aprs_passcode",
        type=str,
        help="APRS passcode",
    )

    parser.add_argument(
        "--to-callsign",
        dest="aprs_to_callsign",
        type=str,
        help="APRS TO callsign (receipient)",
    )

    parser.add_argument(
        "--message",
        dest="aprs_message",
        type=str,
        help="APRS message",
    )

    parser.add_argument(
        "--numeric-message-pagination",
        dest="aprs_message_pagination",
        action="store_true",
        default=False,
        help="Add message number to outgoing APRS message(s)",
    )

    args = parser.parse_args()

    aprs_from_callsign = args.aprs_from_callsign.upper()
    aprs_to_callsign = args.aprs_to_callsign.upper()
    aprs_passcode = args.aprs_passcode
    aprs_message = args.aprs_message
    aprs_message_pagination = args.aprs_message_pagination

    # change our global variable in case of active numeric pagination
    APRS_MSG_LEN = 59 if aprs_message_pagination else 67

    if len(aprs_from_callsign) > 0:
        # Check whether we have a call sign with or without SSID
        regex_string = r"\b^([A-Z0-9]{1,3}[0-9][A-Z0-9]{0,3})(-[A-Z0-9]{1,2})?$\b"
        matches = re.search(pattern=regex_string, string=aprs_from_callsign)
        if not matches:
            raise argparse.ArgumentTypeError(
                "Call sign must match a valid call sign format"
            )
    else:
        raise argparse.ArgumentTypeError("No FROM call sign provided")

    if len(aprs_to_callsign) > 0:
        # Check whether we have a call sign with or without SSID
        regex_string = r"\b^([A-Z0-9]{1,3}[0-9][A-Z0-9]{0,3})(-[A-Z0-9]{1,2})?$\b"
        matches = re.search(pattern=regex_string, string=aprs_to_callsign)
        if not matches:
            raise argparse.ArgumentTypeError(
                "Call sign must match a valid call sign format"
            )
    else:
        raise argparse.ArgumentTypeError("No FROM call sign provided")

    if len(aprs_passcode) != 5:
        raise argparse.ArgumentTypeError("APRS passcode must be 5 characters long")
    else:
        if not aprs_passcode.isdigit():
            raise argparse.ArgumentTypeError("APRS passcode must be a 5 digit string")

    return aprs_from_callsign, aprs_passcode, aprs_message, aprs_message_pagination, aprs_to_callsign


def make_pretty_aprs_messages(
    message_to_add: str,
    destination_list: list = None,
    max_len: int = APRS_MSG_LEN,
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
    message_to_add: 'str'
        message string that is to be added to the list in a pretty way
        If string is longer than 67 chars, we will truncate the information
    destination_list: 'list'
        List with string elements which will be enriched with the
        'mesage_to_add' string. Default: empty list aka user wants new list
    max_len: 'int':
        Max length of the list's string len.
        The length is dependent on whether the user has activated trailing
        message number information in the outgoing message or not.
        When activated, the message length is 59 - otherwise, it is 67.
    separator_char: 'str'
        Separator that is going to be used for dividing the single
        elements that the user is going to add
    add_sep: 'bool'
        True = we will add the separator when more than one item
               is in our string. This is the default
        False = do not add the separator (e.g. if we add the
                very first line of text, then we don't want a
                comma straight after the location
    force_outgoing_unicode_messages: 'bool'
        False = all outgoing UTF-8 content will be down-converted
                to ASCII content
        True = all outgoing UTF-8 content will sent out 'as is'

    Returns
    =======
    destination_list: 'list'
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
    # Details: see APRS specification pg. 71
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


def split_string_to_string_list(
    message_string: str, max_len: int = APRS_MSG_LEN
):
    """
    Force-split the string into chunks of max_len size and return a list of
    strings. This function is going to be called if the string that the user
    wants to insert exceeds more than e.g. 67 characters. In this unlikely
    case, we may not be able to add the string in a pretty format - but
    we will split it up for the user and ensure that none of the data is lost

    Parameters
    ==========
    message_string: 'str'
        message string that is to be divided into 1..n strings of 'max_len"
        text length
    max_len: 'int':
        Default: 67; set to 59 in case of pagination

    Returns
    =======
    split_strings: 'list'
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
    message_string: 'str'
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
    myaprsis: aprslib.inet.IS,
    message_text_array: list,
    destination_call_sign: str,
    simulate_send: bool = True,
    alias: str = "COAC",
    packet_delay: float = 10.0,
    tocall: str = "APRS",
):
    """
    Send a pre-prepared message list to to APRS_IS
    All packages have a max len of 67 characters
    If 'simulate_send'= True, we still prepare the message but only send it to our log file
    Parameters
    ==========
    myaprsis: 'aprslib.inet.IS'
        Our aprslib object that we will use for the communication part
    message_text_array: 'list'
        Contains 1..n entries of the content that we want to send to the user
    destination_call_sign: 'str'
        Target user call sign that is going to receive the message (usually, this
        is the user's call sign who has sent us the initial message)
    simulate_send: 'bool'
        If True: Prepare string but only send it to logger
    alias: 'str'
        Our APRS alias (COAC)
    packet_delay: 'float'
        Delay after sending out our APRS acknowledgment request
    tocall: 'str'
        This bot uses the default TOCALL ("APRS")

    Returns
    =======
    """
    for single_message in message_text_array:
        stringtosend = f"{alias}>{tocall}::{destination_call_sign:9}:{single_message}"
        if not simulate_send:
            logger.debug(msg=f"Sending response message '{stringtosend}'")
            myaprsis.sendall(stringtosend)
        else:
            logger.debug(msg=f"Simulating response message '{stringtosend}'")
        time.sleep(packet_delay)








if __name__ == "__main__":

    aprsis_callsign, aprsis_passcode, aprsis_message = get_command_line_params()

    AIS = aprslib.IS(aprsis_callsign, aprsis_passcode)
    AIS.set_server(aprsis_server_name, aprsis_server_port)
    #AIS.set_filter(aprsis_filter)

    AIS.connect(blocking=True)
    if AIS._connected == True:
        logger.info(
            msg=f"Established connection to APRS_IS: server={aprsis_server_name},"
            f"port={aprsis_server_port},filter={aprsis_filter}"
            f"APRS-IS User: {aprsis_callsign}, APRS-IS passcode: {aprsis_passcode}"
        )
        AIS.sendall(aprsis_message)
        AIS.close()
    else:
        print("An error has occurred")
