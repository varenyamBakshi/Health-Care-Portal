import django_filters
from .models import *


class DoctorFilter(django_filters.FilterSet):
    class Meta:
        model = Doctor
        fields = ['speciality', 'city']


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = specificproducts
        fields = ['name']


class StockFilter(django_filters.FilterSet):
    class Meta:
        model = specificproducts
        fields = ['name', 'brand']
