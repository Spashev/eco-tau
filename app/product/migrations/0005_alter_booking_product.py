# Generated by Django 4.1.4 on 2023-10-03 08:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_like_count_alter_like_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='booking', to='product.product'),
        ),
    ]
