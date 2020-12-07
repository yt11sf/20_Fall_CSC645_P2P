class ClientClosedException(Exception):
    """Raised when the server tries to close the client connection"""
    pass


class ServerResponseException(Exception):
    """Unable to process server response"""
    pass
