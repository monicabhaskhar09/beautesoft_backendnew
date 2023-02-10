from operator import mod
from xml.dom.minidom import Document
from django.db import models, transaction
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User, Group
from django.db.models import F
from django.utils import timezone
# from cl_app.models import ItemSitelist


# Create your models here.
