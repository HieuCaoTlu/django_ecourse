from django.contrib import admin
from .models import *
from django.contrib import admin
from .models import BudgetModel, PaymentInfo

class BudgetModelAdmin(admin.ModelAdmin):
    list_display = ('total_amount','profit')

    def total_amount(self, obj):
        total_amount = PaymentInfo.objects.aggregate(total=models.Sum('amount'))['total']
        return total_amount if total_amount is not None else 0
    
    def profit(self, obj):
        total_amount = PaymentInfo.objects.aggregate(total=models.Sum('amount'))['total']
        profit = total_amount * 0.05 if total_amount is not None else 0
        return profit

admin.site.register(BudgetModel, BudgetModelAdmin)

# Register your models here.
admin.site.register(PaymentInfo)