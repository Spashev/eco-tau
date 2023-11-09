import pytest
from faker import Faker

from account import RoleType

from tests.factories.accounts import UserFactory

fake = Faker()


@pytest.fixture()
def manager(db):
    manager = UserFactory.create(role=RoleType.MANAGER, email='manager@gmail.com', phone_number='+77771234571')
    return manager


@pytest.fixture()
def client(db):
    client = UserFactory.create(role=RoleType.CLIENT, email='client@gmail.com', phone_number='+77771234572')
    return client


@pytest.fixture()
def director(db):
    director = UserFactory.create(role=RoleType.DIRECTOR, email='director@gmail.com', phone_number='+77771234573')
    return director


@pytest.fixture()
def admin(db):
    admin = UserFactory.create(role=RoleType.ADMIN, is_admin=True, email='root@gmail.com', phone_number='+77771234574')
    return admin
