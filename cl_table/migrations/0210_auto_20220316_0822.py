# Generated by Django 3.0.7 on 2022-03-16 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0209_redeempolicy_itemdiv_ids'),
    ]

    operations = [
        migrations.AddField(
            model_name='redeempolicy',
            name='brand_ids',
            field=models.ManyToManyField(blank=True, to='cl_table.ItemBrand'),
        ),
        migrations.AddField(
            model_name='redeempolicy',
            name='dept_ids',
            field=models.ManyToManyField(blank=True, to='cl_table.ItemDept'),
        ),
    ]
