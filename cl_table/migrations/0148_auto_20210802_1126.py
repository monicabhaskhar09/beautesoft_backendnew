# Generated by Django 3.0.7 on 2021-08-02 11:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0147_merge_20210802_1111'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='Item_Codeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Stock'),
        ),
        migrations.AddField(
            model_name='securities',
            name='role_code',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='workschedule',
            name='is_alternative',
            field=models.BooleanField(db_column='is_alter', default=False),
        ),
        migrations.AlterField(
            model_name='treatment_master',
            name='checktype',
            field=models.CharField(blank=True, choices=[('service', 'service'), ('package', 'package'), ('freetext', 'freetext')], db_column='CheckType', max_length=50, null=True),
        ),
    ]
