# Generated by Django 4.1.4 on 2023-05-01 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0011_category_icon_product_comments_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='product',
        ),
        migrations.AddField(
            model_name='booking',
            name='product',
            field=models.ManyToManyField(to='product.product'),
        ),
    ]
