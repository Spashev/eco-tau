from django.db import models

from product.models.products import Product


class Booking(models.Model):
    start_date = models.DateTimeField(verbose_name='Дата заезда')
    end_date = models.DateTimeField(verbose_name='Дата выезда')
    product = models.ManyToManyField(to=Product)

    class Meta:
        verbose_name = 'Бронь'
        verbose_name_plural = 'Брони'
        ordering = ('-id', )
