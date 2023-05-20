from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


def product_like(sender, instance, created, **kwargs):
    try:
        if created:
            instance.product.add_like()
    except Exception as e:
        logger.error(f'Product like error {str(e)}')

def product_dislike(sender, instance, **kwargs):
    try:
        if instance:
            instance.product.remove_like()
    except Exception as e:
        logger.error(f'Remove like error {str(e)}')
