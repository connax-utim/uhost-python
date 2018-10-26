"""
Tag module
"""


class TagInbound(object):
    """
    Inbound data tag class
    """

    GET_UTIM_STATUS = b'\x1a'
    NETWORK_READY = b'\x1c'
    DATA_FROM_NETWORK = b'\x1d'
    DATA_TO_SIGN = b'\x1e'
    DATA_TO_PLATFORM = b'\x1f'

    def in_this_scope(self, tag):
        """
        Check tag is in this scope
        """

        try:
            tag_ord = None
            if isinstance(tag, bytes) and len(tag) == 1:
                tag_ord = ord(tag)

            if tag_ord in (ord(self.GET_UTIM_STATUS), ord(self.NETWORK_READY),
                           ord(self.DATA_FROM_NETWORK), ord(self.DATA_TO_SIGN)):
                return True

        except TypeError:
            pass

        return False

    def assemble_for_utim(self, data):
        """
        Assemble data to sls
        """

        if isinstance(data, (bytes, bytearray)):
            # Get values
            tag = self.DATA_FROM_NETWORK
            length = len(data).to_bytes(2, byteorder='big')

            # Merge values into a message and return
            return tag + length + data

        return None


class TagOutbound(object):
    """
    Outbound data tag class
    """

    OK_STATUS = b'\x2a'
    DATA_TO_NETWORK = b'\x2d'
    DATA_TO_SLS = b'\x2e'

    def in_this_scope(self, tag):
        """
        Check tag is in this scope
        """

        try:
            tag_ord = None
            if isinstance(tag, bytes) and len(tag) == 1:
                tag_ord = ord(tag)

            if tag_ord in (ord(self.OK_STATUS), ord(self.DATA_TO_NETWORK), ord(self.DATA_TO_SLS)):
                return True

        except TypeError:
            pass

        return False

    def assemble_for_network(self, data):
        """
        Assemble data to network
        """

        if isinstance(data, (bytes, bytearray)):
            # Get values
            tag = self.DATA_TO_NETWORK
            length = len(data).to_bytes(2, byteorder='big')

            # Merge values into a message and return
            return tag + length + data

        return None

    def assemble_for_sls(self, data):
        """
        Assemble data to sls
        """

        if isinstance(data, (bytes, bytearray)):
            # Get values
            tag = self.DATA_TO_SLS
            length = len(data).to_bytes(2, byteorder='big')

            # Merge values into a message and return
            return tag + length + data

        return None

    def assemble_ok_status(self):
        """
        Assemble OK status data
        """

        # Get values
        data = b''
        tag = self.OK_STATUS
        length = len(data).to_bytes(2, byteorder='big')

        # Merge values into a message and return
        return tag + length + data


class TagCrypto(object):
    """
    Tags for Crypto layer
    """

    ENCRYPTED = b'\x81'
    SIGNED = b'\x82'


class UCommand(object):
    """
    Commands for SRP authentication
    """

    # SRP authentication process
    # UTIM => UHOST
    HELLO = b'\xa1'
    CHECK = b'\xa2'
    TRUSTED = b'\xa3'
    VERIFIED = b'\xa4'
    # UTIM <= UHOST
    TRY_FIRST = b'\xb1'
    TRY_SECOND = b'\xb2'
    INIT = b'\xb3'
    AUTHENTIC = b'\xb4'

    KEEPALIVE = b'\x9e'
    KEEPALIVE_ANSWER = b'\x9f'

    SIGNED = b'\xc0'
    SIGNATURE = b'\xc1'
    CONNECTION_STRING = b'\xcc'
    CONNECTION_STRING_SUCCESS = b'\xcd'
    CONNECTION_STRING_ERROR = b'\xce'

    TEST_PLATFORM_DATA = b'\xd0'

    ERROR = b'\xee'
    DIE = b'\xff'

    def assemble_test_platform_data(self, data):
        """
        Assemble test platform data command
        """

        if isinstance(data, (bytes, bytearray)):
            # Get values
            tag = self.TEST_PLATFORM_DATA
            length = len(data).to_bytes(2, byteorder='big')

            # Merge values into a message and return
            return tag + length + data

        return None

    def assemble_connection_string_success(self):
        """
        Assemble connection string success command
        """

        # Get values
        tag = self.CONNECTION_STRING
        length = len(self.CONNECTION_STRING_SUCCESS).to_bytes(2, byteorder='big')

        # Merge values into a message and return
        return tag + length + self.CONNECTION_STRING_SUCCESS

    def assemble_connection_string_error(self):
        """
        Assemble connection string error command
        """

        # Get values
        tag = self.CONNECTION_STRING
        length = len(self.CONNECTION_STRING_ERROR).to_bytes(2, byteorder='big')

        # Merge values into a message and return
        return tag + length + self.CONNECTION_STRING_ERROR

    def assemble_hello(self, data):
        """
        Assemble hello command
        """

        if isinstance(data, (bytes, bytearray)):
            # Get values
            tag = self.HELLO
            length = len(data).to_bytes(2, byteorder='big')

            # Merge values into a message and return
            return tag + length + data

        return None

    def assemble_try(self, data1, data2):
        """
        Assemble hello command
        """

        if isinstance(data1, (bytes, bytearray)) and isinstance(data2, (bytes, bytearray)):
            # Get values
            tag1 = self.TRY_FIRST
            length1 = len(data1).to_bytes(2, byteorder='big')
            tag2 = self.TRY_SECOND
            length2 = len(data2).to_bytes(2, byteorder='big')

            # Merge values into a message and return
            return tag1 + length1 + data1 + tag2 + length2 + data2

        return None

    def assemble_check(self, data):
        """
        Assemble check command
        """

        if isinstance(data, (bytes, bytearray)):
            # Get values
            tag = self.CHECK
            length = len(data).to_bytes(2, byteorder='big')

            # Merge values into a message and return
            return tag + length + data

        return None

    def assemble_init(self, data):
        """
        Assemble init command
        """

        if isinstance(data, (bytes, bytearray)):
            # Get values
            tag = self.INIT
            length = len(data).to_bytes(2, byteorder='big')

            # Merge values into a message and return
            return tag + length + data

        return None

    def assemble_trusted(self, data):
        """
        Assemble trusted command
        """

        if isinstance(data, (bytes, bytearray)):
            # Get values
            tag = self.TRUSTED
            length = len(data).to_bytes(2, byteorder='big')

            # Merge values into a message and return
            return tag + length + data

        return None

    def assemble_signed(self, data1, data2):
        """
        Assemble signed command
        """

        if isinstance(data1, (bytes, bytearray)) and isinstance(data2, (bytes, bytearray)):
            # Get values
            tag1 = self.SIGNED
            length1 = len(data1).to_bytes(2, byteorder='big')
            tag2 = self.SIGNATURE
            length2 = len(data2).to_bytes(2, byteorder='big')

            # Merge values into a message and return
            return tag1 + length1 + data1 + tag2 + length2 + data2

        return None

    def assemble_error(self, data):
        """
        Assemble error command
        """

        if isinstance(data, (bytes, bytearray)):
            # Get values
            tag = self.ERROR
            length = len(data).to_bytes(2, byteorder='big')

            # Merge values into a message and return
            return tag + length + data

        return None

    def assemble_verified(self):
        """
        Assemble verified command
        """

        # Get values
        tag = self.VERIFIED
        length = (0).to_bytes(2, byteorder='big')

        # Merge values into a message and return
        return tag + length

    def assemble_authentic(self):
        """
        Assemble authentic command
        """

        # Get values
        tag = self.AUTHENTIC
        length = (0).to_bytes(2, byteorder='big')

        # Merge values into a message and return
        return tag + length


class Tag(object):
    """
    All tags class
    """

    INBOUND = TagInbound()
    OUTBOUND = TagOutbound()
    UCOMMAND = UCommand()
    CRYPTO = TagCrypto()
