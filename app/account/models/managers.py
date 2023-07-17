from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.core.cache import cache
from django.conf import settings

import random
import math

from account.tasks import send_created_account_notification, send_email
from utils.logger import log_exception


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = email.lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        activation_code = self.generate_activation_code()
        cache_key = f'activation_code:{user.id}'
        cache.set(cache_key, activation_code)

        self.send_activation_code(user.email, activation_code)
        # self.send_user_create_mail(user.email, password)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('account.custom_user_manager.value_error.not_staff'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('account.custom_user_manager.value_error.not_superuser'))

        return self.create_user(email, password, **extra_fields)

    def generate_activation_code(self):
        digits = [i for i in range(0, 10)]

        random_str = ""
        for i in range(6):
            index = math.floor(random.random() * 10)
            random_str += str(digits[index])
        
        return random_str

    def send_activation_code(self, email, code: str) -> None:
        try:
            send_email.delay(
                "Код активации",
                [email],
                'email/registration_code.html',
                {'text': code, 'from_email': 'info@example.com', 'domain': settings.ACTIVATE_URL},
            )
        except Exception as e:
            log_exception(e, 'Error in send_activation_code')


    def send_user_create_mail(self, email, password: str) -> None:
        try:
            send_created_account_notification.delay(settings.CURRENT_SITE, email, password)
        except Exception as e:
            log_exception(e, 'Error in send_user_create_mail')
