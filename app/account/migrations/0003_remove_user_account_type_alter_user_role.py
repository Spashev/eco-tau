# Generated by Django 4.1.4 on 2023-04-20 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_alter_user_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='account_type',
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('MANAGER', 'Менеджер'), ('DIRECTOR', 'Директор'), ('CLIENT', 'Клиент')], default='CLIENT', max_length=100, verbose_name='Роль'),
        ),
    ]