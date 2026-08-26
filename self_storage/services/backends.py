import re

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import Q

User = get_user_model()


def normalize_phone(raw_phone: str) -> str:
    if not raw_phone:
        return ""
    has_plus = str(raw_phone).strip().startswith("+")
    digits = re.sub(r"\D", "", str(raw_phone))
    if len(digits) < 10 or len(digits) > 15:
        raise ValidationError(
            "Номер телефона должен содержать от 10 до 15 цифр."
        )
    if len(digits) == 11 and digits.startswith("8"):
        return f"+7{digits[1:]}"
    if len(digits) == 10:
        return f"+7{digits}"

    return f"+{digits}" if has_plus or not digits.startswith("+") else digits


class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD) or kwargs.get("email")
        if not username or not password:
            return None
        try:
            phone_variant = normalize_phone(username)
        except ValidationError:
            phone_variant = None

        query = Q(username__iexact=username) | Q(email__iexact=username)
        if phone_variant:
            query |= Q(phone=phone_variant) | Q(phone=username)

        try:
            user = User.objects.get(query)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
