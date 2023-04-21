# Generated by Django 4.1.4 on 2023-04-20 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_alter_image_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='extension',
            field=models.CharField(blank=True, default=None, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='mimetype',
            field=models.CharField(blank=True, default=None, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='size',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]