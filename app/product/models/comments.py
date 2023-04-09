from django.db import models

from utils.models import TimestampMixin
from product.models.product import Product

class Comment(
    TimestampMixin,
    models.Model
):
    product = models.ForeignKey(Product, related_name='comments', on_delete=models.CASCADE, null=True)
    parent = models.ForeignKey("self", blank=True, null=True, related_name="comment_parent", on_delete=models.CASCADE)
    user = models.ForeignKey('account.User', blank=True, null=True, on_delete=models.CASCADE)
    reply = models.ForeignKey('self', blank=True, null=True)
    content = models.TextField(max_length=350, blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.content
