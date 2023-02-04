# Generated by Django 3.0.7 on 2023-01-23 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0331_customer_site_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='class_name',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='cust_img',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='estimated_deliverydate',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='is_pregnant',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='last_visit',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='no_of_children',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='no_of_weeks_pregnant',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='or_key',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='upcoming_appointments',
        ),
        migrations.AddField(
            model_name='customerextended',
            name='class_name',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='customerextended',
            name='cust_img',
            field=models.ImageField(blank=True, null=True, upload_to='img'),
        ),
        migrations.AddField(
            model_name='customerextended',
            name='estimated_deliverydate',
            field=models.DateTimeField(blank=True, db_column='EstimatedDeliveryDate', null=True),
        ),
        migrations.AddField(
            model_name='customerextended',
            name='is_pregnant',
            field=models.BooleanField(blank=True, db_column='IsPregnant', null=True),
        ),
        migrations.AddField(
            model_name='customerextended',
            name='last_visit',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='customerextended',
            name='no_of_children',
            field=models.IntegerField(blank=True, db_column='NoOfChildren', null=True),
        ),
        migrations.AddField(
            model_name='customerextended',
            name='no_of_weeks_pregnant',
            field=models.IntegerField(blank=True, db_column='NoOfWeeksOfPregnancy', null=True),
        ),
        migrations.AddField(
            model_name='customerextended',
            name='or_key',
            field=models.CharField(blank=True, db_column='OR_KEY', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='customerextended',
            name='upcoming_appointments',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
