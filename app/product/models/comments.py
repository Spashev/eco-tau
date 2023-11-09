from django.db import models
from django.utils import timezone

from utils.models import TimestampMixin
from product.models.products import Product


class Comment(
    TimestampMixin,
    models.Model
):
    product = models.ForeignKey(Product, related_name='product_comments', on_delete=models.CASCADE)
    parent = models.ForeignKey("self", blank=True, null=True, related_name="parent_comments", on_delete=models.CASCADE)
    user = models.ForeignKey('account.User', related_name="user_comments", on_delete=models.CASCADE)
    reply = models.ForeignKey('self', blank=True, related_name="replies", null=True, on_delete=models.CASCADE)
    content = models.TextField(max_length=350)
    date_posted = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.content[:50]

    class Meta:
        ordering = ['-id']
