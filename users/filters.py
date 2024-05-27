import django_filters
from users.models import *

        
class CustomUserFilter(django_filters.FilterSet):
    username =django_filters.CharFilter(field_name="username",lookup_expr="icontains")
    contact_number =django_filters.CharFilter(field_name="contact_number",lookup_expr="icontains")
    email =django_filters.CharFilter(field_name="email",lookup_expr="icontains")

    class Meta:
        model = CustomUser
        fields = ("id","username","contact_number","email")