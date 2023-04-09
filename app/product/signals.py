from django.dispatch import receiver


def product_like(sender, instance, created, **kwargs):
    if created:
        instance.product.add_like()

def product_dislike(sender, instance, **kwargs):
    if instance:
        instance.product.remove_like()
