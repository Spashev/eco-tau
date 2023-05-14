import os
import io
from PIL import Image as PILImage
import requests
from django.core.files import File
from django.core.management.base import BaseCommand
from random import randint, choice
from faker import Faker

from account.models import User
from account import RoleType
from product.models import Product, Image, Category, Type, Convenience

fake = Faker()

class Command(BaseCommand):
    help = 'Create 100 products'

    def handle(self, *args, **kwargs):
        try:
            images = [
                '/code/media/management/images/img1.jpg',
                '/code/media/management/images/img2.jpg',
                '/code/media/management/images/img3.jpg',
                '/code/media/management/images/img4.jpg',
                '/code/media/management/images/img5.jpg',
            ]
            for _ in range(5):
                User.objects.create_user(fake.email(), fake.password(6), role=RoleType.MANAGER)
                Category.objects.create(name=fake.pystr())
            for _ in range(3):
                Type.objects.create(name=fake.pystr())
                Convenience.objects.create(name=fake.pystr())
            for _ in range(100):
                data = {
                    'name': fake.pystr(),
                    'price_per_night': randint(100, 10000),
                    'price_per_week': randint(100, 10000),
                    'price_per_month': randint(100, 10000),
                    'owner_id': randint(1, 5),
                    'rooms_qty': randint(5, 20),
                    'guest_qty': randint(10, 30),
                    'bed_qty': randint(10, 30),
                    'bedroom_qty': randint(10, 30),
                    'toilet_qty': randint(10, 30),
                    'bath_qty': randint(10, 30),
                    'description': fake.paragraph(nb_sentences=3),
                    'city': fake.city(),
                    'address': fake.address(),
                    'type_id': randint(1, 3),
                    'lng': fake.longitude(),
                    'lat': fake.latitude(),
                    'is_active': True,
                    'like_count': randint(1, 5),
                }
                product = Product.objects.create(**data)
                product.category.set([i for i in range(1, randint(1, 5))])
                product.convenience.set([i for i in range(1, randint(1, 3))])

                for _ in range(5):
                    image_url = choice(images)
                    image = Image(product=product)
                    image.original.save(os.path.basename(image_url), open(image_url, 'rb'), save=False)
                    image.thumbnail.save(os.path.basename(image_url), open(image_url, 'rb'), save=False)
                    image.save()
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            return
