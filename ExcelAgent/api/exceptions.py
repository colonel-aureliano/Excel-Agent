class MyAppError(Exception):
    """Base class for all exceptions in this project."""
    pass

class ActionStrParseError(MyAppError):
    pass

class GeminiApiError(MyAppError):
    pass
