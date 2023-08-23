import factory
from faker import Faker
from pytest_factoryboy import register

from account.models import User
from account import RoleType

fake = Faker()


@register
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = fake.unique.email()
    password: str = fake.password(length=6)
    first_name: str = fake.unique.first_name()
    last_name: str = fake.unique.last_name()
    middle_name = fake.unique.last_name()
    date_of_birth = fake.date_of_birth()
    phone_number = "87777777777"
    is_staff = True
    is_active = True
    is_admin = False
    role: str = RoleType.CLIENT
    iin: int = None
