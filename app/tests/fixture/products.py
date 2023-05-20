import pytest
from faker import Faker

from product.models import Product, Category, Type, Convenience

fake = Faker()


@pytest.fixture()
def category_factory(db):
    category = Category.objects.create(name=fake.pystr())
    return category


@pytest.fixture()
def type_factory(db):
    type = Type.objects.create(name=fake.pystr())
    return type


@pytest.fixture()
def convenience_factory(db):
    convenience = Convenience.objects.create(name=fake.pystr())
    return convenience
