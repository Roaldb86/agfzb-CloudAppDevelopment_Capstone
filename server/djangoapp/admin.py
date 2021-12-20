from django.contrib import admin
from .models import CarMake, CarModel, CarDealer, DealerReview


# Register your models here.
class CarModelInline(admin.StackedInline):
    model = CarModel
    extra = 5

class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]

admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel)
