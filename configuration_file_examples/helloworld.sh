#!/bin/bash

# This is the counterpart of the "helloworld" command from the provided
# sample configuration file. It simply takes the two parameters and
# dumps them to an external text file.

# REMINDER: you are REQUIRED to provide a shebang at the beginning of
# the file (e.g. #!/bin/bash) or the execution of the script WILL fail!
# Details: https://github.com/joergschultzelutter/secure-aprs-bastion-bot?tab=readme-ov-file#faq

# Output the parameters provided by the user's APRS message to a local file
echo "$1 $2" >~/aprs_parameters.txt
