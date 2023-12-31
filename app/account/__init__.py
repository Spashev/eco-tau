from django.db.models import TextChoices


class RoleType(TextChoices):
    MANAGER = 'MANAGER', 'Менеджер'
    DIRECTOR = 'DIRECTOR', 'Директор'
    CLIENT = 'CLIENT', 'Клиент'
    ADMIN = 'ADMIN', 'Админ'


class RoleClientManagerType(TextChoices):
    CLIENT = 'CLIENT', 'Клиент'
    MANAGER = 'MANAGER', 'Менеджер'
