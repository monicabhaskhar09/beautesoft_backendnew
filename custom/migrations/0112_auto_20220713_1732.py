# Generated by Django 3.0.7 on 2022-07-13 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0111_quotationsign'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemcart',
            name='is_flexi',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='itemcart',
            name='is_flexinewservice',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
