import os
import uuid

from django.core.management.base import BaseCommand
from random import randint, choice
from faker import Faker

from account.models import User
from account import RoleType
from product.models import Product, Image, Category, Type, Convenience
from utils.logger import log_exception

from io import BytesIO
import cairosvg
from django.core.files.base import ContentFile

fake = Faker()


class Command(BaseCommand):
    help = 'Create 100 products'
    images = [
        '/code/product/management/images/houses/img1.jpg',
        '/code/product/management/images/houses/img2.jpg',
        '/code/product/management/images/houses/img3.jpg',
        '/code/product/management/images/houses/img4.jpg',
        '/code/product/management/images/houses/img5.jpg',
    ]
    categories = {
        '/code/product/management/images/categories/popular.svg': 'Популярные',
        '/code/product/management/images/categories/tree.svg': 'Деревянные дома',
        '/code/product/management/images/categories/couple.svg': 'Купольные дома',
        '/code/product/management/images/categories/urta.svg': 'Юрта',
        '/code/product/management/images/categories/campe.svg': 'Кемпинг',
        '/code/product/management/images/categories/osobnyk.svg': 'Особняк',
        '/code/product/management/images/categories/zagrod.svg': 'Загородные дома',
        '/code/product/management/images/categories/cottage.svg': 'Коттедж',
        '/code/product/management/images/categories/hostel.svg': 'Гостиница',
        '/code/product/management/images/categories/swim.svg': 'Бассейн',
        '/code/product/management/images/categories/game.svg': 'Игры',
        '/code/product/management/images/categories/beatch.svg': 'Пляж',
        '/code/product/management/images/categories/sauna.svg': 'Сауна',
        '/code/product/management/images/categories/cusine.svg': 'Большие кухни',
        '/code/product/management/images/categories/peizash.svg': 'Пейзаж',
        '/code/product/management/images/categories/house_reka.svg': 'Дом у реки',
        '/code/product/management/images/categories/luxe.svg': 'Luxe',
        '/code/product/management/images/categories/golf.svg': 'Гольф',
    }
    conveniences = [
        'Wifi',
        'Ванная',
        'Шампунь',
        'Фен',
        'Кондиционер',
        'Предметы первой необходимости',
        'Постельное белье',
        'Дополнительные подушки и одеяла',
        'Плотные шторы или занавеси',
        'Место для хранения одежды',
        'Телевизор',
        'Камин',
        'Огнетушитель',
        'Аптечка',
        'Кухня',
        'Всё необходимое для приготовления еды',
        'Посуда и столовые приборы',
        'Электроплита',
        'Кофеварка',
        'Кофе',
        'Обеденный стол',
        'Дворик (патио) или балкон с частным доступом',
        'Костровище',
        'Уличная мебель',
        'Зона барбекю',
        'Бесплатная парковка на территории',
        'Бассейн: Частный доступ',
        'Можно курить',
        'Хозяин встретит вас лично',
        'Стиральная машина',
        'Датчик дыма',
        'Отопление',
        'Датчик угарного газа',
        'Камеры видеонаблюдения в жилье',
    ]
    types = [
        'Панельные дома',
        'Блочные дома',
        'Монолитные дома',
        'Каменные дома',
        'Бетонные дома',
        'Металлические дома',
        'Соломенные дома',
        'Глинобитные дома',
        'Шале',
        'Фахверк',
        'Дома из бамбука',
        'Дома из стекла',
        'Мобильные дома'
    ]

    def handle(self, *args, **kwargs):
        try:
            print('Starting create products...')

            for icon_path, category_name in self.categories.items():
                User.objects.create_user(fake.email(), fake.password(6), role=RoleType.MANAGER,
                                         last_name=fake.last_name(), first_name=fake.first_name(),
                                         middle_name=fake.word(), date_of_birth="1970-01-01")

                print(f'Create category {category_name}')

                png_data = cairosvg.svg2png(url=icon_path)
                png_io = BytesIO(png_data)

                random_name = f'{uuid.uuid4()}.jpeg'
                cate = Category.objects.create(name=category_name)
                cate.icon.save(random_name, ContentFile(png_io.getvalue()), save=True)

            for convenience in self.conveniences:
                Convenience.objects.create(name=convenience)

            for h_type in self.types:
                Type.objects.create(name=h_type)

            for _ in range(100):
                data = {
                    'name': fake.text(max_nb_chars=5),
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
                    'type_id': randint(1, len(self.types)),
                    'lng': fake.longitude(),
                    'lat': fake.latitude(),
                    'is_active': True,
                    'like_count': randint(1, 5)
                }
                product = Product.objects.create(**data)
                product.category.set([i for i in range(1, len(self.categories) + 1)])
                product.convenience.set([i for i in range(1, len(self.conveniences) + 1)])

                print(f'Product {_} created')

                for _ in range(5):
                    image_url = choice(self.images)
                    image = Image(product=product)
                    image.original.save(os.path.basename(image_url), open(image_url, 'rb'), save=False)
                    image.thumbnail.save(os.path.basename(image_url), open(image_url, 'rb'), save=False)
                    image.save()

        except Exception as e:
            log_exception(e)
            return
