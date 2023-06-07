from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.utils.translation import gettext_lazy as _
from utils.models import TimestampMixin, CharNameModel
from product.signals import product_like, product_dislike
from product import Priority


class ActiveProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class Product(CharNameModel, TimestampMixin, models.Model):
    price_per_night = models.CharField(verbose_name=_('Цена за ночь'), max_length=255)
    price_per_week = models.CharField(verbose_name=_('Цена за неделю'), max_length=255, blank=True, null=True)
    price_per_month = models.CharField(verbose_name=_('Цена за месяц'), max_length=255, blank=True, null=True)
    owner = models.ForeignKey(verbose_name=_('Хозяин'), to='account.User', on_delete=models.CASCADE)
    rooms_qty = models.CharField(verbose_name=_('Количество комнат'), max_length=255)
    guest_qty = models.CharField(verbose_name=_('Количество гостей'), max_length=255)
    bed_qty = models.CharField(verbose_name=_('Количество кроватей'), max_length=255)
    bedroom_qty = models.CharField(verbose_name=_('Количество спален'), max_length=255)
    toilet_qty = models.CharField(verbose_name=_('Количество уборной'), max_length=255, blank=True, null=True)
    bath_qty = models.CharField(verbose_name=_('Количество ванн'), max_length=255, blank=True, null=True)
    description = models.TextField(verbose_name='Описание')
    category = models.ManyToManyField('product.Category', related_name='products')
    city = models.CharField(verbose_name='Город/Район', max_length=255)
    address = models.CharField(verbose_name='Адрес', max_length=255)
    convenience = models.ManyToManyField(to='product.Convenience', related_name='products')
    type = models.ForeignKey(to='product.Type', verbose_name=_('Тип построение'), related_name='products',
                             on_delete=models.PROTECT)
    lng = models.CharField(verbose_name='Координата Longitude', max_length=255, null=True, blank=True)
    lat = models.CharField(verbose_name='Координата Latitude', max_length=255, null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_('Активный'), default=False)
    priority = models.TextField(choices=Priority.choices, default=Priority.MEDIUM, max_length=50)
    like_count = models.PositiveIntegerField(verbose_name='Likes', default=0)
    comments = models.TextField(verbose_name='Коментарии', null=True, blank=True)

    objects = models.Manager()
    active_objects = ActiveProductManager()

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name

    def add_like(self):
        self.like_count += 1
        self.save()

    def remove_like(self):
        self.like_count -= 1
        self.save()


class Like(TimestampMixin, models.Model):
    product = models.ForeignKey(Product, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey('account.User', related_name='likes', on_delete=models.CASCADE)


class Favorites(TimestampMixin, models.Model):
    product = models.ForeignKey(Product, related_name='favorites', on_delete=models.CASCADE)
    user = models.ForeignKey('account.User', related_name='favorites', on_delete=models.CASCADE)
    like = models.ForeignKey(Like, related_name='favorites', on_delete=models.CASCADE)

    class Meta:
        ordering = ("-created_at",)


post_save.connect(product_like, sender=Like)
pre_delete.connect(product_dislike, sender=Like)
