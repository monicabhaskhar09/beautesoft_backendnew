# Generated by Django 3.0.7 on 2022-06-24 15:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('custom', '0104_manualinvoicemodel_currency_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quotationpayment',
            name='fk_quotation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='custom.QuotationModel'),
        ),
        migrations.CreateModel(
            name='ManualInvoicePayment',
            fields=[
                ('id', models.AutoField(db_column='id', primary_key=True, serialize=False)),
                ('payment_schedule', models.CharField(blank=True, db_column='payment_schedule', default='', max_length=255, null=True)),
                ('payment_term', models.CharField(blank=True, db_column='payment_term', default='', max_length=255, null=True)),
                ('active', models.CharField(blank=True, db_column='Active', default='active', max_length=255, null=True)),
                ('fk_manualinvoice', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='custom.ManualInvoiceModel')),
            ],
            options={
                'db_table': 'ManualInvoice_Payment',
            },
        ),
    ]
