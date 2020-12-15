class ClientClosedException(Exception):
    """Raised when the server tries to close the client connection"""
    pass


class ProtocolException(Exception):
    """Unable to process data received"""
    pass
