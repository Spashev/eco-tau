import pytest
from faker import Faker

from account import RoleType

from tests.factories.accounts import UserFactory

fake = Faker()


@pytest.fixture()
def manager(db):
    manager = UserFactory.create(role=RoleType.MANAGER)
    return manager


@pytest.fixture()
def client(db):
    client = UserFactory.create(role=RoleType.CLIENT)
    return client


@pytest.fixture()
def director(db):
    director = UserFactory.objects.create(role=RoleType.DIRECTOR)
    return director


@pytest.fixture()
def admin(db):
    admin = UserFactory.create(role=RoleType.ADMIN, is_admin=True)
    return admin
