import pytest
from rest_framework.test import APIClient

from tests.factories.products import ProductFactory


class BaseTestCase:
    api_client = None
    director = None
    admin = None
    manager = None
    buyer = None
    client = None
    type_factory = None
    convenience_factory = None
    category_factory = None
    permission_error = 'У вас недостаточно прав для выполнения данного действия.'

    @pytest.fixture(autouse=True)
    def class_setup(
            self,
            client,
            manager,
            admin,
            director,
            type_factory,
            convenience_factory,
            category_factory
    ):
        self.api_client = APIClient()
        self.client = client
        self.manager = manager
        self.admin = admin
        self.director = director
        self.category_factory = category_factory
        self.type_factory = type_factory
        self.convenience_factory = convenience_factory

    def create_orders_approve(self, count: int = 1):
        for _ in range(count):
            self.__create_product(is_active=True)

    def __create_product(self, is_active: bool = False):
        return ProductFactory.create(
            owner=self.client,
            category=self.category_factory,
            type=self.type_factory,
            is_active=is_active
        )
