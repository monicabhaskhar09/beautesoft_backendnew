# Generated by Django 3.0.7 on 2021-05-05 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0024_multipricepolicy'),
    ]

    operations = [
        migrations.AddField(
            model_name='multipricepolicy',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='multipricepolicy',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
