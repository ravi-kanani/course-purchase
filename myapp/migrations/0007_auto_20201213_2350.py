# Generated by Django 3.1.1 on 2020-12-13 23:50

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_auto_20201112_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='student_image',
            field=models.ImageField(blank=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='course',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('50.0')), django.core.validators.MaxValueValidator(Decimal('500.0'))]),
        ),
    ]