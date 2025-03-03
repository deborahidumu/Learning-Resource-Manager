class UserExistsError(Exception):
    """Raised when a user already exists in the database"""
    pass

class UserDoesNotExistError(Exception):
    """Raised when a user does not exist in the database"""
    pass

class DatabaseError(Exception):
    """Raised when a database error occurs"""
    pass