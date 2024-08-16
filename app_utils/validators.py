from typing import NamedTuple

from email_validator import EmailSyntaxError, validate_email


class InvalidEmail(NamedTuple):
    email: str


class ValidEmail(NamedTuple):
    email: str


def validate_single_email(email: str) -> ValidEmail | InvalidEmail:
    try:
        valid = validate_email(email)
        return ValidEmail(valid.email)
    except EmailSyntaxError as _:
        return InvalidEmail(email)
