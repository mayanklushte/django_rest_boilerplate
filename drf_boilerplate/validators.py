import re
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class ComplexPasswordValidator:
    def __init__(self):
        self.regex = re.compile(r'(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9])')

    def validate(self, password, user=None):
        if not self.regex.search(password):
            raise ValidationError(
                _('This password is not strong enough.'),
                code='password_is_weak',
            )

    def get_help_text(self):
        return _('Your password must contain at least 1 uppercase letter, 1 digit, and 1 non-alphanumeric character.')
