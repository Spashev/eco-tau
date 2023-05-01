from django.db import models
from django.utils.translation import gettext_lazy as _
from imagekit.processors import ResizeToFill
from django.utils.safestring import mark_safe
from PIL import Image as PILImage
import uuid

from utils.models import TimestampMixin, CharNameModel
from utils.mixins import ResizeImageMixin


class Category(CharNameModel, models.Model):
    is_active = models.BooleanField(verbose_name=_('Активный'), default=True)
    parent = models.ForeignKey('Category', related_name='categories', on_delete=models.PROTECT, null=True, blank=True)
    icon = models.CharField(verbose_name=_('Иконки'), max_length=255, null=True, blank=True)

    class Meta:
        ordering = ("-pk",)
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')

    def __str__(self):
        return self.name


class Convenience(CharNameModel, models.Model):
    is_active = models.BooleanField(verbose_name=_('Активный'), default=True)
    icon = models.CharField(verbose_name=_('Иконки'), max_length=255, null=True, blank=True)
    parent = models.ForeignKey('Convenience', related_name='conveniences', on_delete=models.PROTECT, null=True,
                               blank=True)

    class Meta:
        ordering = ("-pk",)
        verbose_name = _('Условия')
        verbose_name_plural = _('Условии')

    def __str__(self):
        return self.name


class Type(CharNameModel, TimestampMixin, models.Model):
    class Meta:
        ordering = ("-created_at",)
        verbose_name = _('Тип построении домов')
        verbose_name_plural = _('Тип построении домов')

    def __str__(self):
        return self.name


class Image(models.Model, ResizeImageMixin):
    original = models.ImageField(verbose_name=_('Оригинальная картина'), upload_to='images/original')
    thumbnail = models.ImageField(verbose_name=_('Thumbnail картина'), upload_to='images/thumbnail', null=True)
    product = models.ForeignKey('product.Product', verbose_name=_('Продукт'), related_name='images',
                                on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        ordering = ("-pk",)
        verbose_name = _('Картинка продукта')
        verbose_name_plural = _('Картинки продуктов')

    def clean_original(self):
        image = self.cleaned_data.get('original', False)
        if image:
            if image._size > 4 * 1024 * 1024:
                raise ValidationError("Image file too large ( > 4mb )")

            return image
        else:
            raise ValidationError("Couldn't read uploaded image")

    def image_tag(self):
        if self.original.url is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(self.original.url))
        else:
            return ""

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.resize(self.thumbnail, (324, 300))

        super().save(*args, **kwargs)
