from utils.logger import log_exception
from django.db.models import F


def product_like(sender, instance, created, **kwargs):
    try:
        if created:
            instance.product.like_count = F('like_count') + 1
            instance.product.save()
            instance.favorites.create(user=instance.user, product=instance.product)
    except Exception as e:
        log_exception(e, f'Product like error {str(e)}')


def product_dislike(sender, instance, **kwargs):
    try:
        if instance:
            instance.product.like_count = F('like_count') - 1
            instance.product.save()
            instance.favorites.filter(user=instance.user, product=instance.product).delete()
    except Exception as e:
        log_exception(e, f'Remove like error {str(e)}')
