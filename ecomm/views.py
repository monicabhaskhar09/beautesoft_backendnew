from django.shortcuts import render
from cl_table.authentication import ExpiringTokenAuthentication
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from cl_app.permissions import authenticated_only
from .serializers import ()
from .models import ()
# from cl_table.models import (Fmspw,Employee,ControlNo,Customer,PosHaud,PosDaud)
from rest_framework import status,viewsets,mixins
from rest_framework.response import Response
from custom.views import response, get_client_ip, round_calc
from cl_app.utils import general_error_response
from django.db import transaction, connection
from datetime import timedelta
import datetime
from datetime import date, timedelta
# from cl_app.models import ItemSitelist
from django.db.models import Q
from rest_framework.decorators import action
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator, InvalidPage
from Cl_beautesoft.settings import SMS_ACCOUNT_SID, SMS_AUTH_TOKEN, SMS_SENDER, SITE_ROOT


# Create your views here.
