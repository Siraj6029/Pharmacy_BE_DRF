from django.contrib import admin
from .models import Company, Formula, Distribution

admin.site.register((Company, Formula, Distribution))
