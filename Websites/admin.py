from django.contrib import admin
from .models import Websites,Categories,Slider,Sub_Categories,Countries
# Register your models here.
admin.site.register(Slider)
admin.site.register(Websites)
admin.site.register(Categories)
admin.site.register(Sub_Categories)
admin.site.register(Countries)
