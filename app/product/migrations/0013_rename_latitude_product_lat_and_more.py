# Generated by Django 4.1.4 on 2023-05-01 18:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0012_remove_booking_product_booking_product'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='latitude',
            new_name='lat',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='longitude',
            new_name='lng',
        ),
    ]
