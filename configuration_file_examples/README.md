# Configuration file examples

# Table of Contents
<!--ts-->
* [Template files](#template-files)
* [Sample commands and command scripts](#sample-commands-and-command-scripts)
<!--te-->

This directory contains four files in total:

## Template files

- [`apprise.yml.TEMPLATE`](apprise.yml.TEMPLATE) - Sample [Apprise](https://www.github.com/caronc/apprise) configuration file in [Apprise's YAML format](https://github.com/caronc/apprise/wiki/config_yaml) syntax. You can use this file as foundation for your own Apprise configuration.
- [`secure_aprs_bastion_bot.cfg.TEMPLATE`](secure_aprs_bastion_bot.cfg.TEMPLATE) - Fully preconfigured configuration file for the APRS bot. Follow [the installation instructions](/docs/installation-instructions.md) for further details.

## Sample commands and command scripts

>[!NOTE]
> These two files are only provided for illustration purposes. You are neither required nor requested to use any of these two files.

- [`sabb_command_config.yml.SAMPLE`](sabb_command_config.yml.SAMPLE) - a demo file for a `--command-code` configuration. One single command `helloworld` is provided; this file expects one mandatory additional parameter via APRS messaging. Both the additional parameter and the user's call sign will then be written to an external text file. 
- [`helloworld.sh`](helloworld.sh) - this is the script that is called by the `helloworld` keyword. It simply takes two parameters and dumps them into a text file.