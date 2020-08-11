import django_filters
from django_filters import CharFilter
from .models import *

class OrderFilter(django_filters.FilterSet):
	address = CharFilter(field_name='address', lookup_expr= 'icontains')
	class Meta :
		model = Order
		fields = "__all__"
		exclude = ['customer']