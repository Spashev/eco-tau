import uuid
import random
import math
from django.db import models
from django.utils.translation import gettext_lazy as _


class UUIDMixin(models.Model):
    uuid = models.UUIDField(verbose_name=_('uuid'), default=uuid.uuid4, editable=False,)

    class Meta:
        abstract = True
        ordering = ('uuid',)


class CharNameModel(models.Model):
    name = models.CharField(verbose_name=_("Наименование"), max_length=255,)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(verbose_name=_('Дата создания'), auto_now_add=True,)
    updated_at = models.DateTimeField(verbose_name=_('Дата изменения'), auto_now=True,)

    class Meta:
        abstract = True
        ordering = ('created_at', 'updated_at')


def generate_activation_code():
    digits = [i for i in range(0, 10)]

    random_str = ""
    for i in range(6):
        index = math.floor(random.random() * 10)
        random_str += str(digits[index])

    return random_str
