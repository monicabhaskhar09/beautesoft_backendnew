from django.db import models

# Create your models here.
class Reportmaster(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    code = models.CharField(db_column='Code', max_length=255, null=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=255)  # Field name made lowercase.
    description = models.TextField(db_column='Description', null=True)  # Field name made lowercase.
    pageid = models.CharField(db_column='PageID', max_length=255, null=True)  # Field name made lowercase.
    url = models.CharField(db_column='URL', max_length=255, null=True)  # Field name made lowercase.
    image = models.ImageField(db_column='Image', max_length=255,upload_to='img')  # Field name made lowercase.
    seq = models.IntegerField(db_column='Seq')  # Field name made lowercase.
    inactive = models.CharField(db_column='InActive', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'ReportMaster'
        unique_together = [['name']]
