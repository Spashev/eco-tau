from utils.logger import log_exception


def product_like(sender, instance, created, **kwargs):
    try:
        if created:
            instance.product.add_like()
    except Exception as e:
        log_exception(e, f'Product like error {str(e)}')


def product_dislike(sender, instance, **kwargs):
    try:
        if instance:
            instance.product.remove_like()
    except Exception as e:
        log_exception(e, f'Remove like error {str(e)}')
