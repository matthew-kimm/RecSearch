"""
Allows for adding custom checks.
fdict = {'custom_check_name': custom_check_function, ...}
"""
from validate import Validator, VdtValueTooLongError, VdtValueError


# Define custom check functions here
def valid_name(name: str):
    """Check if valid python identifier and not > 255 chars after adding prefixes."""
    if len(name) > 246:
        raise VdtValueTooLongError(name)
    if not name.isidentifier():
        raise VdtValueError(name)
    return name


# Add custom check functions to fdict
fdict = {'valid_name': valid_name}

default_validator = Validator(fdict)
