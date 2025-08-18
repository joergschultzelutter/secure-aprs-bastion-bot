# `secure-aprs-bastion-bot.py`

`secure-aprs-bastion-bot.py` is based on [`core-aprs-client`](https://github.com/joergschultzelutter/core-aprs-client). All generic parts of the configuration file, such as the configuration of beacons and bulletins, are described in detail in the accompanying [configuration file documentation](https://github.com/joergschultzelutter/core-aprs-client/blob/master/docs/configuration.md). Only the parameters specific to this program (custom configuration) are described here.

The configuration file created by [`configure.py`](configure.md) is the basis for the programs to be executed by `secure-aprs-bastion-bot.py`. The name of this configuration file is defined and stored in the `custom` section of `secure-aprs-bastion-bot.py`. Details can be found at [this link](https://github.com/joergschultzelutter/core-aprs-client/blob/master/docs/configuration_subsections/config_custom.md). Changes to this external configuration file are detected by `secure-aprs-bastion-bot.py` and result in the configuration parameters being re-read; it is therefore not necessary to restart `secure-aprs-bastion-bot.py` when the configuration file is changed.

In the configuration file of the `secure-aprs-bastion-bot`, the name of the program configuration from `configure.py` must be stored in the `custom_config` section. By default, this is set to `sabb_config.yaml` and should only be changed if necessary.

```
[custom_config]
#
# This section is deliberately kept empty and can be used for storing your
# individual APRS bot's configuration settings
sabb_config_file=sabb_config.yaml
```
