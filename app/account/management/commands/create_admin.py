from account.models import User
from account import RoleType
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create users'

    def handle(self, *args, **kwargs):
        User.objects.create_superuser(first_name="Admin", last_name="Admin", date_of_birth="1970-01-01",
                                      email="admin@gmail.com", role=RoleType.ADMIN, password='123')
