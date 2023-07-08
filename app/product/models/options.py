from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from PIL import Image as PILImage
from django.core.exceptions import ValidationError
import uuid

from utils.models import TimestampMixin, CharNameModel
from utils.mixins import ResizeImageMixin


class Category(CharNameModel, models.Model):
    is_active = models.BooleanField(verbose_name=_('Активный'), default=True)
    icon = models.FileField(verbose_name=_('Иконки'), upload_to='icons/categories', null=True, blank=True)

    class Meta:
        ordering = ("-pk",)
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')

    def __str__(self):
        return self.name


class Convenience(CharNameModel, models.Model):
    is_active = models.BooleanField(verbose_name=_('Активный'), default=True)
    icon = models.FileField(verbose_name=_('Иконки'), upload_to='icons/conveniences', null=True, blank=True)
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
    original = models.ImageField(verbose_name=_('Оригинальная картина'), upload_to='images/original/%Y/%m/%d')
    thumbnail = models.ImageField(verbose_name=_('Thumbnail картина'), upload_to='images/thumbnail/%Y/%m/%d', null=True)
    width = models.IntegerField(verbose_name=_('Width'), blank=True, null=True)
    height = models.IntegerField(verbose_name=_('Height'), blank=True, null=True)
    mimetype = models.CharField(max_length=300, default=None, blank=True, null=True)
    size = models.IntegerField(default=None, blank=True, null=True)
    product = models.ForeignKey('product.Product', verbose_name=_('Продукт'), related_name='images',
                                on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ("-pk",)
        verbose_name = _('Картинка продукта')
        verbose_name_plural = _('Картинки продуктов')

    def clean_original(self):
        image = self.cleaned_data.get('original', False)
        if image:
            if image.size > 4 * 1024 * 1024:
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
            width, height, mime_type = self.resize(self.thumbnail, 0.5)
            if width < 600 or height < 300:
                raise ValidationError("Image size(width,height) must be greater than 720px.")
            self.width = width
            self.height = height
            self.mimetype = mime_type
        super().save(*args, **kwargs)
