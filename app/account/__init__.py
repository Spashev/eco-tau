from django.db.models import TextChoices


class UserAccountType(TextChoices):
    ADMIN = 'ADMIN', 'Админ'
    STAFF = 'STAFF', 'Сотрудник'
    CLIENT = 'CLIENT', 'Клиент'


class RoleType(TextChoices):
    MANAGER = 'MANAGER', 'Менеджер'
    DIRECTOR = 'DIRECTOR', 'Директор'
    CLIENT = 'CLIENT', 'Клиент'
    ADMIN = 'ADMIN', 'Админ'
