"""
Length module
"""


class LengthInbound(object):
    """
    Inbound data length class
    """

    GET_UTIM_STATUS = 0
    NETWORK_READY = 12


class LengthOutbound(object):
    """
    Outbound data length class
    """

    OK_STATUS = 0


class UCommand(object):
    """
    Commands for SRP authentication
    """

    # SRP authentication process

    SIGNATURE = 20


class Length(object):
    """
    All length class
    """

    INBOUND = LengthInbound()
    OUTBOUND = LengthOutbound()
    UCOMMAND = UCommand()
