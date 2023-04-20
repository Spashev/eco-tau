from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.db import models

from account.tasks import send_created_account_notification
from django.conf import settings
from utils.logger import log_exception


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = email.lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        self.send_user_create_mail(user.email, password)
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

    def send_user_create_mail(self, email, password: str) -> None:
        try:
            send_created_account_notification.delay(settings.CURRENT_SITE, email, password)
        except Exception as e:
            log_exception(e, 'Error in send_user_create_mail')
