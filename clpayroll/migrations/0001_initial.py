# Generated by Django 3.0.7 on 2022-02-15 08:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cl_table', '0199_delete_employeesalary'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee_Salary',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('emp_name', models.CharField(blank=True, db_column='Emp_name', max_length=60, null=True)),
                ('site_code', models.CharField(blank=True, db_column='Site_Code', max_length=100, null=True)),
                ('basicsalary', models.FloatField(blank=True, db_column='basicsalary', null=True)),
                ('salarystatus', models.CharField(blank=True, choices=[('New', 'New'), ('Open', 'Open'), ('Posted', 'Posted')], default='New', max_length=50, null=True)),
                ('salarymonth', models.CharField(blank=True, db_column='salarly_month', max_length=100, null=True)),
                ('from_date', models.DateField(auto_now_add=True, null=True)),
                ('to_date', models.DateField(auto_now_add=True, null=True)),
                ('checkbox', models.BooleanField(db_column='checkbox', default=False)),
                ('is_active', models.CharField(blank=True, choices=[('Active', 'Active'), ('In Active', 'In Active'), ('All', 'All')], max_length=50, null=True)),
                ('empid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cl_table.Employee')),
            ],
            options={
                'db_table': 'Employee_Salary',
            },
        ),
    ]
