from django.contrib import admin
from .models import Members, MonthlyROI , Investment
# Register your models here.
admin.site.register(Members)
admin.site.register(MonthlyROI)
admin.site.register(Investment)