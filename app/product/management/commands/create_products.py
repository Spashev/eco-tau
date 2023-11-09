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
PRODUCT_COUNT = 1000


class Command(BaseCommand):
    help = f'Create {PRODUCT_COUNT} products'
    images = [
        '/code/product/management/images/houses/img1.jpg',
        '/code/product/management/images/houses/img2.jpg',
        '/code/product/management/images/houses/img3.jpg',
        '/code/product/management/images/houses/img4.jpg',
        '/code/product/management/images/houses/img5.jpg',
        '/code/product/management/images/houses/img6.webp',
        '/code/product/management/images/houses/img7.webp',
        '/code/product/management/images/houses/img8.webp',
    ]
    categories = {
        '/code/product/management/images/categories/башни.svg': 'Башни',
        '/code/product/management/images/categories/большие кухни.svg': 'Большие кухни',
        '/code/product/management/images/categories/вау.svg': 'Вау',
        '/code/product/management/images/categories/вершины мира.svg': 'Вершины мира',
        '/code/product/management/images/categories/виноградники.svg': 'Виноградники',
        '/code/product/management/images/categories/гольф.svg': 'Гольф',
        '/code/product/management/images/categories/популярные.svg': 'Популярные',
        '/code/product/management/images/categories/города мечты.svg': 'Города мечты',
        '/code/product/management/images/categories/гостиницы.svg': 'Гостиница',
        '/code/product/management/images/categories/дер дома.svg': 'Деревянные дома',
        '/code/product/management/images/categories/дома шалаши.svg': 'Дома шалаши',
        '/code/product/management/images/categories/загородные дома.svg': 'Загородные дома',
        '/code/product/management/images/categories/у озера.svg': 'Дом у озера',
        '/code/product/management/images/categories/купольный дом.svg': 'Купольные дома',
        '/code/product/management/images/categories/микродома.svg': 'Микродома',
        '/code/product/management/images/categories/новинки.svg': 'Новинки',
        '/code/product/management/images/categories/лыжня.svg': 'Рядом с лыжней базы',
        '/code/product/management/images/categories/юрта.svg': 'Юрта',
        '/code/product/management/images/categories/отд комнаты.svg': 'Отдельные комнаты',
        '/code/product/management/images/categories/кемпинг.svg': 'Кемпинг',
        '/code/product/management/images/categories/особняки.svg': 'Особняк',
        '/code/product/management/images/categories/коттедж.svg': 'Коттедж',
        '/code/product/management/images/categories/отличные виды.svg': 'Отличный вид',
        '/code/product/management/images/categories/отопление.svg': 'Отопление',
        '/code/product/management/images/categories/игры.svg': 'Игры',
        '/code/product/management/images/categories/пейзаж.svg': 'Пейзаж',
        '/code/product/management/images/categories/пещеры.svg': 'Пещеры',
        '/code/product/management/images/categories/рядом пляж.svg': 'Рядом пляж',
        '/code/product/management/images/categories/рабочая зона.svg': 'Рабочая зона',
        '/code/product/management/images/categories/намазхана.svg': 'Намазхана',
        '/code/product/management/images/categories/сауна.svg': 'Сауна',
        '/code/product/management/images/categories/супербассейны.svg': 'Супербассейны',
        '/code/product/management/images/categories/люкс.svg': 'Luxe',
    }
    conveniences = {
        '/code/product/management/images/convenience/wifi.svg': 'Wifi',
        '/code/product/management/images/convenience/vanna.svg': 'Ванная',
        '/code/product/management/images/convenience/shampon.svg': 'Шампунь',
        '/code/product/management/images/convenience/fen.svg': 'Фен',
        '/code/product/management/images/convenience/kondor.svg': 'Кондиционер',
        '/code/product/management/images/convenience/pred_perv_neb.svg': 'Предметы первой необходимости',
        '/code/product/management/images/convenience/post_bel.svg': 'Постельное белье',
        '/code/product/management/images/convenience/podushka.svg': 'Дополнительные подушки и одеяла',
        '/code/product/management/images/convenience/grderob.svg': 'Место для хранения одежды',
        '/code/product/management/images/convenience/tv.svg': 'Телевизор',
        '/code/product/management/images/convenience/kamin.svg': 'Камин',
        '/code/product/management/images/convenience/ognetush.svg': 'Огнетушитель',
        '/code/product/management/images/convenience/aptechka.svg': 'Аптечка',
        '/code/product/management/images/convenience/kuh.svg': 'Кухня',
        '/code/product/management/images/convenience/posuda.svg': 'Посуда и столовые приборы',
        '/code/product/management/images/convenience/elektro_plita.svg': 'Электроплита',
        '/code/product/management/images/convenience/koffe_varka.svg': 'Кофеварка',
        '/code/product/management/images/convenience/obed_stol.svg': 'Обеденный стол',
        '/code/product/management/images/convenience/dvorik_balkon.svg': 'Дворик (патио) или балкон с частным доступом',
        '/code/product/management/images/convenience/krovat.svg': 'Kроватка',
        '/code/product/management/images/convenience/ulich_meb.svg': 'Уличная мебель',
        '/code/product/management/images/convenience/bbk.svg': 'Зона барбекю',
        '/code/product/management/images/convenience/parkovka.svg': 'Бесплатная парковка на территории',
        '/code/product/management/images/convenience/bassein.svg': 'Бассейн: Частный доступ',
        '/code/product/management/images/convenience/hos_vstre.svg': 'Хозяин встретит вас лично',
        '/code/product/management/images/convenience/stir_mach.svg': 'Стиральная машина',
        '/code/product/management/images/convenience/datchik_dim.svg': 'Датчик дыма',
        '/code/product/management/images/convenience/datch_ugar_dim.svg': 'Датчик угарного газа',
        '/code/product/management/images/convenience/camera.svg': 'Камеры видеонаблюдения в жилье',
        '/code/product/management/images/convenience/utug.svg': 'Утюг',
        '/code/product/management/images/convenience/gidro_mass.svg': 'Гидромассажная ванна',
        '/code/product/management/images/convenience/gor_voda.svg': 'Горячая вода',
        '/code/product/management/images/convenience/gas_petch.svg': 'Газавая печка',
        '/code/product/management/images/convenience/dush_ul.svg': 'Душ на улице',
        '/code/product/management/images/convenience/zad_dvor.svg': 'Задний двор',
        '/code/product/management/images/convenience/mikrovol.svg': 'Микроволновка',
        '/code/product/management/images/convenience/otdel_vhod.svg': 'Отдельный вход',
        '/code/product/management/images/convenience/lezhaki.svg': 'Лежаки',
        '/code/product/management/images/convenience/plech.svg': 'Плечики',
        '/code/product/management/images/convenience/posuda_moi_mach.svg': 'Посудомоечная машина',
        '/code/product/management/images/convenience/protiv.svg': 'Вкусно поесть',
        '/code/product/management/images/convenience/work_area.svg': 'Рабочая зона',
        '/code/product/management/images/convenience/stol_korm.svg': 'Стульчик для кормления',
        '/code/product/management/images/convenience/sushul_odezh.svg': 'Сушилка для одежды',
        '/code/product/management/images/convenience/toster.svg': 'Тостер',
        '/code/product/management/images/convenience/holod.svg': 'Холодильник',
        '/code/product/management/images/convenience/center_otop.svg': 'Центр отопление',
        '/code/product/management/images/convenience/chainik.svg': 'Чайник',
    }
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

            for icon_path, convenience_name in self.conveniences.items():
                conv = Convenience.objects.create(name=convenience_name)
                random_name = f'{uuid.uuid4()}.jpeg'
                png_data = cairosvg.svg2png(url=icon_path)
                png_io = BytesIO(png_data)
                conv.icon.save(random_name, ContentFile(png_io.getvalue()), save=True)

                print(f'Create conveniences {convenience_name}')

            for h_type in self.types:
                Type.objects.create(name=h_type)

            for _ in range(PRODUCT_COUNT):
                data = {
                    'name': fake.name(),
                    'price_per_night': randint(100, 1000),
                    'price_per_week': randint(1000, 10000),
                    'price_per_month': randint(1000, 50000),
                    'owner_id': randint(1, 15),
                    'rooms_qty': randint(1, 12),
                    'guest_qty': randint(1, 30),
                    'bed_qty': randint(1, 10),
                    'bedroom_qty': randint(1, 10),
                    'toilet_qty': randint(1, 10),
                    'bath_qty': randint(1, 10),
                    'description': fake.paragraph(nb_sentences=3),
                    'city': fake.city(),
                    'address': fake.address(),
                    'type_id': randint(1, len(self.types)),
                    'lng': fake.longitude(),
                    'lat': fake.latitude(),
                    'is_active': True,
                    'like_count': randint(1, 50),
                    'rating': randint(1, 3)
                }
                product = Product.objects.create(**data)
                product.category.set([i for i in range(1, len(self.categories) + 1)])
                product.convenience.set([i for i in range(1, len(self.conveniences) + 1)])

                print(f'Product {_} created')

                for _ in range(8):
                    image_url = choice(self.images)
                    image = Image(product=product)
                    image.original.save(os.path.basename(image_url), open(image_url, 'rb'), save=False)
                    image.thumbnail.save(os.path.basename(image_url), open(image_url, 'rb'), save=False)
                    image.save()

        except Exception as e:
            log_exception(e)
            return
