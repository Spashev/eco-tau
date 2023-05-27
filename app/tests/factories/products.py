import pytest
import factory
from random import randint, choice
from faker import Faker
from pytest_factoryboy import register
from datetime import datetime
from django.utils import timezone
from account.models import User
from product.models import Product

fake = Faker()


@register
class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    price_per_night: int = randint(1, 1000)
    price_per_week: int = randint(1000, 10000)
    price_per_month: int = randint(10000, 100000)
    owner: User = None
    rooms_qty: int = randint(1, 10)
    guest_qty: int = randint(5, 40)
    bed_qty: int = randint(1, 10)
    bedroom_qty: int = randint(1, 10)
    toilet_qty: int = randint(1, 10)
    bath_qty: int = randint(1, 10)
    description: str = fake.pystr()
    category: int = None
    address: str = fake.address()
    city: str = fake.city()
    convenience: list = None
    type: int = None
    lng: int = fake.longitude()
    lat: int = fake.latitude()
    is_active: bool = choice([True, False])
    priority: str = choice(['HIGH', 'MEDIUM', 'LOW'])
    like_count: int = randint(1, 10)
    comments: str = fake.pystr()
