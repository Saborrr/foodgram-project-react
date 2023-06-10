# Generated by Django 3.2.9 on 2023-06-10 14:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20230610_1714'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Ой, время приготовления не может быть меньше 1 минуты')], verbose_name='время приготовления в минутах'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='text',
            field=models.TextField(verbose_name='текстовое описание'),
        ),
    ]
