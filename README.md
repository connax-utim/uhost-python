# uhost-python
Universal Host for UTIM

## Installation

Use `pip` for python3:

    pip3 install uhost

## Launch

Example of Uhost launcher is in `examples` folder

Before you run launcher you need:

1. Set environment variable `UHOST_MASTER_KEY`. Value of this variable is in hex format. For example:

        UHOST_MASTER_KEY=6b6579       

1. Edit `config.ini` file (in the same folder), or create config file in the other place and set environment variable `UHOST_CONFIG`. Value of this variable is a absolute path to `config.ini`.


After running in output you should see config for Utim like that:

    ########################################################
       
    Use this configuration to start Utim:
    
    UHOST_NAME=74657374
    MASTER_KEY=6b6579
    MESSAGING_PROTOCOL=MQTT
    MESSAGING_HOSTNAME=localhost
    MESSAGING_USERNAME=test
    MESSAGING_PASSWORD=test
        
    NOTE: UHOST_NAME and MASTER_KEY are in hex format
        
    ########################################################
    
Before Utim launching you should add Utim ID to database:

1. Connect to database (from your `config.ini`)

1. Select schema which name is `uhost_{UHOST_NAME}`

1. Add Utim ID in hex format to `device_id` column of `udata` table