# Generated by Django 3.0.7 on 2022-05-24 10:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0233_auto_20220509_1006'),
    ]

    operations = [
        migrations.AddField(
            model_name='tmptreatment',
            name='newservice_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Stock'),
        ),
        migrations.AddField(
            model_name='tmptreatment',
            name='treatment_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Treatment'),
        ),
    ]