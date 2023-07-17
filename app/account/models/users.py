import string
import secrets

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

from account import RoleType
from account.models.managers import UserManager
from account.tasks import send_password_reset_notification

from utils.logger import log_exception
from utils.models import TimestampMixin


class User(
    TimestampMixin,
    AbstractUser,
    models.Model,
):
    username = None
    email = models.EmailField(verbose_name=_('Email'), unique=True)
    first_name = models.CharField(verbose_name=_("Имя"), max_length=100)
    last_name = models.CharField(verbose_name=_("Фамилия"), max_length=100)
    middle_name = models.CharField(verbose_name=_("Отчество"), max_length=100, blank=True)
    date_of_birth = models.DateField(verbose_name=_("Дата рождения"))
    phone_number = PhoneNumberField(unique=True, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatar/', blank=True, null=True)
    iin = models.CharField(verbose_name='ИИН', max_length=12, blank=True, null=True)
    role = models.CharField(verbose_name=_("Роль"), choices=RoleType.choices, default=RoleType.CLIENT, max_length=100)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    @property
    def full_name(self):
        first_name = self.first_name if self.first_name else ''
        last_name = self.last_name if self.last_name else ''
        middle_name = self.middle_name if self.middle_name else ''
        full_name = f"{last_name} {first_name} {middle_name}".strip()
        return full_name if len(full_name) > 0 else 'Данные не заполнены!'

    def __str__(self):
        return self.full_name

    @staticmethod
    def generate_password():
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(20))
        return password

    def reset_password(self):
        password = self.generate_password()
        self.set_password(password)
        self.save()
        self.send_mail_invitation(password)
        return password

    def send_mail_invitation(self, password: str) -> None:
        try:
            send_password_reset_notification.delay(self.email, password)
        except Exception as e:
            log_exception(e, 'Error in send_mail_invitation')
