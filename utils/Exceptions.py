class NoTokenError(Exception):
    """
    Exception raised when no token is provided.
    """
    pass

class InvalidTokenFormatError(Exception):
    """
    Exception raised when the token format is invalid.
    For example, if the token is a string instead of a dictionary.
    (token is string when the oauth state is stored)
    """
    pass

class InvalidTokenError(Exception):
    """
    Exception raised when the token is invalid.
    For example, if the access token is not able to be used.
    Can be caused by bugs or someone messing with the database. (or when the token is revoked)
    """
    pass



class FakeStateError(Exception):
    """
    Exception raised when the state is not a valid state.
    Usually happens when the user makes a fake state and makes a request on website.
    """
    pass

