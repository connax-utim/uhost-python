"""
Constants module
"""


class Status(object):
    """
    Utim status class
    """

    STATUS_NEWBORN = 'STATUS_NEWBORN'
    STATUS_SRP = 'STATUS_SRP'
    STATUS_CONFIGURING = 'STATUS_CONFIGURING'
    STATUS_TESTING = 'STATUS_TESTING'
    STATUS_DONE = 'STATUS_DONE'
    STATUS_NO_CONFIG = 'STATUS_NO_CONFIG'
    STATUS_DED = 'STATUS_DED'


class Flags(object):
    """
    Utim flags object
    """

    FLAG_NONE = 0
    FLAG_RECONFIGURE = 1
