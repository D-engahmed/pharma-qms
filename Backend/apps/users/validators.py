from django.core.exceptions import ValidationError


class ContainsDigitValidator:
    """
    09-authentication.md / 19-validation-rules.md: password must contain at
    least one number. Django's built-in NumericPasswordValidator does the
    OPPOSITE — it rejects passwords that are ENTIRELY numeric. It was
    present in AUTH_PASSWORD_VALIDATORS but never enforced "must contain a
    digit." This validator actually does that.

    Wire it into config/settings/base.py:

        AUTH_PASSWORD_VALIDATORS = [
            {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
             'OPTIONS': {'min_length': 8}},
            {'NAME': 'apps.users.validators.ContainsDigitValidator'},
            # UserAttributeSimilarityValidator / CommonPasswordValidator left
            # as your call — spec says "no unnecessary complexity" but these
            # are standard hygiene, not obviously what that line means.
        ]
    """

    def validate(self, password, user=None):
        if not any(char.isdigit() for char in password):
            raise ValidationError(
                "This password must contain at least one number.",
                code='password_no_number',
            )

    def get_help_text(self):
        return "Your password must contain at least one number."
