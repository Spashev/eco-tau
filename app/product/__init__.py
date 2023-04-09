from django.db.models import TextChoices


class Priority(TextChoices):
    HIGH = 'HIGHEST', 'Наивысший приоритет'
    MEDIUM = 'MEDIUM', 'Средний приоритет'
    LOW = 'LOW', 'Низкий приоритет'
