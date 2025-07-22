import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r"^(\+31[1-9][0-9]{8}|06[1-9][0-9]{7})$",
    message="Phone number must be in the format: +31XXXXXXXXX or 06XXXXXXXX.",
)


def validate_alphanumeric(value):
    if not re.match(r"^[a-zA-Z0-9]*$", value):
        raise ValidationError(
            "ID number must be alphanumeric (letters and numbers only)."
        )


class CustomPasswordValidator:
    def validate(self, password):
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in password):
            raise ValidationError("Password must contain at least one digit.")
        if not any(char.islower() for char in password):
            raise ValidationError(
                "Password must contain at least one lowercase letter."
            )
        if not any(char.isupper() for char in password):
            raise ValidationError(
                "Password must contain at least one uppercase letter."
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                'Password must contain at least one special character (!@#$%^&*(),.?":{}|<>).'
            )

    def get_help_text(self):
        return (
            "Your password must contain at least 8 characters, "
            "including one uppercase letter, one lowercase letter, one number, and one special character."
        )
