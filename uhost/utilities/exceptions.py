"""Utim exceptions module"""


class UtimException(Exception):
    """
    Utim Base Exception
    """
    pass


class UtimConnectionException(UtimException):
    """
    Connection Exception class

    The exception is raised when:
     * AMQP configuration has wrong parameters (config.py)
    """
    pass


class UtimExchangeException(UtimException):
    """
    Exchange Exception class

    The exception is raised when:
     * destination in send function is not string or zero length string
    """
    pass


class UtimUnknownException(UtimException):
    """
    Unknown Exception class

    The exception is raised when raised any Exception except
    * pika.exceptions.ConnectionClosed
    * pika.exceptions.ProbableAuthenticationError
    * pika.exceptions.ChannelClosed
    """
    pass


class UtimInitializationError(UtimException):
    """
    Utim Initialization Error

    The exception is raised when:
    * Utim was started without master key
    """


class UtimDeadException(UtimException):
    """
    Utim Dead Exception

    The exception is raised when:
     * Uhost told Utim to die
    """
    pass


class UtimUncallableCallbackError(UtimException):
    """
    Utim uncallable callback error

    The exception is raised when:
     * Uncallable object was given to method as callback
    """
    pass
