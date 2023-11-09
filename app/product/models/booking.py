from django.db import models

from product.models.products import Product


class Booking(models.Model):
    start_date = models.DateField(verbose_name='Дата заезда')
    end_date = models.DateField(verbose_name='Дата выезда')
    product = models.ForeignKey(to=Product, related_name='booking', on_delete=models.CASCADE, default=1)

    class Meta:
        verbose_name = 'Бронь'
        verbose_name_plural = 'Брони'
        ordering = ('-id', )
