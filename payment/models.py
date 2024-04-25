from django.utils import timezone
from django.db import models
from base.models import Enrollment
# Create your models here.
class PaymentInfo(models.Model):
    enrollment = models.OneToOneField(Enrollment,on_delete=models.SET_NULL,null=True)
    amount = models.IntegerField(default=0)
    code = models.CharField(max_length=50, default='')
    bank = models.CharField(max_length=50)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.enrollment} {self.amount}"
    
    class Meta:
        verbose_name = 'Thanh toán'
        verbose_name_plural = 'Thanh toán'

class BudgetModel(models.Model):
    pass

    class Meta:
        verbose_name = 'Ngân sách'
        verbose_name_plural = 'Ngân sách'